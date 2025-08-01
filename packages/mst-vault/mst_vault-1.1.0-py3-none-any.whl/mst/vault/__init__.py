import os
from typing import Optional
from pathlib import Path
import hvac
from mst.core import LogAPIUsage


class MSTVault:
    """Allows retrieving secrets from the vault server.

    Requires a token in either '/vault/secrets/token' or '/run/secrets/kubernetes.io/serviceaccount/token' to initialize, prioritizing the former.

    Raises RuntimeError if neither token is found.
    """

    def __init__(self):
        self.vault_addr = os.getenv("VAULT_ADDR", "https://vault.mst.edu")
        self.app_user = os.getenv("APP_USER")

        t = Path("/vault/secrets/token")
        f = Path("/run/secrets/kubernetes.io/serviceaccount/token")

        if t.is_file():
            token = t.read_text(encoding="utf8").strip()
            client = hvac.Client(url=self.vault_addr, token=token)
            try:
                if client.is_authenticated():
                    self.client = client
            except Exception as err:
                raise RuntimeError("vault client could not authenticate")
        elif f.is_file() and self.app_user:
            k8s_jwt = f.read_text(encoding="utf8")
            client = hvac.Client(url=self.vault_addr)

            mounts = []
            if os.getenv("VAULT_K8S_MOUNT"):
                mounts.append("VAULT_K8S_MOUNT")
            else:
                if not os.getenv("LOCAL_ENV") or "dev" in os.getenv("LOCAL_ENV"):
                    mounts.append("rke-apps-d")
                if not os.getenv("LOCAL_ENV") or "test" in os.getenv("LOCAL_ENV"):
                    mounts.append("rke-apps-t")
                if not os.getenv("LOCAL_ENV") or "prod" in os.getenv("LOCAL_ENV"):
                    mounts.append("rke-apps-p")

                for mount in mounts:
                    res = client.auth.jwt.jwt_login(role=f"app-{self.app_user}", jwt=k8s_jwt, path=mount)
                    if res and res["auth"]["client_token"]:
                        client = hvac.Client(url=self.vault_addr, token=res["auth"]["client_token"])
                        try:
                            if client.is_authenticated():
                                self.client = client
                                break
                        except Exception as err:
                            raise RuntimeError("vault client could not authenticate")

        else:
            raise RuntimeError("Vault Client not configured or is missing!")

    def read_secret(self, path: str) -> Optional[str]:
        """Reads a secret value from the given path

        Args:
            path (str): the path on vault to the secret

        Returns:
            Optional[str]: The value of the secret or none if it does not exist
        """
        LogAPIUsage()
        secrets = self.client.secrets.kv.v1.read_secret(mount_point="secret", path=f"data/{path}")
        return secrets["data"]["data"]
