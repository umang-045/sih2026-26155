import os
import re
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
    elif "set deviceconfig" in text or "panning" in text or "panorama" in text:
        return "paloalto"
    return "cisco"

def extract_normalized_features(file_bytes: bytes, filename: str) -> dict:
    raw_text = file_bytes.decode("utf-8", errors="ignore")
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    vendor = detect_vendor(raw_text)
    custom_mappings = load_mappings().get(vendor, {})

    baseline = {
        "hostname": filename,
        "vendor": vendor,
        "has_enable_secret": False,
        "telnet_enabled": False,
        "ntp_servers": [],
        "unmapped_lines": []
    }

    def check_dynamic_pattern(key: str) -> bool:
        patterns = custom_mappings.get(key, [])
        return any(p.lower() in raw_text.lower() for p in patterns)

    if vendor == "cisco":
        # Pass list of lines directly to CiscoConfParse
        parse = CiscoConfParse(lines)
        
        # 1. Enable Secret Detection
        baseline["has_enable_secret"] = len(parse.find_objects(r"^enable secret")) > 0 or check_dynamic_pattern("has_enable_secret")
        
        # 2. Telnet Check
        vty_lines = parse.find_objects(r"^line vty")
        for line in vty_lines:
            for child in line.children:
                child_text = child.text.lower()
                if "transport input telnet" in child_text or "transport input all" in child_text:
                    baseline["telnet_enabled"] = True
        if check_dynamic_pattern("telnet_enabled"):
            baseline["telnet_enabled"] = True

        # 3. Hostname Check
        hostname_objs = parse.find_objects(r"^hostname\s+")
        if hostname_objs:
            baseline["hostname"] = hostname_objs[0].text.split()[-1]

        # 4. NTP Server Extraction with Batfish + Native Regex Fallback
        ntp_found = []
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                config_dir = os.path.join(tmpdir, "configs")
                os.makedirs(config_dir, exist_ok=True)
                file_path = os.path.join(config_dir, filename)
                with open(file_path, "wb") as f:
                    f.write(file_bytes)

                bf = Session(host="localhost", port=9996)
                bf.set_network("audit_network")
                bf.init_snapshot(tmpdir, name="snapshot", overwrite=True)
                node_df = bf.q.nodeProperties().answer().frame()
                if not node_df.empty:
                    row = node_df.iloc[0]
                    ntp_found = list(row.get("NTP_Servers", []))
        except Exception:
            pass

        # Regex fallback if Batfish isn't running
        if not ntp_found:
            ntp_matches = parse.find_objects(r"^ntp server\s+")
            for obj in ntp_matches:
                parts = obj.text.split()
                if len(parts) >= 3:
                    ntp_found.append(parts[2])

        baseline["ntp_servers"] = ntp_found

    else:
        # Generic Parser for Non-Cisco Vendors (Juniper, Palo Alto)
        for line_str in lines:
            if line_str.startswith("#") or line_str.startswith("/*") or line_str.startswith("!"):
                continue

            # Hostname regex match
            if re.search(r"(host-name|hostname)\s+", line_str, re.IGNORECASE):
                parts = line_str.split()
                if len(parts) >= 2:
                    baseline["hostname"] = parts[-1].rstrip(";")

            # NTP Server regex match
            if re.search(r"ntp-?server\s+", line_str, re.IGNORECASE):
                parts = line_str.split()
                if len(parts) >= 2:
                    baseline["ntp_servers"].append(parts[-1].rstrip(";"))

        baseline["has_enable_secret"] = check_dynamic_pattern("has_enable_secret")
        
        # Strict enable check for non-cisco telnet
        has_telnet_service = any(
            re.search(r"set system services telnet", l, re.IGNORECASE) or 
            re.search(r"enable.*telnet", l, re.IGNORECASE) for l in lines
        )
        baseline["telnet_enabled"] = has_telnet_service or check_dynamic_pattern("telnet_enabled")

    # Unmapped line flagging
    sensitive_keywords = ["password", "secret", "auth", "transport", "crypto", "snmp"]
    for line_clean in lines:
        if line_clean.startswith("!") or line_clean.startswith("#"):
            continue
        if any(kw in line_clean.lower() for kw in sensitive_keywords):
            if not any(mapped in line_clean.lower() for key in custom_mappings for mapped in custom_mappings[key]):
                baseline["unmapped_lines"].append(line_clean)

    baseline["unmapped_lines"] = list(set(baseline["unmapped_lines"]))[:10]
    return baseline