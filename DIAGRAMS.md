# E/D Vault — System Diagrams

**Project:** Encryption and Decryption Vault  
**Version:** 1.0  
**Category:** Cybersecurity / Cryptography

---

# Diagram 1 — Overall System Architecture

```mermaid
flowchart TB
    USER["User"]
    BROWSER["Web Browser"]

    subgraph FRONTEND["Presentation Layer"]
        HTML["HTML5"]
        CSS["CSS3"]
        JS["JavaScript"]
    end

    subgraph BACKEND["Flask Application"]
        APP["app.py"]
        AUTH["Authentication Routes"]
        FILES["File Management Routes"]
        ACTIVITY["Activity Routes"]
        SETTINGS["Security Settings"]
    end

    subgraph CRYPTO["Cryptography Layer"]
        KEY["Scrypt Key Manager"]
        ENC["AES-256-GCM Encryption"]
        DEC["AES-256-GCM Decryption"]
        FORMAT["EDV File Format"]
    end

    subgraph INTEGRITY["Integrity Layer"]
        SHA["SHA-256 Hash Manager"]
    end

    subgraph STORAGE["Data and Storage"]
        DB[("SQLite Database")]
        VAULT[("Encrypted File Storage")]
        TEMP["Temporary Processing Files"]
    end

    USER --> BROWSER
    BROWSER --> FRONTEND
    FRONTEND --> APP

    APP --> AUTH
    APP --> FILES
    APP --> ACTIVITY
    APP --> SETTINGS

    AUTH --> DB
    FILES --> KEY
    KEY --> ENC
    KEY --> DEC
    ENC --> FORMAT
    DEC --> FORMAT
    FILES --> SHA

    ENC --> VAULT
    DEC --> TEMP
    FILES --> DB
    FILES --> VAULT
    ACTIVITY --> DB
    SETTINGS --> DB
```

# Diagram 2 — User Authentication Flow

```mermaid
flowchart TD
    A["Start Application"]
    B["Open Login Page"]
    C["Enter Username / Email"]
    D["Enter Account Password"]
    E["Validate Input"]
    F{"Valid Input?"}
    G["Find User Account"]
    H["Verify Password Hash"]
    I{"Credentials Correct?"}
    J["Show Login Error"]
    K["Create Authenticated Session"]
    L["Open Dashboard"]
    M["Access Protected Features"]
    N["Logout"]
    O["Clear Session"]
    P["End Session"]

    A --> B --> C --> D --> E --> F
    F -->|No| J --> B
    F -->|Yes| G --> H --> I
    I -->|No| J
    I -->|Yes| K --> L --> M --> N --> O --> P
```

# Diagram 3 — File Encryption Workflow

```mermaid
flowchart TD
    A["Authenticated User"]
    B["Open Encrypt Page"]
    C["Select File"]
    D["Enter Encryption Password"]
    E["Validate Password and Confirmation"]
    F{"Validation Successful?"}
    G["Display Error"]
    H["Validate File and Size"]
    I["Generate Random Salt"]
    J["Generate Random Nonce"]
    K["Derive Key Using Scrypt"]
    L["Encrypt with AES-256-GCM"]
    M["Create EDV File"]
    N["Calculate SHA-256"]
    O["Save Encrypted File"]
    P["Save Database Metadata"]
    Q["Record Activity"]
    R["Encryption Complete"]

    A --> B --> C --> D --> E --> F
    F -->|No| G
    F -->|Yes| H --> I --> J --> K --> L
    L --> M --> N --> O --> P --> Q --> R
```

# Diagram 4 — File Decryption Workflow

```mermaid
flowchart TD
    A["Authenticated User"]
    B["Open Decrypt Page"]
    C["Select EDV File"]
    D["Enter Encryption Password"]
    E["Validate File Metadata"]
    F["Read Salt and Nonce"]
    G["Derive Key Using Scrypt"]
    H["AES-256-GCM Decryption"]
    I{"Authentication Successful?"}
    J["Reject Decryption"]
    K["Verify Original File Size"]
    L["Make Plaintext Available"]
    M["Record Activity"]
    N["Decryption Complete"]

    A --> B --> C --> D --> E --> F
    F --> G --> H --> I
    I -->|No| J
    I -->|Yes| K --> L --> M --> N
```

# Diagram 5 — Database Entity Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ VAULT_FILE : owns
    USER ||--o{ ACTIVITY_LOG : generates

    USER {
        integer id PK
        string username UK
        string email UK
        string password_hash
        datetime created_at
    }

    VAULT_FILE {
        integer id PK
        integer user_id FK
        string original_filename
        string stored_filename UK
        integer file_size
        string sha256_hash
        datetime created_at
    }

    ACTIVITY_LOG {
        integer id PK
        integer user_id FK
        string action
        string filename
        datetime created_at
    }
```

# Diagram 6 — Encrypted File Structure

```mermaid
flowchart TD
    A["EDV Encrypted File"]
    A --> B["Magic Identifier"]
    A --> C["Format Version"]
    A --> D["Header Length"]
    A --> E["JSON Metadata"]
    A --> F["Encrypted Content"]
    A --> G["Authentication Tag"]

    E --> H["Algorithm Information"]
    E --> I["Scrypt Parameters"]
    E --> J["Random Salt"]
    E --> K["Random Nonce"]
    E --> L["Original File Metadata"]
```

# Diagram 7 — Security Architecture

```mermaid
flowchart TB
    USER["User"]

    subgraph ACCESS["Access Protection"]
        AUTH["Authentication"]
        SESSION["Secure Sessions"]
        RATE["Rate Limiting"]
        CSRF["CSRF Protection"]
    end

    subgraph FILE["File Protection"]
        AES["AES-256-GCM"]
        SCRYPT["Scrypt"]
        SHA["SHA-256"]
        VALIDATION["File Validation"]
    end

    subgraph DATA["Data Protection"]
        OWNERSHIP["User Ownership Checks"]
        DB["SQLite Constraints"]
        HEADERS["HTTP Security Headers"]
    end

    USER --> AUTH
    AUTH --> SESSION
    AUTH --> RATE
    AUTH --> CSRF

    SESSION --> AES
    AES --> SCRYPT
    AES --> SHA
    AES --> VALIDATION

    VALIDATION --> OWNERSHIP
    OWNERSHIP --> DB
    DB --> HEADERS
```

---

# Diagram Summary

| Diagram | Purpose |
|---|---|
| 1. System Architecture | Explains overall application structure |
| 2. Authentication Flow | Explains account login and logout |
| 3. Encryption Workflow | Explains file encryption |
| 4. Decryption Workflow | Explains file restoration |
| 5. ER Diagram | Explains database relationships |
| 6. EDV File Structure | Explains encrypted file components |
| 7. Security Architecture | Explains security controls |

---

**E/D Vault — Secure Your Files. Protect Your Privacy.**