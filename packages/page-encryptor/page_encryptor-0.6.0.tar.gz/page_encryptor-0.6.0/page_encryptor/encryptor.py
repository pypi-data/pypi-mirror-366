#!/usr/bin/env python3

import argparse
from base64 import b64encode
from pathlib import Path

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2

PAYLOAD_TAG = '/*__PAYLOAD__*/ ""'


def encrypt_html(input_file, template_file, password):
    try:
        data = input_file.read_bytes()
    except Exception as err:
        raise RuntimeError("Error reading input file") from err

    salt = Random.get_random_bytes(32)
    iv = Random.get_random_bytes(16)
    key = PBKDF2(password.encode(), salt, dkLen=32, count=100000, hmac_hash_module=SHA256)

    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    encrypted_data, tag = cipher.encrypt_and_digest(data)

    try:
        template = template_file.read_text(encoding="utf-8")
    except Exception as err:
        raise RuntimeError("Error reading template file") from err

    if PAYLOAD_TAG not in template:
        raise RuntimeError(f"Template must contain the placeholder {PAYLOAD_TAG}")

    encoded_payload = b64encode(salt + iv + encrypted_data + tag).decode("utf-8")
    return template.replace(PAYLOAD_TAG, f'"{encoded_payload}"')


def main():
    parser = argparse.ArgumentParser(
        description="Encrypt a static HTML file with AES and embed it into a decryptable template."
        "\n\n"
        f"The template must contain the string {PAYLOAD_TAG} which will be replaced with the encrypted data.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        required=True,
        help="Path to the HTML file to encrypt.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        required=True,
        help="Path to the output encrypted HTML file.",
    )
    parser.add_argument("--password", "-p", required=True, help="Password used for encryption.")
    parser.add_argument(
        "--template",
        "-t",
        type=Path,
        default=Path(__file__).parent / "templates" / "decryptor_template.html",
        help="Path to the decrypt HTML template file. Defaults to the built-in template.",
    )

    args = parser.parse_args()

    try:
        encrypted_html = encrypt_html(args.input, args.template, args.password)
        args.output.write_text(encrypted_html, encoding="utf-8-sig")
        print(f"Encrypted file saved to {args.output}")
    except Exception as err:
        raise RuntimeError("Error writing output file") from err


if __name__ == "__main__":
    main()
