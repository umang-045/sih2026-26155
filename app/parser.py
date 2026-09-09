import os
import json
import tempfile
from pybatfish.client.session import Session
from ciscoconfparse2 import CiscoConfParse

MAPPINGS_FILE = os.path.join(os.path.dirname(__file__), "mappings.json")

def load_mappings():
    if os.path.exists(MAPPINGS_FILE):
        with open(MAPPINGS_FILE, "r") as f:
            return json.load(f)
    return {"cisco": {}, "juniper": {}, "paloalto": {}}

def save_mapping(vendor: str, feature_key: str, cli_pattern: str):
    mappings = load_mappings()
    if vendor not in mappings:
        mappings[vendor] = {}
    if feature_key not in mappings[vendor]:
        mappings[vendor][feature_key] = []
    if cli_pattern not in mappings[vendor][feature_key]:
        mappings[vendor][feature_key].append(cli_pattern)
    with open(MAPPINGS_FILE, "w") as f:
        json.dump(mappings, f, indent=2)

def detect_vendor(raw_text: str) -> str:
    text = raw_text.lower()
    if "set system" in text or "junos" in text:
        return "juniper"
    elif "set deviceconfig" in text or "panning" in text:
        return "paloalto"
    return "cisco"

def extract_normalized_features(file_bytes: bytes, filename: str) -> dict:
    raw_text = file_bytes.decode("utf-8", errors="ignore")
    vendor = detect_vendor(raw_text)
    custom_mappings = load_mappings().get(vendor, {})

    # Default Normalized Baseline Model
    baseline = {
        "hostname": filename,
        "vendor": vendor,
        "has_enable_secret": False,
        "telnet_enabled": False,
        "ntp_servers": [],
        "unmapped_lines": []
    }

    # Helper function to evaluate dynamic user mappings
    def check_dynamic_pattern(key: str) -> bool:
        patterns = custom_mappings.get(key, [])
        return any(p.lower() in raw_text.lower() for p in patterns)

    if vendor == "cisco":
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = os.path.join(tmpdir, "configs")
            os.makedirs(config_dir, exist_ok=True)
            file_path = os.path.join(config_dir, filename)
            
            with open(file_path, "wb") as f:
                f.write(file_bytes)

            parse = CiscoConfParse(file_path)
            baseline["has_enable_secret"] = len(parse.find_objects(r"^enable secret")) > 0 or check_dynamic_pattern("has_enable_secret")
            
            vty_lines = parse.find_objects(r"^line vty")
            for line in vty_lines:
                for child in line.children:
                    if "transport input telnet" in child.text or "transport input all" in child.text:
                        baseline["telnet_enabled"] = True
            if check_dynamic_pattern("telnet_enabled"):
                baseline["telnet_enabled"] = True

            hostname_objs = parse.find_objects(r"^hostname\s+")
            if hostname_objs:
                baseline["hostname"] = hostname_objs[0].text.split()[-1]

            try:
                bf = Session(host="localhost", port=9996)
                bf.set_network("audit_network")
                bf.init_snapshot(tmpdir, name="snapshot", overwrite=True)
                node_df = bf.q.nodeProperties().answer().frame()
                if not node_df.empty:
                    row = node_df.iloc[0]
                    baseline["ntp_servers"] = list(row.get("NTP_Servers", []))
            except Exception:
                pass

    else:
        # Generic NLP / Pattern Parser for Non-Cisco Vendors (Juniper, Palo Alto, etc.)
        for line in raw_text.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#") or line_str.startswith("/*"):
                continue

            if "host-name" in line_str or "hostname" in line_str:
                parts = line_str.split()
                if len(parts) >= 2:
                    baseline["hostname"] = parts[-1].strip(";")

            if "ntp server" in line_str or "ntp-server" in line_str:
                parts = line_str.split()
                baseline["ntp_servers"].append(parts[-1].strip(";"))

        baseline["has_enable_secret"] = check_dynamic_pattern("has_enable_secret")
        baseline["telnet_enabled"] = ("telnet" in raw_text.lower()) or check_dynamic_pattern("telnet_enabled")

    # Flag unmapped commands containing security-sensitive keywords
    sensitive_keywords = ["password", "secret", "auth", "transport", "crypto", "snmp"]
    for line in raw_text.splitlines():
        line_clean = line.strip()
        if any(kw in line_clean.lower() for kw in sensitive_keywords):
            if not any(mapped in line_clean.lower() for key in custom_mappings for mapped in custom_mappings[key]):
                baseline["unmapped_lines"].append(line_clean)

    # Deduplicate unmapped lines
    baseline["unmapped_lines"] = list(set(baseline["unmapped_lines"]))[:10]
    return baseline