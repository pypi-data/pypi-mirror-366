# 🔐 page-encryptor

**page-encryptor** is a simple Python utility to encrypt static HTML pages offline and embed a JavaScript-based decryptor for in-browser access. It's inspired by [PageCrypt](https://github.com/MaxLaumeister/PageCrypt) by Max Laumeister, but is independently developed and substantially refactored for modern Python workflows and packaging.

## ✨ Features

- AES-GCM encryption with PBKDF2 key derivation
- Fully static: No server required
- Runs offline — ideal for sensitive or private HTML content
- Decrypts in-browser using an embeddable JavaScript template
- Optional auto-unlock via ?pass=... in the URL
- Designed for automation and integration into static site generators (e.g., 11ty)
- Lightweight and dependency-minimal

## 📦 Installation

```bash
pip install page-encryptor
```

## 🚀 Usage

```bash
page-encryptor \
  --input path/to/file.html \
  --password your-secret-password \
  --template decryptor_template.html \
  --output protected-file.html

```

The template file must contain the placeholder `/*__PAYLOAD__*/""` which will be replaced with the encrypted data payload in Base64. See [decryptor_template.html](page_encryptor/templates/decryptor_template.html).

Once encrypted, open the resulting HTML in any modern browser. You can enter the password manually, or append `?pass=your-secret-password` to the URL to attempt automatic decryption.

## 🧩 Example

```bash
page-encryptor \
  --input index.html \
  --template decryptor_template.html \
  --output index-protected.html \
  --password hunter2

```

You can now open `index-protected.html` in a browser and enter your password to decrypt it in place.

## 🛠️ Development

To set up the project locally:

```bash
git clone https://github.com/yourname/page-encryptor.git
cd page-encryptor
python3 -m venv venv
source venv/bin/activate.fish
pip install .
pip install .[dev]
```

Run script:

```bash
cd page_encryptor
./encryptor.py --help
```

Run formatting and hooks:

```bash
pre-commit install
pre-commit run --all-files
```
