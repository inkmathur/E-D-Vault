# E/D Vault — Technical Project Documentation

**Full Name:** Encryption and Decryption Vault  
**Version:** 1.0  
**Project Category:** Cybersecurity / Cryptography  
**Project Type:** Personal Project  
**Primary Language:** Python

---

# 1. Introduction

E/D Vault is a cybersecurity web application developed to protect digital files from unauthorized access.

The application provides file encryption, decryption, secure storage, and integrity verification through cryptographic techniques.

It uses AES-256-GCM for authenticated encryption and Scrypt for deriving encryption keys from user-provided passwords.

The primary purpose of E/D Vault is to demonstrate the practical implementation of cryptography and secure file management in a web application.

# 2. Problem Statement

Digital files often contain personal, professional, and confidential information.

When files are stored or transferred without proper protection, unauthorized individuals may access or modify their contents.

E/D Vault addresses this problem by providing a password-based file encryption and decryption system with integrity verification and user-specific file management.

# 3. Project Objectives

The main objectives are:

1. Protect files using strong encryption.
2. Prevent unauthorized file access.
3. Provide password-based encryption and decryption.
4. Detect modifications to encrypted files using SHA-256.
5. Provide secure user authentication.
6. Maintain a personal encrypted file vault.
7. Record file-related activities.
8. Demonstrate practical cybersecurity implementation.

# 4. Project Scope

E/D Vault is designed as a web-based file security application.

Its current scope includes:

- User registration and authentication.
- File upload and encryption.
- Encrypted file generation.
- Password-based file decryption.
- Encrypted file management.
- SHA-256 integrity verification.
- Activity history.
- Account security settings.

The current implementation is intended for local development and demonstration.

# 5. Technology Stack

| Technology | Implementation |
|---|---|
| Python | Main programming language |
| Flask | Web application framework |
| HTML5 | Page structure |
| CSS3 | User interface styling |
| JavaScript | Frontend interactions |
| SQLite | Database |
| Flask-SQLAlchemy | Database integration |
| PyCA Cryptography | Cryptographic operations |
| AES-256-GCM | File encryption |
| Scrypt | Key derivation |
| SHA-256 | Integrity verification |
| Werkzeug | Account password hashing |
| Flask-Limiter | Request rate limiting |
| Flask-WTF | CSRF protection |

# 6. System Architecture

E/D Vault follows a modular web application architecture.

The frontend communicates with Flask routes. Authentication and file-management routes interact with the database and cryptographic modules.

The encryption module handles key derivation, encrypted file creation, and decryption.

The integrity module calculates and verifies SHA-256 hashes.

## Main Components

1. Presentation Layer — HTML, CSS, and JavaScript.
2. Application Layer — Flask routes and authentication.
3. Cryptography Layer — AES-256-GCM and Scrypt.
4. Integrity Layer — SHA-256 verification.
5. Data Layer — SQLite and Flask-SQLAlchemy.
6. Storage Layer — Encrypted files.

# 7. Module Description

## 7.1 Authentication Module

The authentication module manages user accounts and access.

Functions include:

- User registration.
- User login.
- User logout.
- Password hashing.
- Session management.
- Protected page access.
- Login and registration rate limiting.

Account passwords are hashed before being stored in the database.

## 7.2 File Upload Module

The upload module accepts files from authenticated users.

It performs:

- File selection and upload.
- Filename validation.
- File-size validation.
- Safe temporary file handling.
- Secure storage naming.

The current upload limit is approximately 100 MB.

## 7.3 Encryption Module

The encryption module protects uploaded files.

It uses:

- AES-256-GCM authenticated encryption.
- Scrypt password-based key derivation.
- Random salt generation.
- Random nonce generation.
- Authenticated metadata.

The application creates an encrypted file with the `.edv` extension.

## 7.4 Decryption Module

The decryption module restores encrypted files.

It:

1. Reads the encrypted file header.
2. Validates encryption metadata.
3. Derives the encryption key using Scrypt.
4. Attempts AES-256-GCM decryption.
5. Verifies the authentication tag.
6. Makes the plaintext available only after successful verification.

Incorrect passwords and corrupted encrypted files are rejected.

## 7.5 Personal Vault Module

The vault provides a user-specific location for managing encrypted files.

Available operations:

- View encrypted files.
- Download encrypted files.
- Delete encrypted files.
- Verify file integrity.

Users can access only files associated with their accounts.

## 7.6 Integrity Verification Module

The integrity module uses SHA-256.

It calculates a hash of an encrypted file and compares it with the previously stored hash.

If the hashes match, the file matches its recorded integrity baseline.

If they do not match, the application reports a possible modification.

Older files without a stored baseline cannot receive historical hash verification.

## 7.7 Activity History Module

The activity module records file-related actions.

It provides:

- Activity history.
- Search functionality.
- Activity filtering.
- Recent activity records.

Activity records are associated with individual users.

## 7.8 Security Settings Module

The security settings module allows users to change their account password after verifying their current password.

The new password is hashed before database storage.

# 8. Database Design

E/D Vault uses SQLite with Flask-SQLAlchemy.

The current database contains three main models.

## 8.1 User Table

Stores account information.

| Field | Description |
|---|---|
| id | Unique user identifier |
| username | User's username |
| email | User's email address |
| password_hash | Hashed account password |
| created_at | Account creation timestamp |

## 8.2 VaultFile Table

Stores encrypted file information.

| Field | Description |
|---|---|
| id | Unique file identifier |
| user_id | Associated user |
| original_filename | Original file name |
| stored_filename | Stored encrypted file name |
| file_size | Encrypted file size |
| sha256_hash | Recorded SHA-256 hash |
| created_at | File creation timestamp |

## 8.3 ActivityLog Table

Stores user activity records.

| Field | Description |
|---|---|
| id | Unique activity identifier |
| user_id | Associated user |
| action | Activity type |
| filename | Related filename |
| created_at | Activity timestamp |

# 9. Encryption Algorithm

E/D Vault uses AES-256-GCM.

AES is a symmetric encryption algorithm, meaning the same derived key is used for encryption and decryption.

GCM provides authenticated encryption, which checks whether encrypted data has been modified.

## Encryption Process

1. User selects a file.
2. User enters an encryption password.
3. Application generates a random 16-byte salt.
4. Application generates a random 12-byte nonce.
5. Scrypt derives a 32-byte encryption key.
6. AES-256-GCM encrypts the file.
7. Authentication information is included in the encrypted output.
8. The encrypted file is saved with the `.edv` extension.

## Scrypt Configuration

| Parameter | Value |
|---|---|
| N | 32768 |
| r | 8 |
| p | 1 |
| Key Length | 32 bytes |
| Salt Length | 16 bytes |

## Decryption Process

1. User selects an `.edv` file.
2. User provides the encryption password.
3. Application reads the salt and nonce.
4. Scrypt derives the encryption key.
5. AES-256-GCM attempts decryption.
6. Authentication is verified.
7. Plaintext is made available only if verification succeeds.

# 10. Encrypted File Format

E/D Vault uses a custom `.edv` file format.

The format contains:

- File magic identifier.
- Format version.
- Encryption metadata.
- Key derivation parameters.
- Salt.
- Nonce.
- Encrypted content.
- Authentication tag.

The metadata is authenticated as associated data during AES-GCM encryption.

This helps prevent undetected changes to the protected metadata.

# 11. Security Implementation

The following protections are implemented:

1. AES-256-GCM authenticated encryption.
2. Scrypt-based encryption key derivation.
3. Random salt and nonce generation.
4. Werkzeug password hashing.
5. CSRF protection.
6. Login and registration rate limiting.
7. Session cookie security settings.
8. User-specific file access checks.
9. Secure filename validation.
10. Upload size restrictions.
11. SHA-256 integrity verification.
12. HTTP security headers.
13. Encrypted file authentication.
14. Safe temporary file handling.
15. SQLite foreign-key enforcement.

# 12. Testing

The project includes automated tests for:

- Encryption and decryption.
- Wrong-password rejection.
- File tampering detection.
- Unique encryption output.
- Key generation.
- Scrypt key derivation.
- Encrypted file-format validation.
- File integrity verification.
- Overwrite protection.
- HTTP security headers.
- Database security.

The developer has reported successful completion of the automated test suite and final manual application verification.

# 13. Current Limitations

The current implementation has the following limitations:

1. Maximum supported file size is approximately 100 MB.
2. Encryption and decryption currently process the whole file in memory.
3. Authenticated chunk-based encryption is not yet implemented.
4. The application is currently designed for local development.
5. Production deployment requires HTTPS and production-grade rate-limit storage.
6. Files created before integrity baselines were introduced may not have a saved SHA-256 hash.

# 14. Future Enhancements

Possible future improvements include:

- Authenticated chunk-based encryption.
- Multi-factor authentication.
- Secure account recovery.
- Improved key management.
- Cloud storage integration.
- Advanced security monitoring.
- Production deployment.
- Automated penetration testing.
- Security notifications.

# 15. Conclusion

E/D Vault demonstrates the practical application of cybersecurity and cryptographic techniques in a web-based file protection system.

By combining AES-256-GCM, Scrypt, SHA-256, secure authentication, and encrypted file management, the application provides a foundation for protecting sensitive digital information.

The project also demonstrates the importance of secure software development, authentication, data integrity, and safe file handling.

E/D Vault is an ongoing personal cybersecurity project with opportunities for further development and improvement.

---

**Project:** E/D Vault  
**Tagline:** Secure Your Files. Protect Your Privacy.  
**Version:** 1.0