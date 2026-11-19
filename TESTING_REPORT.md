# E/D Vault — Testing and Results Report

**Project Name:** Encryption and Decryption Vault  
**Version:** 1.0  
**Project Category:** Cybersecurity / Cryptography  
**Testing Type:** Functional Testing, Security Testing, Integration Testing and Unit Testing

---

# 1. Introduction

Testing is an important part of software development. It helps identify errors, verify functionality, and ensure that application components work as expected.

E/D Vault has undergone testing of its encryption engine, decryption engine, authentication system, file management, integrity verification, and security controls.

This report documents the test cases, expected results, and reported outcomes.

# 2. Testing Objectives

The main objectives are:

1. Verify that file encryption works correctly.
2. Verify that encrypted files can be decrypted.
3. Ensure incorrect passwords are rejected.
4. Detect modifications to encrypted files.
5. Verify account authentication.
6. Test file upload restrictions.
7. Verify user-specific vault access.
8. Test database security.
9. Verify HTTP security headers.
10. Ensure the application works as an integrated system.

# 3. Testing Environment

| Component | Environment |
|---|---|
| Operating System | Windows |
| Programming Language | Python |
| Backend | Flask |
| Database | SQLite |
| Cryptography Library | PyCA Cryptography |
| Encryption Algorithm | AES-256-GCM |
| Key Derivation | Scrypt |
| Integrity Algorithm | SHA-256 |
| Testing Framework | Python unittest |
| Development Environment | Visual Studio Code |
| Browser | Web Browser |

# 4. Types of Testing

## 4.1 Unit Testing

Individual modules are tested separately.

Examples:

- Key generation.
- Encryption functions.
- Decryption functions.
- File-format validation.
- SHA-256 calculations.

## 4.2 Functional Testing

Checks whether application features perform their intended operations.

Examples:

- Registration.
- Login.
- File encryption.
- File decryption.
- Vault management.
- Password changes.

## 4.3 Security Testing

Checks whether security protections work correctly.

Examples:

- Wrong-password rejection.
- File tampering detection.
- CSRF protection.
- Rate limiting.
- Secure HTTP headers.
- Database foreign-key enforcement.

## 4.4 Integration Testing

Checks whether different application components work together.

Examples:

- Flask routes communicating with the database.
- Upload routes invoking the encryption engine.
- Vault routes accessing stored encrypted files.
- Activity routes displaying recorded actions.

# 5. Encryption Testing

| Test ID | Test Case | Expected Result | Reported Result |
|---|---|---|---|
| ENC-01 | Encrypt a valid file | Encrypted `.edv` file created | Passed |
| ENC-02 | Decrypt with correct password | Original file restored | Passed |
| ENC-03 | Decrypt with incorrect password | Decryption rejected | Passed |
| ENC-04 | Modify encrypted content | Authentication failure | Passed |
| ENC-05 | Encrypt same file multiple times | Different encrypted outputs | Passed |
| ENC-06 | Use empty encryption password | Validation error | Passed |
| ENC-07 | Attempt to overwrite existing output | Existing file protected | Passed |

# 6. Key Management Testing

| Test ID | Test Case | Expected Result | Reported Result |
|---|---|---|---|
| KEY-01 | Generate random salt | 16-byte salt | Passed |
| KEY-02 | Generate random nonce | 12-byte nonce | Passed |
| KEY-03 | Derive encryption key | 32-byte key | Passed |
| KEY-04 | Same password and salt | Same derived key | Passed |
| KEY-05 | Different salts | Different derived keys | Passed |
| KEY-06 | Empty password | Rejected | Passed |
| KEY-07 | Invalid salt | Rejected | Passed |
| KEY-08 | Excessively long password | Rejected | Passed |

# 7. File Format Testing

The custom `.edv` format was tested for valid and invalid input.

| Test ID | Test Case | Expected Result | Reported Result |
|---|---|---|---|
| FMT-01 | Serialize valid metadata | Valid file header | Passed |
| FMT-02 | Serialize metadata repeatedly | Stable serialization | Passed |
| FMT-03 | Generate authenticated data | Correct AAD | Passed |
| FMT-04 | Parse valid encrypted file | Successful parsing | Passed |
| FMT-05 | Invalid magic identifier | Rejected | Passed |
| FMT-06 | Empty header | Rejected | Passed |
| FMT-07 | Oversized header | Rejected | Passed |
| FMT-08 | Duplicate JSON keys | Rejected | Passed |
| FMT-09 | Non-standard JSON values | Rejected | Passed |
| FMT-10 | Incomplete encrypted file | Rejected | Passed |
| FMT-11 | Invalid header type | Rejected | Passed |
| FMT-12 | Invalid AAD input | Rejected | Passed |

# 8. Integrity Testing

| Test ID | Test Case | Expected Result | Reported Result |
|---|---|---|---|
| INT-01 | Calculate SHA-256 | Valid 64-character hexadecimal hash | Passed |
| INT-02 | Verify unchanged file | Integrity confirmed | Passed |
| INT-03 | Verify modified file | Integrity mismatch detected | Passed |
| INT-04 | Verify missing file | File error reported | Passed |
| INT-05 | Verify invalid hash | Rejected | Passed |

# 9. Authentication Testing

| Test ID | Test Case | Expected Result | Reported Result |
|---|---|---|---|
| AUTH-01 | Register valid account | Account created | Passed |
| AUTH-02 | Login with correct credentials | Dashboard accessible | Passed |
| AUTH-03 | Login with incorrect password | Access rejected | Passed |
| AUTH-04 | Register duplicate username/email | Registration rejected | Passed |
| AUTH-05 | Submit short password | Validation error | Passed |
| AUTH-06 | Submit mismatched passwords | Registration rejected | Passed |
| AUTH-07 | Access dashboard without login | Redirect to login | Passed |
| AUTH-08 | Logout | Session cleared | Passed |
| AUTH-09 | Repeated login attempts | Rate limit enforced | Passed |

# 10. File Management Testing

| Test ID | Test Case | Expected Result | Reported Result |
|---|---|---|---|
| FILE-01 | Upload supported file | Upload accepted | Passed |
| FILE-02 | Upload oversized file | Upload rejected | Passed |
| FILE-03 | View personal vault | User's files displayed | Passed |
| FILE-04 | Download encrypted file | Password verification required | Passed |
| FILE-05 | Delete encrypted file | Account password verification required | Passed |
| FILE-06 | Verify encrypted file | Integrity result displayed | Passed |
| FILE-07 | Access another user's file | Access denied | Passed |

# 11. Web Security Testing

| Test ID | Test Case | Expected Result | Reported Result |
|---|---|---|---|
| WEB-01 | Submit form without valid CSRF token | Request rejected | Passed |
| WEB-02 | Check X-Content-Type-Options | `nosniff` returned | Passed |
| WEB-03 | Check X-Frame-Options | `DENY` returned | Passed |
| WEB-04 | Check Referrer-Policy | Expected policy returned | Passed |
| WEB-05 | Check Content-Security-Policy | Policy returned | Passed |
| WEB-06 | Open application root | Appropriate redirect | Passed |

# 12. Database Security Testing

| Test ID | Test Case | Expected Result | Reported Result |
|---|---|---|---|
| DB-01 | Check SQLite foreign keys | Enforcement enabled | Passed |
| DB-02 | Check VaultFile foreign key | Constraint exists | Passed |
| DB-03 | Check ActivityLog foreign key | Constraint exists | Passed |
| DB-04 | Check foreign-key violations | No existing violations | Passed |

# 13. Manual Application Testing

The complete application workflow was also reported as tested.

| Test | Expected Result | Reported Result |
|---|---|---|
| Registration and login | Successful authentication | Passed |
| File encryption | `.edv` file generated | Passed |
| Integrity verification | Correct integrity result | Passed |
| Correct-password decryption | Original file restored | Passed |
| Wrong-password decryption | Operation rejected | Passed |
| Vault download | Encrypted file downloaded | Passed |
| Vault deletion | File deleted after verification | Passed |
| Password change | Account password updated | Passed |
| Activity History | Activities displayed | Passed |

# 14. Overall Testing Results

The developer reported successful execution of the automated test suite and completion of the manual application workflow.

The reported results cover:

- Encryption and decryption.
- Key management.
- File-format validation.
- Integrity verification.
- Overwrite protection.
- Authentication.
- File management.
- Web security.
- Database security.
- Application integration.

The exact total number of executed tests is not recorded in this report.

# 15. Known Testing Limitations

The current testing does not establish that the application is production-ready.

Further testing is recommended for:

1. Large-file memory consumption.
2. Concurrent user operations.
3. Production deployment security.
4. Penetration testing.
5. Dependency vulnerability scanning.
6. Cross-browser compatibility.
7. Recovery after unexpected process termination.
8. Backup and restoration procedures.

# 16. Conclusion

Testing has played an important role in validating the E/D Vault application.

The reported results demonstrate successful operation of the main encryption, decryption, authentication, file management, integrity, and security features.

Additional performance testing, penetration testing, and production deployment validation are recommended before using the application to protect real-world sensitive data.

---

**E/D Vault**  
*Secure Your Files. Protect Your Privacy.*