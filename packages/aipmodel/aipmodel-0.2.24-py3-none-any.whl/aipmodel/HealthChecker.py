import socket
import requests
from base64 import b64encode

# HealthChecker includes static methods to verify system and service availability
class HealthChecker:
    @staticmethod
    def check_internet():
        """
        Check internet connectivity by attempting to reach a known DNS server (Google).
        """
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            print("[OK] Internet")
            return True
        except OSError:
            print("[FAIL] Internet")
            return False

    @staticmethod
    def check_clearml_service(url):
        """
        Check if ClearML service is reachable and responding.
        """
        try:
            r = requests.get(url + "/auth.login", timeout=5)
            if r.status_code in [200, 401]:
                print("[OK] ClearML Service")
                return True
            print(f"[FAIL] ClearML Service {r.status_code}")
            return False
        except Exception:
            print("[FAIL] ClearML Service")
            return False

    @staticmethod
    def check_clearml_auth(url, access_key, secret_key):
        """
        Check if ClearML credentials are valid by attempting login.
        """
        try:
            creds = f"{access_key}:{secret_key}"
            auth_header = b64encode(creds.encode("utf-8")).decode("utf-8")
            r = requests.post(
                url + "/auth.login",
                headers={"Authorization": f"Basic {auth_header}"},
                timeout=5
            )
            if r.status_code == 200:
                print("[OK] ClearML Auth")
                return True
            print(f"[FAIL] ClearML Auth {r.status_code}")
            return False
        except Exception:
            print("[FAIL] ClearML Auth")
            return False
