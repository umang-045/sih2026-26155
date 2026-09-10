````
# AI-Augmented Multi-Vendor Network Compliance Auditor

An AI-augmented, vendor-agnostic network configuration compliance auditing platform that maps heterogeneous device CLI syntax (Cisco, Juniper, Palo Alto) to standardized security benchmarks such as CIS, DISA STIG, and NIST.

The platform replaces manual, vendor-specific auditing workflows with a unified normalization, policy evaluation, training, and reporting pipeline.

---

## Key Features

- **Unified Ingestion Engine**
  - Upload and audit single or multiple network configuration files.
  - Supports `.cfg` and `.txt` files.

- **Vendor-Agnostic Normalization**
  - Detects supported network vendors.
  - Converts vendor-specific CLI syntax into a standardized JSON Security Baseline Model.

- **OPA Multi-Framework Compliance Engine**
  - Evaluates normalized configurations using Open Policy Agent.
  - Supports Rego v1 security policies.
  - Designed for CIS, DISA STIG, and NIST compliance frameworks.

- **AI-Powered Training Module**
  - Human-in-the-loop training interface available at `/train`.
  - Administrators can map previously unseen CLI commands to compliance feature keys.
  - Mapping updates are persisted dynamically without requiring backend code changes or redeployment.

- **Actionable PDF Reporting**
  - Generates downloadable executive audit reports.
  - Includes compliance status, risk severity, failed controls, and CLI remediation commands.

---

## Architecture

```text
                         ┌──────────────────────────┐
                         │      Web Dashboard       │
                         │ HTML + Tailwind + JS     │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │       FastAPI API        │
                         │       app/main.py        │
                         └────────────┬─────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
             ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
             │   Config    │  │ Normalization │  │ PDF Reporting │
             │   Parser    │  │    Engine     │  │    Engine     │
             └──────┬──────┘  └──────┬───────┘  └──────────────┘
                    │                 │
                    │                 ▼
                    │        ┌─────────────────┐
                    │        │  Standardized   │
                    │        │ Security Model  │
                    │        └────────┬────────┘
                    │                 │
                    │                 ▼
                    │        ┌─────────────────┐
                    │        │ Open Policy     │
                    │        │ Agent / Rego    │
                    │        └────────┬────────┘
                    │                 │
                    └─────────────────┤
                                      ▼
                            ┌──────────────────┐
                            │ Compliance       │
                            │ Findings         │
                            └──────────────────┘
````

---

 ## Tech Stack

 ### Backend

 - Python 3.10+
- FastAPI
- Uvicorn
- Pybatfish
- ciscoconfparse2
- ReportLab

 ### Policy Engine

 - Open Policy Agent (OPA)
- Rego v1

 ### Frontend

 - HTML5
- Tailwind CSS via CDN
- Vanilla JavaScript

 ### Data Persistence

 - JSON-based dynamic mapping store
- `app/mappings.json`

 ### Testing

 - Pytest

---

 ## Repository Structure

```
network-compliance-auditor/
│
├── app/
│   ├── main.py
│   ├── parser.py
│   ├── reporter.py
│   ├── mappings.json
│   │
│   └── static/
│       └── index.html
│
├── rules/
│   └── compliance.rego
│
├── samples/
│   ├── cisco_switch.cfg
│   └── juniper_router.cfg
│
├── tests/
│   └── test_audit.py
│
├── requirements.txt
└── README.md
```

---

 ## Prerequisites

 Make sure the following are installed:

 - Python 3.10 or higher
- Open Policy Agent (OPA)
- Git

 Verify the installations:

```
python --version
opa version
git --version
```

---

 ## Installation

 ### 1\. Clone the Repository

```
git clone https://github.com/your-username/network-compliance-auditor.git
cd network-compliance-auditor
```

---

 ### 2\. Create a Virtual Environment

 #### Linux / macOS

```
python3 -m venv venv
source venv/bin/activate
```

 #### Windows

```
python -m venv venv
venv\Scripts\activate
```

---

 ### 3\. Install Dependencies

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

 ## Running the Application

 The application requires both **OPA** and the **FastAPI server**.

 ### Step 1: Start OPA

 Open a new terminal and run:

```
opa run --server --addr=0.0.0.0:8181 ./rules
```

 OPA will be available at:

```
http://127.0.0.1:8181
```

---

 ### Step 2: Start FastAPI

 From the project root:

```
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

 The application will be available at:

```
http://127.0.0.1:8000
```

---

 ## Web Dashboard

 Open your browser and navigate to:

```
http://127.0.0.1:8000
```

 The dashboard provides access to:

 - Configuration auditing
- Compliance results
- Risk assessment
- PDF reporting
- Dynamic CLI training

---

 ## Usage

 ### 1\. Audit a Device Configuration

 1. Open the web dashboard.
2. Click **Browse**.
3. Select a network configuration file.
4. Click **Audit File**.

 Example configuration files:

```
samples/cisco_switch.cfg
samples/juniper_router.cfg
```

 The application processes the configuration through the following pipeline:

```
Configuration File
        ↓
Vendor Detection
        ↓
CLI Parsing
        ↓
Feature Extraction
        ↓
Normalization
        ↓
OPA / Rego Evaluation
        ↓
Compliance Findings
```

 The dashboard displays:

 - Device vendor
- Device metadata
- Compliance status
- Failed controls
- Risk severity
- Remediation recommendations

 Possible compliance states:

```
COMPLIANT
NON_COMPLIANT
```

---

 ### 2\. Generate a PDF Report

 After completing an audit:

 1. Click **Download PDF Report**.
2. The backend processes the configuration.
3. A PDF report is generated using ReportLab.
4. The report can be downloaded for further analysis or distribution.

 The report contains:

 - Executive summary
- Device information
- Compliance status
- Failed controls
- Risk severity
- Remediation recommendations
- Device-specific CLI commands

---

 ### 3\. Train New CLI Patterns

 The application provides a human-in-the-loop training workflow.

 Navigate to the **Dynamic AI Training Loop** section.

 Example:

```
Vendor:
Juniper

Feature Key:
has_enable_secret

CLI Pattern:
plain-text-password
```

 After clicking **Save Mapping**, the mapping is stored in:

```
app/mappings.json
```

 Example mapping:

```
{
  "juniper": {
    "has_enable_secret": [
      "plain-text-password"
    ]
  }
}
```

 This allows administrators to extend CLI recognition rules without modifying the parser source code.

---

 ## API Endpoints

 | Endpoint | Method | Description |
| --- | --- | --- |
| `/` | `GET` | Serves the web dashboard |
| `/audit` | `POST` | Uploads and audits a network configuration |
| `/audit/pdf` | `POST` | Generates and downloads a PDF audit report |
| `/train` | `POST` | Adds a new CLI-to-feature mapping |

---

 ## API Examples

 ### Audit Configuration

```
curl -X POST \
  http://127.0.0.1:8000/audit \
  -F "file=@samples/cisco_switch.cfg"
```

---

 ### Generate PDF Report

```
curl -X POST \
  http://127.0.0.1:8000/audit/pdf \
  -F "file=@samples/cisco_switch.cfg" \
  --output audit_report.pdf
```

---

 ### Add Training Mapping

```
curl -X POST \
  http://127.0.0.1:8000/train \
  -H "Content-Type: application/json" \
  -d '{
    "vendor": "Juniper",
    "feature_key": "has_enable_secret",
    "cli_pattern": "plain-text-password"
  }'
```

---

 ## Supported Vendors

 The normalization engine is designed to support multiple network vendors.

 Current target vendors:

 - Cisco
- Juniper
- Palo Alto

 The architecture can be extended to support additional vendors through parser logic and dynamic CLI mappings.

---

 ## Compliance Frameworks

 The policy engine is designed to support standardized security frameworks, including:

 - CIS Benchmarks
- DISA STIG
- NIST

 Compliance rules are maintained in:

```
rules/compliance.rego
```

---

 ## Example Compliance Workflow

```
┌──────────────────────────┐
│ Network Configuration    │
│ .cfg / .txt              │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Vendor Detection         │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ CLI Parsing              │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Feature Extraction       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Standardized Security    │
│ Baseline Model           │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ OPA / Rego Policies      │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Compliance Findings      │
└────────────┬─────────────┘
             │
       ┌─────┴─────┐
       ▼           ▼
┌────────────┐ ┌────────────┐
│ Dashboard  │ │ PDF Report │
└────────────┘ └────────────┘
```

---

 ## Dynamic Training Workflow

```
Unknown CLI Command
        │
        ▼
Administrator Review
        │
        ▼
Select Vendor
        │
        ▼
Select Feature Key
        │
        ▼
Add CLI Pattern
        │
        ▼
Save Mapping
        │
        ▼
app/mappings.json
        │
        ▼
Available to Future Audits
```

---

 ## Running Tests

 Run the complete test suite:

```
pytest tests/
```

 Run tests with verbose output:

```
pytest tests/ -v
```

---

 ## Development

 Start the FastAPI development server with automatic reload:

```
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

 Run tests:

```
pytest tests/ -v
```

---

 ## Security Considerations

 Network configuration files may contain sensitive information, including:

 - IP addresses
- Usernames
- Encrypted credentials
- SNMP communities
- Routing information
- Network topology information
- Access-control configuration

 When deploying this project in a production environment, consider implementing:

 - Authentication and authorization
- Role-based access control
- HTTPS/TLS
- Secure file upload validation
- File size restrictions
- Input sanitization
- Malware scanning
- Secure OPA configuration
- Audit logging
- Secure configuration storage
- Database-backed persistence
- Access control for training mappings

 Do not expose the application or OPA server directly to the public internet without appropriate security controls.

---

 ## Production Deployment

 For production environments, consider:

 - Running FastAPI behind a reverse proxy
- Enabling HTTPS
- Adding authentication
- Replacing JSON persistence with a database
- Implementing structured logging
- Containerizing the application
- Restricting OPA network access
- Implementing secure file uploads
- Adding CI/CD pipelines
- Adding monitoring and alerting

---

 ## Roadmap

 - [ ] Support additional network vendors
- [ ] Expand CIS benchmark coverage
- [ ] Expand DISA STIG coverage
- [ ] Add NIST control mappings
- [ ] Add user authentication
- [ ] Add role-based access control
- [ ] Replace JSON mappings with database persistence
- [ ] Add configuration version history
- [ ] Add audit history
- [ ] Add Docker support
- [ ] Add CI/CD pipeline
- [ ] Add scheduled audits
- [ ] Add multi-device bulk auditing
- [ ] Improve AI-assisted CLI classification
- [ ] Add SIEM integration
- [ ] Add API authentication
- [ ] Add enterprise reporting

---

 ## Contributing

 Contributions are welcome.

 ### 1\. Fork the Repository

 Create a fork of the repository on GitHub.

 ### 2\. Create a Feature Branch

```
git checkout -b feature/your-feature
```

 ### 3\. Make Your Changes

 Implement your changes and add appropriate tests.

 ### 4\. Run Tests

```
pytest tests/ -v
```

 ### 5\. Commit Changes

```
git add .
git commit -m "Add your feature"
```

 ### 6\. Push the Branch

```
git push origin feature/your-feature
```

 Then open a Pull Request on GitHub.

---

 ## License

 This project is currently unlicensed.

 If you intend to distribute this project publicly, consider adding an appropriate license such as the MIT License.

 Create a `LICENSE` file in the repository containing the selected license.

---

 ## Author

 **Your Name**

 GitHub: https://github.com/your-username

---

 ## Project Status

 **Status: Active Development**

 This project provides a foundation for automated, vendor-agnostic net    ion files to generate Pass/Fail compliance reports for standards like CIS, DISA STIG, or NIST SP 800-53.

    Hackathon Judges / Evaluators: During your project presentation, the judges will click the Browse... button to upload sample CLI configuration files (.cfg, .txt) to test if your engine correctly identifies misconfigurations and generates the PDF report.

and thw dynamic ai part is for

The Dynamic AI Training Module (Human-in-the-Loop) is designed for Network Administrators and Security Engineers to dynamically teach the system how to parse unrecognized or novel CLI commands without modifying backend code.
Purpose & Problem It Solves

    The Problem: Networking vendors (Cisco, Juniper, Palo Alto, Fortinet) constantly release new OS updates, and enterprise networks often feature custom syntax or lesser-known commands. Traditional static tools fail or break when encountering CLI commands they weren't pre-programmed to recognize.

    The AI/Dynamic Solution: Instead of waiting for a developer to update Python parsers or regex rules, the admin uses Section 2 of the GUI to map an unknown command pattern directly to a standardized compliance baseline parameter on the fly.

Real-World Example

    Scenario: A Juniper router uses a custom or new syntax like plain-text-password to define access passwords, which the engine doesn't recognize out of the box.

    Admin Action:

        The administrator selects vendor Juniper.

        Sets the Feature Key to has_enable_secret.

        Enters the CLI Syntax Pattern plain-text-password.

        Clicks Save Mapping.

    System Result: The backend updates app/mappings.json instantly. From that moment forward, any uploaded file containing plain-text-password will be recognized and parsed accurately into the compliance model without needing a server restart or code redeployment.

but is this asked in problem statement

Yes, this addresses the problem statement directly.

Requirement 2 of the problem statement explicitly mandates an "AI-Powered Training Module: A dedicated, intuitive GUI where administrators can 'train' the system to parse unseen vendor formats by mapping specific command outputs to compliance parameters."

Here is how your implementation directly fulfills the problem statement's vision:

    Unseen Vendor Formats: Devices running newer OS versions or non-standard CLI syntax won't be hardcoded into the initial parser.

    Human-in-the-Loop "Training": Rather than retraining a massive AI model from scratch, the admin uses the intuitive GUI section to map novel commands to internal standardized feature keys (like has_enable_secret or telnet_enabled).

    Rwork configuration compliance auditing using:

 - Configuration parsing
- Vendor normalization
- Security baseline modeling
- Policy-as-code
- Open Policy Agent
- Human-in-the-loop training
- Automated PDF reporting

```

```
