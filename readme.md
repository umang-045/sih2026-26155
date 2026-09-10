AI-Augmented Multi-Vendor Network Compliance Auditor

An AI-augmented, vendor-agnostic network configuration compliance auditing platform that maps heterogeneous device CLI syntax (Cisco, Juniper, Palo Alto) to standardized security benchmarks such as CIS, DISA STIG, and NIST.

The platform is designed to replace manual, vendor-specific auditing workflows with a unified normalization, policy evaluation, training, and reporting pipeline.

Key Features

Unified Ingestion Engine

Upload and audit single or multiple network configuration files.
Supports .cfg and .txt configuration files.

Vendor-Agnostic Normalization

Detects supported network vendors.
Converts vendor-specific CLI syntax into a standardized JSON Security Baseline Model.

OPA Multi-Framework Compliance Engine

Evaluates normalized configurations using Open Policy Agent.
Uses Rego v1 policies for security frameworks such as CIS and DISA STIG.

AI-Powered Training Module

Human-in-the-loop training interface available at /train.
Administrators can map previously unseen CLI commands to compliance feature keys.
Mapping updates are persisted dynamically without requiring backend code changes or redeployment.

Actionable PDF Reporting

Generates downloadable executive audit reports.
Includes compliance status, risk severity, failed controls, and device-specific CLI remediation commands.
Architecture
                ┌──────────────────────────┐
                │      Web Dashboard       │
                │ HTML + Tailwind + JS     │
                └────────────┬─────────────┘
                             │
                             ▼
                ┌──────────────────────────┐
                │       FastAPI API        │
                │      app/main.py         │
                └────────────┬─────────────┘
                             │
             ┌───────────────┼────────────────┐
             │               │                │
             ▼               ▼                ▼
      ┌─────────────┐ ┌──────────────┐ ┌──────────────┐
      │ Config      │ │ Normalization │ │ PDF Reporting │
      │ Parser      │ │ Engine        │ │ Engine        │
      └──────┬──────┘ └──────┬───────┘ └──────────────┘
             │               │
             │               ▼
             │       ┌─────────────────┐
             │       │ Standardized    │
             │       │ Security Model  │
             │       └────────┬────────┘
             │                │
             │                ▼
             │       ┌─────────────────┐
             │       │ Open Policy     │
             │       │ Agent / Rego    │
             │       └────────┬────────┘
             │                │
             └────────────────┤
                              ▼
                    ┌──────────────────┐
                    │ Compliance       │
                    │ Findings         │
                    └──────────────────┘

Tech Stack
Backend
Python 3.10+
FastAPI
Uvicorn
Pybatfish
ciscoconfparse2
ReportLab
Policy Engine
Open Policy Agent (OPA)
Rego v1
Frontend
HTML5
Tailwind CSS via CDN
Vanilla JavaScript
Data Persistence
JSON-based dynamic mapping store
app/mappings.json
Testing
Pytest
Repository Structure
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

Prerequisites

Before running the project, make sure you have the following installed:

Python 3.10 or higher
Open Policy Agent (OPA)
Git

You can verify Python and OPA with:

python --version
opa version

Installation
1. Clone the Repository

Replace your-username with your GitHub username:

git clone https://github.com/your-username/network-compliance-auditor.git
cd network-compliance-auditor

2. Create a Virtual Environment
Linux / macOS
python3 -m venv venv
source venv/bin/activate

Windows
python -m venv venv
venv\Scripts\activate

3. Install Python Dependencies
pip install --upgrade pip
pip install -r requirements.txt

Running the Application

The application requires both OPA and the FastAPI server to be running.

1. Start OPA

Open a new terminal and run:

opa run --server --addr=0.0.0.0:8181 ./rules


OPA should now be available at:

http://127.0.0.1:8181

2. Start FastAPI

From the project root:

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000


The application should now be available at:

http://127.0.0.1:8000

Web Dashboard

Open the following address in your browser:

http://127.0.0.1:8000


The dashboard provides access to configuration auditing, compliance results, PDF reporting, and dynamic CLI training.

Usage
1. Audit a Device Configuration
Open the web dashboard.
Select Browse.
Upload a configuration file.
Supported examples include:
samples/cisco_switch.cfg
samples/juniper_router.cfg

Click Audit File.

The application processes the configuration through the normalization and policy evaluation pipeline.

The resulting dashboard displays information such as:

Device vendor
Device metadata
Compliance status
Failed controls
Risk severity
Remediation recommendations

Possible compliance states include:

COMPLIANT
NON_COMPLIANT

2. Generate a PDF Report

After completing an audit:

Click Download PDF Report.
The backend generates a PDF using ReportLab.
The report contains the audit results and remediation information.

The report is intended to provide both technical and executive-level visibility into configuration compliance.

3. Train New CLI Patterns

The application includes a human-in-the-loop training workflow.

Navigate to the Dynamic AI Training Loop section of the dashboard.

For example:

Vendor:
Juniper

Feature Key:
has_enable_secret

CLI Pattern:
plain-text-password


After clicking Save Mapping, the mapping is persisted to:

app/mappings.json


This allows administrators to extend CLI recognition rules without modifying the parser source code or redeploying the application.

API Endpoints
Endpoint	Method	Description
/	GET	Serves the web dashboard
/audit	POST	Uploads and audits a network configuration
/audit/pdf	POST	Generates and downloads a PDF audit report
/train	POST	Adds a new CLI-to-feature mapping
Example API Usage
Audit Configuration
curl -X POST \
  http://127.0.0.1:8000/audit \
  -F "file=@samples/cisco_switch.cfg"

Generate PDF Report
curl -X POST \
  http://127.0.0.1:8000/audit/pdf \
  -F "file=@samples/cisco_switch.cfg" \
  --output audit_report.pdf

Add a Training Mapping
curl -X POST \
  http://127.0.0.1:8000/train \
  -H "Content-Type: application/json" \
  -d '{
    "vendor": "Juniper",
    "feature_key": "has_enable_secret",
    "cli_pattern": "plain-text-password"
  }'

Running Tests

Run the complete test suite with:

pytest tests/


For more detailed output:

pytest tests/ -v

Supported Vendors

The normalization engine is designed around multi-vendor network configuration analysis.

Current target vendors include:

Cisco
Juniper
Palo Alto

The architecture is intended to allow additional vendors to be added through parser logic and dynamic mappings.

Compliance Frameworks

The policy engine is designed to support standardized security frameworks, including:

CIS Benchmarks
DISA STIG
NIST security guidance

Compliance rules are maintained as Rego policies under:

rules/compliance.rego

Configuration Flow

A typical audit follows this pipeline:

Network Configuration
        │
        ▼
Vendor Detection
        │
        ▼
CLI Parsing
        │
        ▼
Feature Extraction
        │
        ▼
Normalized Security Model
        │
        ▼
OPA / Rego Evaluation
        │
        ▼
Compliance Findings
        │
        ├───────────────┐
        ▼               ▼
Web Dashboard      PDF Report

Dynamic Training Flow

Unrecognized CLI syntax can be incorporated through the training workflow:

Unknown CLI Command
        │
        ▼
Administrator Review
        │
        ▼
Vendor + Feature Key
        │
        ▼
CLI Pattern Mapping
        │
        ▼
app/mappings.json
        │
        ▼
Future Audits

Security Considerations

This project is intended for authorized network security and configuration auditing.

When deploying in a production environment, consider:

Authentication and authorization
Secure file upload validation
File size limits
Input sanitization
HTTPS/TLS
Secure OPA configuration
Access control for training mappings
Protection of uploaded network configurations
Audit logging
Secure storage instead of JSON-based persistence for multi-user deployments

Network configuration files may contain sensitive information such as IP addresses, usernames, SNMP communities, routing information, or encrypted credentials. Treat uploaded configurations as sensitive data.

Development

Start FastAPI in development mode with automatic reload:

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000


Run tests:

pytest tests/ -v

Production Considerations

For production deployments, the development configuration should be hardened.

Recommended improvements include:

Use a production ASGI deployment strategy.
Run behind a reverse proxy.
Enable HTTPS.
Add authentication.
Replace mappings.json with a database.
Add structured application logging.
Containerize the application.
Restrict OPA network access.
Implement upload validation and malware scanning.
Store reports and configuration files securely.
Add CI/CD testing.
Roadmap

Potential future improvements include:

 Support for additional network vendors
 Expanded CIS benchmark coverage
 Additional DISA STIG controls
 NIST control mapping
 Role-based access control
 User authentication
 Database-backed training mappings
 Configuration version history
 Audit history dashboard
 Docker deployment
 CI/CD pipeline
 Scheduled configuration audits
 Multi-device bulk auditing
 Advanced AI-assisted CLI classification
 SIEM integration
 REST API authentication
 Enterprise reporting
Contributing

Contributions are welcome.

1. Fork the Repository

Create your own fork of the project on GitHub.

2. Create a Feature Branch
git checkout -b feature/your-feature

3. Make Your Changes

Implement and test your changes.

4. Run Tests
pytest tests/ -v

5. Commit Your Changes
git add .
git commit -m "Add your feature"

6. Push the Branch
git push origin feature/your-feature


Then open a Pull Request on GitHub.

License

Add your preferred license here.

For example:

MIT License


If this repository is intended for public distribution, add a LICENSE file to the repository as well.

Author

Your Name

GitHub: https://github.com/your-username

Project Status

Status: Active Development

This project is intended to provide a foundation for automated, vendor-agnostic network configuration compliance auditing using configuration normalization, policy-as-code, and human-in-the-loop learning.
