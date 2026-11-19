# E/D Vault 🔐
### Encryption and Decryption Vault

**Secure Your Files. Protect Your Privacy.**

E/D Vault is a Python-based cybersecurity web application designed to protect sensitive files through strong encryption and secure file management.

It uses **AES-256-GCM encryption**, **Scrypt key derivation**, and **SHA-256 integrity verification** to help protect files against unauthorized access and tampering.

---

## 🚀 Project Overview

E/D Vault allows users to:

- Register and securely log in.
- Upload files and encrypt them with a password.
- Download encrypted files in `.edv` format.
- Decrypt files using the correct encryption password.
- Store and manage encrypted files in a personal vault.
- Verify file integrity using SHA-256.
- View file activity history.
- Manage account security settings.

## 🛡️ Security Technologies

| Technology | Purpose |
|---|---|
| AES-256-GCM | Authenticated file encryption |
| Scrypt | Password-based key derivation |
| SHA-256 | File integrity verification |
| Werkzeug | Account password hashing |
| Flask-Limiter | Login and request rate limiting |
| Flask-WTF / CSRF protection | Form request protection |
| Secure Sessions | Session and cookie security |
| SQLite | Application database |

## ⚙️ Technology Stack

**Backend**
- Python
- Flask
- Flask-SQLAlchemy
- SQLite

**Frontend**
- HTML5
- CSS3
- JavaScript

**Cryptography**
- PyCA Cryptography
- AES-256-GCM
- Scrypt
- SHA-256

## ✨ Core Features

### 1. User Authentication
- User registration and login.
- Password hashing.
- Login rate limiting.
- Session protection.

### 2. File Encryption
- Upload files through the web interface.
- AES-256-GCM encryption.
- Random salt and nonce generation.
- Password-derived encryption keys.
- Encrypted `.edv` file format.

### 3. File Decryption
- Password-based decryption.
- Authentication tag verification.
- Wrong-password detection.
- Protection against corrupted encrypted files.

### 4. Personal Vault
- View encrypted files.
- Download encrypted files.
- Delete stored files.
- Per-user file access restrictions.

### 5. Integrity Verification
- SHA-256 hash calculation.
- Verification of encrypted file integrity.
- Detection of file modifications when a trusted baseline exists.

### 6. Activity History
- Track file-related activities.
- View recent activity.
- Search and filter activity records.

## 🔄 How It Works

**Encryption workflow**

1. User selects a file.
2. User enters an encryption password.
3. A random salt and nonce are generated.
4. Scrypt derives an encryption key.
5. AES-256-GCM encrypts the file.
6. The encrypted output is saved in `.edv` format.
7. SHA-256 integrity information is recorded.

**Decryption workflow**

1. User selects an encrypted `.edv` file.
2. User enters the encryption password.
3. The application reads the encryption metadata.
4. Scrypt derives the encryption key.
5. AES-256-GCM verifies and decrypts the data.
6. The decrypted file becomes available only after successful authentication.

## 📁 Project Structure

```text
E_D Vault/
│
├── app.py
├── config.py
├── extensions.py
│
├── authentication/
│   └── routes.py
│
├── database/
│   ├── db.py
│   └── models.py
│
├── encryption/
│   ├── key_manager.py
│   ├── file_format.py
│   ├── encrypt.py
│   └── decrypt.py
│
├── integrity/
│   └── hash_manager.py
│
├── routes/
│   └── files.py
│
├── templates/
│
├── tests/
│
├── sample_files/
│
├── instance/
│
├── .env
└── .gitignore
```

## 💻 Installation and Setup

### Prerequisites
- Python 3.10 or newer.
- pip.
- Git (optional).

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd "E_D Vault"
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

Install the project's required Python packages using its dependency list.

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root.

```env
SECRET_KEY=YOUR_RANDOM_SECRET_KEY
SESSION_COOKIE_SECURE=false
```

Generate a strong random secret key. Never publish your real `.env` file.

### 6. Run the application

```bash
python app.py
```

Open the local address shown by Flask in your browser.

## 🧪 Testing

Run the automated test suite:

```bash
python -m unittest discover -s tests -v
```

The project includes tests for:

- Encryption and decryption.
- Key generation and Scrypt.
- Encrypted file format validation.
- File integrity verification.
- Overwrite protection.
- Database security.
- HTTP security headers.

## ⚠️ Current Limitations

- The current encryption prototype supports files up to 100 MB.
- File encryption and decryption currently use whole-file memory processing.
- Authenticated chunk-based encryption is a future improvement for larger files.
- The application is currently designed as a local development prototype, not a production-hosted security service.
- Existing encrypted files without a saved integrity baseline cannot receive historical SHA-256 verification.

## 🔮 Future Improvements

- Authenticated chunk-based encryption for large files.
- Multi-factor authentication.
- Password recovery and account recovery workflows.
- Improved key management.
- Secure cloud storage integration.
- Advanced security monitoring.
- Deployment with HTTPS and production-grade rate-limit storage.
- Automated security testing.

## 👨‍💻 Project Information

**Project Name:** E/D Vault  
**Full Name:** Encryption and Decryption Vault  
**Category:** Cybersecurity / Cryptography  
**Version:** 1.0  
**Project Type:** Personal Project  
**Primary Language:** Python

---

### 🔐 Secure Your Files. Protect Your Privacy.

E/D Vault is a personal cybersecurity project focused on practical cryptography, secure file handling, and data protection.