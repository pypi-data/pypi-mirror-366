import os
import sys
import socket
import requests
import boto3
from huggingface_hub import snapshot_download
from tqdm import tqdm
from base64 import b64encode
from botocore.exceptions import ClientError, EndpointConnectionError
from typing import List
from dotenv import load_dotenv
load_dotenv()  

from .CephS3Manager import CephS3Manager
from .HealthChecker import HealthChecker

# ProjectsAPI manages ClearML project operations
class ProjectsAPI:
    def __init__(self, post):
        self._post = post

    def create(self, name, description=""):
        return self._post("/projects.create", {"name": name, "description": description})

    def get_all(self):
        return self._post("/projects.get_all")['projects']

# ModelsAPI manages ClearML model operations
class ModelsAPI:
    def __init__(self, post):
        self._post = post

    def create(self, name, project_id, metadata=None, uri=""):
        payload = {
            "name": name,
            "project": project_id,
            "uri": uri
        }

        if isinstance(metadata, dict):
            payload["metadata"] = metadata

        return self._post("/models.create", payload)

    def get_all(self, project_id=None):
        payload = {"project": project_id} if project_id else {}
        # print("$$$$$$$$$$$$$$$$$$ model get all payload", payload)
        response = self._post("/models.get_all", payload)
        # print("[DEBUG] Full response from /models.get_all:", response)

        # Check expected key in proper format
        if isinstance(response, dict):
            if "models" in response and isinstance(response["models"], list):
                return response["models"]
            elif "data" in response and isinstance(response["data"], dict) and "models" in response["data"]:
                return response["data"]["models"]

        print(f"[ERROR] 'models' not found in response: {response}")
        return []

    def get_by_id(self, model_id):
        return self._post("/models.get_by_id", {"model": model_id})

    def update(self, model_id, uri=None, metadata=None):
        payload = {"model": model_id}
        if uri:
            payload["uri"] = uri
        if isinstance(metadata, dict) or isinstance(metadata, list): 
            payload["metadata"] = metadata

        # print(f"[DEBUG] Metadata Payload: {metadata}")
        # print(f"[DEBUG] Full Payload to /models.update: {payload}")

        return self._post("/models.add_or_update_metadata", payload)

    def delete(self, model_id):
        return self._post("/models.delete", {"model": model_id})
    
    def edit_uri(self, model_id, uri):
        payload = {"model": model_id, "uri": uri}
        # print(f"[DEBUG] Payload to /models.edit: {payload}")
        return self._post("/models.edit", payload)


# MLOpsManager integrates ClearML and Ceph S3 operations
class MLOpsManager:
    def __init__(self, clearml_url, clearml_access_key, clearml_secret_key, clearml_username):
        self.clearml_url = clearml_url
        self.clearml_access_key = clearml_access_key
        self.clearml_secret_key = clearml_secret_key
        self.clearml_username = clearml_username

        self.ceph_endpoint = os.environ["CEPH_ENDPOINT"]
        self.ceph_access_key = os.environ["CEPH_ACCESS_KEY"]
        self.ceph_secret_key = os.environ["CEPH_SECRET_KEY"]
        self.ceph_bucket = os.environ["CEPH_BUCKET"]

        # Health checks for S3 and ClearML services
        ceph_mgr = CephS3Manager(self.ceph_endpoint, self.ceph_access_key, self.ceph_secret_key, self.ceph_bucket)
        ceph_mgr.ensure_bucket_exists()
        if not ceph_mgr.check_connection():
            sys.exit(1)
        if not ceph_mgr.check_auth():
            sys.exit(1)
        if not HealthChecker.check_clearml_service(self.clearml_url):
            sys.exit(1)
        if not HealthChecker.check_clearml_auth(self.clearml_url, self.clearml_access_key, self.clearml_secret_key):
            sys.exit(1)

        self.ceph = ceph_mgr

        # Login to ClearML and extract token
        creds = f"{self.clearml_access_key}:{self.clearml_secret_key}"
        auth_header = b64encode(creds.encode("utf-8")).decode("utf-8")
        res = requests.post(
            f"{self.clearml_url}/auth.login",
            headers={"Authorization": f"Basic {auth_header}"}
        )
        self.token = res.json()['data']['token']

        # Debug output for Bearer token
        # print(f"[DEBUG] Bearer Token: {self.token}")

        self.projects = ProjectsAPI(self._post)
        self.models = ModelsAPI(self._post)

        # Get or create user-specific project
        projects = self.projects.get_all()
        self.project_name = f"project_{self.clearml_username}"
        exists = [p for p in projects if p['name'] == self.project_name]
        self.project_id = exists[0]['id'] if exists else self.projects.create(self.project_name)['id']


    def _post(self, path, params=None):
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            res = requests.post(f"{self.clearml_url}{path}", headers=headers, json=params)
            res.raise_for_status()  

            data = res.json()
            # print(f"[DEBUG] Response for {path}: {data}")

            if 'data' not in data:
                print(f"[ERROR] No 'data' key in response: {data}")
                return {}

            return data['data']

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request to {path} failed: {e}")
            print(f"[ERROR] Status Code: {res.status_code}, Response: {res.text}")
            return {}

        except ValueError as e:
            print(f"[ERROR] Failed to parse JSON from {path}: {e}")
            print(f"[ERROR] Raw response: {res.text}")
            return {}



    def get_model_id_by_name(self, name):
        # print(f"[DEBUG] Using project ID: {self.project_id}")
        models = self.models.get_all(self.project_id)
        for m in models:
            if m['name'] == name:
                return m['id']
        return None

    def get_model_name_by_id(self, model_id):
        model = self.models.get_by_id(model_id)
        return model.get("name") if model else None

    def add_model(self, source_type, model_name=None, code_path=None, source_path=None, 
                  hf_source=None, clearml_url=None, access_key=None, secret_key=None,
                  bucket_name=None):
        if self.get_model_id_by_name(model_name):
            print(f"[WARN] Model with name '{model_name}' already exists.")
            print("[INFO] Listing existing models:")
            self.list_models(verbose=True)
            return None

        model_folder_name = os.path.basename(source_path.rstrip("/\\"))
        have_model_py = False  
        
        model = self.models.create(
            name=model_name,
            project_id=self.project_id,
            uri="s3://dummy/uri"  
        
        )
        # print("[DEBUG] Model Create Response:", model)

        if not model or 'id' not in model:
            print("[ERROR] Model creation failed.")
            return None

        model_id = model['id']
        dest_prefix = f"models/{model_id}/"

        try:
            if source_type == "local":
                self.ceph.upload(source_path, dest_prefix)
            elif source_type == "hf":
                local_path = snapshot_download(repo_id=hf_source)
                self.ceph.upload(local_path, dest_prefix)
            elif source_type == "s3":
                src_ceph = CephS3Manager(clearml_url,
                                        access_key,
                                        secret_key,
                                        bucket_name)
                tmp = f"./tmp_{model_name}"
                src_ceph.download(source_path, tmp,
                                keep_folder=True,
                                exclude=[".git", ".DS_Store"],
                                overwrite=True)
                self.ceph.upload(tmp, dest_prefix)
            else:
                raise ValueError("Unknown source_type")

            if code_path and os.path.isfile(code_path):
                self.ceph.upload(code_path, dest_prefix + "model.py")
                have_model_py = True

            # update with metadata list
            metadata_list = [
                {"key": "modelFolderName", "type": "str", "value": model_folder_name},
                {"key": "haveModelPy", "type": "str", "value": str(have_model_py).lower()},
                {"key": "modelSize", "type": "float", "value": "0.0"}

            ]
            
            uri = f"s3://{self.ceph_bucket}/{dest_prefix}"
            self.models.edit_uri(model_id, uri=uri)
            self.models.update(model_id, metadata=metadata_list)
            
                    # After setting the correct URI, calculate actual model size and update metadata
            try:
                model_size_mb = self.ceph.get_uri_size(uri)
                size_metadata = [
                    {"key": "modelSize", "type": "float", "value": str(round(model_size_mb, 2))}
                ]
                self.models.update(model_id, metadata=size_metadata)
            except Exception as e:
                print(f"[WARN] Failed to calculate or update model size: {e}")


            print(f"[AddModel] {model_id} {model_name}")
            return model_id



        except Exception as e:
            print(f"[ERROR] Upload failed: {e}")
            print("[INFO] Cleaning up partially uploaded model...")
            self.models.delete(model_id)
            self.ceph.delete_folder(dest_prefix)
            return None


    def get_model(self, model_name, local_dest):
        model_id = self.get_model_id_by_name(model_name)
        if not model_id:
            print("[FAIL] Model not found")
            return
        model_data = self.models.get_by_id(model_id)
        model = model_data.get("model") or model_data
        uri = model['uri']
        _, remote_path = uri.replace("s3://", "").split("/", 1)
        self.ceph.download(remote_path, local_dest,
                           keep_folder=True,
                           exclude=[".git", ".DS_Store"],
                           overwrite=False)
        print("[Info] Downloaded:", model)
        return model
    
    def get_model_info(self, identifier):
        """
        Fetch model info using either model_name or model_id.
        If `identifier` matches an existing ID, it will use it directly.
        Otherwise, it will treat it as a name and search accordingly.
        """
        all_models = self.models.get_all(self.project_id)

        def extract_model_info(model):
            print("=" * 40)
            print(f"ID: {model.get('id')}")
            print(f"Name: {model.get('name')}")
            print(f"Created: {model.get('created')}")
            print(f"Framework: {model.get('framework')}")
            print(f"URI: {model.get('uri')}")

            # Extract and show metadata (including modelSize)
            metadata = model.get('metadata', {})
            print("Metadata:")
            for key, value in metadata.items():
                print(f"  - {key}: {value}")

            # Highlight modelSize if available
            model_size = metadata.get("modelSize")
            if model_size is not None:
                try:
                    print(f"\n[Model Size] {float(model_size):.2f} MB")
                except (ValueError, TypeError):
                    print(f"\n[Model Size] Invalid value: {model_size}")

            print(f"Labels: {model.get('labels')}")
            print("=" * 40)

        # Try match by ID
        matched_by_id = [m for m in all_models if m.get("id") == identifier]
        if matched_by_id:
            extract_model_info(matched_by_id[0])
            return matched_by_id[0]

        # Try match by name
        matched_by_name = [m for m in all_models if m.get("name") == identifier]
        if matched_by_name:
            for model in matched_by_name:
                extract_model_info(model)
            return matched_by_name

        print(f"[INFO] No model found with identifier: '{identifier}'")
        return None




    def list_models(self, verbose=True):
        models = self.models.get_all(self.project_id)
        if verbose:
            grouped = {}
            for m in models:
                grouped.setdefault(m["name"], []).append(m["id"])
            for name, ids in grouped.items():
                print(f"[Model] Name: {name}, Count: {len(ids)}")
        return [(m['name'], m['id']) for m in models]

    def delete_model(self, model_id=None, model_name=None):
        if model_name:
            model_id = self.get_model_id_by_name(model_name)
            if not model_id:
                print(f"[WARN] No model found with name '{model_name}'")
                return

        model_data = self.models.get_by_id(model_id)
        if not model_data:
            print(f"[WARN] Model with ID '{model_id}' not found.")
            return

        model = model_data.get("model") or model_data
        uri = model.get("uri")
        if not uri:
            print(f"[WARN] Model '{model_id}' has no 'uri'.")
            return

        _, remote_path = uri.replace("s3://", "").split("/", 1)
        self.ceph.delete_folder(remote_path)
        self.models.delete(model_id)
        print(f"[Deleted] {model_id}")


if __name__ == "__main__":
    manager = MLOpsManager(
        clearml_url=os.environ["CLEARML_URL"],
        clearml_access_key=os.environ["CLEARML_ACCESS_KEY"],
        clearml_secret_key=os.environ["CLEARML_SECRET_KEY"],
        clearml_username=os.environ["CLEARML_USERNAME"]
    )

    # Optional: Delete model by name if it exists
    manager.delete_model(model_name="local_model")

    print("\n[Model List] BEFORE ADD")
    models = manager.list_models(verbose=False)
    for name, mid in models:
        print(f"Model Name: {name}, Model ID: {mid}")

    # Add local model with optional code_path (model.py)
    local_model_id = manager.add_model(
        source_type="local",
        source_path=r"D:\university\Master-Terms\DML\Projects\MLOPS\Test\Qwen2.5-14B-Instruct - test",
        model_name="local_model",
        code_path=r"D:\university\Master-Terms\DML\Projects\MLOPS\Test\Qwen2.5-14B-Instruct - test\model.py"
    )
    
    print("\n[Model List] AFTER ADD")
    models = manager.list_models(verbose=False)
    for name, mid in models:
        print(f"Model Name: {name}, Model ID: {mid}")

    print(f"\n[INFO] Fetching model info for: 'local_model'")
    model_info = manager.get_model_info("local_model")

    # Test: Get URI size of the model just added
    test_model_name = "local_model"

    print(f"\n[TEST] Get size of URI for model '{test_model_name}'")

    # Step 1: Get model ID
    model_id = manager.get_model_id_by_name(test_model_name)
    if not model_id:
        print(f"[ERROR] Model '{test_model_name}' not found.")
    else:
        # Step 2: Get full model info (including URI)
        model_data = manager.models.get_by_id(model_id)
        model = model_data.get("model") or model_data
        model_uri = model.get("uri")

        if model_uri:
            # Step 3: Use CephS3Manager to get size of this URI
            size = manager.ceph.get_uri_size(model_uri)
            print(f"[RESULT] Size of model at URI '{model_uri}': {size:.2f} MB")
        else:
            print(f"[ERROR] No URI found in model metadata.")

    # Optional: Delete model if you want to clean up after
    # manager.delete_model(model_name="local_model")


