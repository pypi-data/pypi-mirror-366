from dataclasses import dataclass

@dataclass
class DNName:
    CN: str
    OU: str
    O: str
    L: str
    ST: str
    C: str

@dataclass
class CertificateData:
    alias: str
    keystore_file: str
    store_pass: str
    key_pass: str
    dname: DNName
    keyalg: str
    keysize: str
    validity_days: str