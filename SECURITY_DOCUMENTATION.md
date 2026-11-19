# E/D Vault — Security Documentation

**Project Name:** Encryption and Decryption Vault  
**Version:** 1.0  
**Category:** Cybersecurity / Cryptography  
**Tagline:** Secure Your Files. Protect Your Privacy.

---

# 1. Introduction

E/D Vault is a file protection application designed to provide confidentiality, integrity verification, and controlled access to encrypted files.

The application uses cryptographic algorithms and web security controls to reduce the risk of unauthorized access, file tampering, and account compromise.

This document describes the security architecture, implemented protections, threat model, and known limitations of E/D Vault.

# 2. Security Objectives

The primary security objectives are:

1. **Confidentiality:** Protect file contents from unauthorized access.
2. **Integrity:** Detect modifications to encrypted files.
3. **Authentication:** Verify user credentials before allowing access.
4. **Authorization:** Restrict file operations to the file owner.
5. **Secure Processing:** Validate uploaded files and safely handle temporary data.
6. **Account Protection:** Protect account passwords and authenticated sessions.

# 3. Cryptographic Architecture

## 3.1 AES-256-GCM

E/D Vault uses AES-256-GCM for file encryption.

AES is a symmetric encryption algorithm that uses the same secret key for encryption and decryption.

GCM provides authenticated encryption, which offers:

- Confidentiality of file contents.
- Authentication of encrypted data.
- Detection of unauthorized modifications.

The application uses a 256-bit encryption key.

## 3.2 Scrypt Key Derivation

Scrypt derives encryption keys from user-provided passwords.

Configuration:

| Parameter | Value |
|---|---|
| N | 32768 |
| r | 8 |
| p | 1 |
| Derived Key | 32 bytes |
| Salt | 16 bytes |

A random salt is generated for each encryption operation.

The encryption password is not stored in the database.

## 3.3 Nonce Management

AES-GCM requires nonce uniqueness for every encryption operation under the same key.

E/D Vault generates a random 12-byte nonce for each encryption operation.

Nonce reuse with the same key must be avoided because it can severely compromise AES-GCM security.

## 3.4 SHA-256 Integrity Verification

SHA-256 generates a 256-bit hash of the encrypted file.

The calculated hash is stored as an integrity baseline.

When verification is requested, the application calculates the hash again and compares it with the stored value.

A mismatch indicates that the file no longer matches its recorded baseline.

**Important:** SHA-256 verification detects changes relative to a trusted baseline. It does not independently authenticate the database record containing that baseline.

# 4. Password Security

E/D Vault handles two different password types.

### Account Password

Used for:

- User registration.
- User login.
- Account password changes.
- Confirming account ownership for file deletion.

Account passwords are hashed using Werkzeug password hashing functions.

### File Encryption Password

Used for:

- Encrypting files.
- Decrypting files.
- Verifying the password before encrypted-file download.

The file encryption password is used by Scrypt to derive the encryption key.

It is not stored in plaintext or saved as an encryption key in the database.

# 5. Authentication Security

The authentication module implements:

- Password hashing.
- Login rate limiting.
- Registration rate limiting.
- Generic invalid-login messages.
- Dummy password-hash verification for nonexistent usernames.
- Session clearing during login and logout.
- Protected routes.
- Session lifetime configuration.

Rate limits currently include:

- Login: 5 attempts per minute.
- Registration: 5 attempts per hour.

The current rate-limit storage uses in-memory storage, which is appropriate for the local prototype but should be replaced with shared persistent storage for multi-instance deployment.

# 6. Web Application Security

## 6.1 CSRF Protection

Cross-Site Request Forgery protection is enabled for protected form submissions.

CSRF tokens are included in application forms.

## 6.2 Session Security

The application configures:

- HttpOnly session cookies.
- SameSite=Lax.
- A 30-minute permanent session lifetime.
- Secure cookie configuration through an environment variable.

For production deployment, HTTPS must be enabled and `SESSION_COOKIE_SECURE` must be set to `true`.

## 6.3 HTTP Security Headers

The application adds these security headers:

| Header | Purpose |
|---|---|
| X-Content-Type-Options | Prevents MIME-type sniffing |
| X-Frame-Options | Restricts framing |
| Referrer-Policy | Controls referrer information |
| Permissions-Policy | Restricts browser features |
| Content-Security-Policy | Restricts permitted content sources |

## 6.4 Rate Limiting

Flask-Limiter restricts repeated authentication and file-processing requests.

This helps reduce automated abuse and repeated password attempts.

# 7. File Upload Security

E/D Vault uses multiple upload protections:

- Filename validation.
- Secure filename handling.
- UUID-based encrypted storage filenames.
- File-size restrictions.
- Chunked upload writing.
- Extension validation for stored encrypted files.
- Path validation.
- Symlink checks.
- Temporary file cleanup.

The application does not execute uploaded files.

The current maximum supported file size is approximately 100 MB.

# 8. Access Control

Every authenticated user has access to their own encrypted files.

The application checks file ownership before allowing operations such as:

- Decryption.
- Download.
- Integrity verification.
- Deletion.

This prevents normal application requests from accessing another user's vault files.

# 9. Temporary File Security

Temporary files are used during file upload, encryption, and decryption operations.

The application uses temporary directories and cleanup operations to reduce the time plaintext files remain on disk.

Temporary file cleanup is an important part of secure file handling.

However, deleting a file does not guarantee forensic erasure from all storage devices or backups.

# 10. Database Security

E/D Vault uses SQLite with Flask-SQLAlchemy.

Database protections include:

- Parameterized ORM queries.
- Unique username and email constraints.
- User-to-file relationships.
- User-to-activity relationships.
- SQLite foreign-key enforcement.
- Password hashes instead of plaintext account passwords.

Database files must remain private and must not be included in public source-code repositories.

# 11. Threat Model

The following table describes major threats considered in E/D Vault.

| Threat | Potential Impact | Implemented Protection |
|---|---|---|
| Unauthorized file access | Exposure of sensitive files | AES-256-GCM |
| Incorrect encryption password | Failed decryption | GCM authentication |
| Encrypted file modification | Data corruption or tampering | GCM authentication and SHA-256 baseline |
| Brute-force login attempts | Account compromise | Rate limiting |
| CSRF attacks | Unauthorized form actions | CSRF protection |
| Unsafe filenames | Path manipulation | Filename validation |
| Oversized uploads | Resource exhaustion | Upload size restrictions |
| Unauthorized vault access | Access to another user's files | Ownership checks |
| Session misuse | Unauthorized account access | Session security settings |
| Database relationship errors | Orphaned records | Foreign-key enforcement |

# 12. Security Limitations

Although E/D Vault includes several security controls, it is not yet a production-certified security product.

Known limitations include:

1. Encryption and decryption process the whole file in memory.
2. The current maximum file size is approximately 100 MB.
3. Authenticated chunk-based encryption is not implemented.
4. In-memory rate limiting is unsuitable for distributed production deployments.
5. The current application is designed for local development.
6. A compromised server or operating system may expose plaintext during processing.
7. SHA-256 baselines stored in the same database are not independently protected against a privileged database attacker.
8. Secure deletion and forensic erasure are not guaranteed.

# 13. Recommended Future Security Improvements

Future improvements should include:

- Authenticated chunk-based encryption.
- Multi-factor authentication.
- Stronger production key management.
- HTTPS deployment.
- Persistent distributed rate-limit storage.
- Database backup and recovery protection.
- Security monitoring and alerting.
- Independent integrity-baseline protection.
- Automated vulnerability scanning.
- Penetration testing.
- Production-grade deployment hardening.

# 14. Security Testing

Security testing has included:

- Correct-password decryption.
- Incorrect-password rejection.
- Encrypted-file tampering tests.
- Encryption output uniqueness tests.
- Overwrite protection tests.
- File-format validation.
- Upload-size restriction tests.
- CSRF protection tests.
- HTTP security-header tests.
- SQLite foreign-key tests.
- Full automated test-suite execution.

The developer has reported successful completion of the current automated test suite.

# 15. Conclusion

E/D Vault demonstrates the practical use of cryptographic techniques and web security controls in a file protection application.

AES-256-GCM provides authenticated file encryption, Scrypt derives encryption keys, and SHA-256 supports integrity verification against recorded baselines.

Additional protections for authentication, file access, uploads, sessions, and database relationships contribute to the application's security design.

The project remains an evolving prototype, with further improvements planned before any production deployment.

---

**E/D Vault**  
*Secure Your Files. Protect Your Privacy.*