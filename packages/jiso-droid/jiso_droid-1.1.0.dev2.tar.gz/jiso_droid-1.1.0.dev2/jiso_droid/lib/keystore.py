import subprocess
from pathlib import Path
from .config import Config

class Generate(Config):

    def __init__(self):
        super().__init__()

    def create(self):
        cert = self.certificate()

        dn_str = (
            f"CN={cert.dname.CN}, OU={cert.dname.OU}, O={cert.dname.O}, "
            f"L={cert.dname.L}, ST={cert.dname.ST}, C={cert.dname.C}"
        )

        cmd = [
            "keytool", "-genkeypair", "-v",
            "-keystore", str(cert.keystore_file),
            "-alias", str(cert.alias),
            "-keyalg", str(cert.keyalg),
            "-keysize", str(cert.keysize),
            "-validity", str(cert.validity_days),
            "-storepass", str(cert.store_pass),
            "-keypass", str(cert.key_pass),
            "-dname", dn_str
        ]

        subprocess.run(cmd, check=True, capture_output=True, text=True)

        return Path(cert.keystore_file).exists()