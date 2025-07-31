#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
from lib.keystore import Generate
from lib.signer import SignApk

keystore = Generate()
data = keystore.certificate()

menu = """
\t┏┳┳┏┓┏┓  ┳┓    • ┓
\t ┃┃┗┓┃┃━━┃┃┏┓┏┓┓┏┫
\t┗┛┻┗┛┗┛  ┻┛┛ ┗┛┗┗┻
"""

def _get_input(prompt: str, default: str = "") -> str:
    response = input(f"[-] {prompt} => ").strip()
    return response if response else default

def generate_keystore():
    inputs = {
        'alias': ("Alias", data.alias),
        'keystore_file': ("Keystore Name", data.keystore_file),
        'store_pass': ("Store Password", data.store_pass),
        'key_pass': ("Key Password", data.key_pass),
        'keyalg': ("Key Algorithm", data.keyalg),
        'keysize': ("Key Size", data.keysize),
        'validity_days': ("Validity Days", data.validity_days),
        'dname': {
            'CN': ("Common Name", data.dname.CN),
            'OU': ("Organizational Unit", data.dname.OU),
            'O': ("Organization", data.dname.O),
            'ST': ("State/Province", data.dname.ST),
            'C': ("Country Code", data.dname.C),
        },
    }
    data.alias = _get_input(*inputs['alias'])
    keystore_file = _get_input(*inputs['keystore_file'])
    data.keystore_file = keystore_file if keystore_file.endswith('.jks') else f"{keystore_file}.jks"
    data.store_pass = _get_input(*inputs['store_pass'])
    data.key_pass = _get_input(*inputs['key_pass']) or data.store_pass

    for field, (prompt, default) in inputs['dname'].items():
        setattr(data.dname, field, _get_input(prompt, default))

    data.keyalg = _get_input(*inputs['keyalg'])
    data.keysize = _get_input(*inputs['keysize'])
    data.validity_days = _get_input(*inputs['validity_days'])

    keystore.update_config(data)

    if (keystore.create()):
        print("[INFO] Successfully created keystore!")
    else:
        print("[ERROR] Failed to create keystore!")


def sign_apk():
    pass

def main():

    parser = argparse.ArgumentParser(
        description=f"""{menu}
        JISO-DROID - Keystore Generator & APK Signing Tool
        
        This tool helps you:
        1. Generate new keystores for APK signing
        2. Sign APK files with existing keystores
        3. Supports comprehensive configuration including:
           - Custom distinguished names (DN)
           - Multiple cryptographic algorithms (RSA/EC)
           - Flexible validity periods
           - V1/V2/V3/V4 signature schemes
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""Contoh penggunaan:
        {sys.argv[0]} generatekey
        {sys.argv[0]} sign app.apk file.jks
        """
    )

    subparsers = parser.add_subparsers(
        dest='command',
        required=True
    )
    subparsers.add_parser(
    'generatekey',
        help='Create a new keystore'
    )
    signparser = subparsers.add_parser(
    'sign',
        help='Sign APK'
    )
    signparser.add_argument('-k','--keystore', help='Keystore file path')
    signparser.add_argument('-s', '--schema', help='Schema (V1,V2,V3,V4)')
    signparser.add_argument('input',help='APK file path')

    args = parser.parse_args()

    if args.command == 'generatekey':
        generate_keystore()


if __name__ == '__main__':
    main()