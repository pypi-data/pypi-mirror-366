import json
from pathlib import Path
from typing import Dict, Any
from .models import CertificateData, DNName

class Config:

    DEFAULT_CONFIG = {
        "certificates": {
            "alias": "android",
            "keystore_file": "my_signature.jks",
            "store_pass": "password1234",
            "key_pass": "password1234",
            "dname": {
                "CN": "example.com",
                "OU": "IT Department",
                "O": "Example Inc",
                "L": "Jakarta",
                "ST": "DKI Jakarta",
                "C": "ID"
            },
            "keyalg": "RSA",
            "keysize": "2048",
            "validity_days": "365"
        }
    }

    def __init__(self, config_path : str = '../config.json'):
        self._config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not self._config_path.exists():
            self._save_config(self.DEFAULT_CONFIG)

        with open(self._config_path, 'r') as f:
            config = json.load(f)
            return {**self.DEFAULT_CONFIG, **config}

    def _save_config(self, config: Dict[str, Any]):
        with open(self._config_path, 'w') as f:
            json.dump(config, f)

    def certificate(self) -> CertificateData:
        certificates = self._config.get("certificates")
        return CertificateData(
            alias=certificates.get("alias"),
            keystore_file=certificates.get("keystore_file"),
            store_pass=certificates.get("store_pass"),
            key_pass=certificates.get("key_pass"),
            dname=DNName(**certificates.get("dname")),
            keyalg=certificates.get("keyalg"),
            keysize=certificates.get("keysize"),
            validity_days=certificates.get("validity_days"),
        )

    def update_config(self, certificate: CertificateData):
        self._config["certificates"] = {
            "alias": certificate.alias,
            "keystore_file": certificate.keystore_file,
            "store_pass": certificate.store_pass,
            "key_pass": certificate.key_pass,
            "dname": {
                "CN": certificate.dname.CN,
                "OU": certificate.dname.OU,
                "O": certificate.dname.O,
                "L": certificate.dname.L,
                "ST": certificate.dname.ST,
                "C": certificate.dname.C
            },
            "keyalg": certificate.keyalg,
            "keysize": certificate.keysize,
            "validity_days": certificate.validity_days,
        }
