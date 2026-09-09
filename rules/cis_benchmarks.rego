package network.compliance

default allow := true

# CIS Cisco 1.1.1: Ensure 'enable secret' is configured
deny contains res if {
    input.has_enable_secret == false
    res := {
        "rule_id": "CIS-1.1.1",
        "severity": "High",
        "title": "Enable Secret Missing",
        "remediation": "Set an encrypted enable secret using 'enable secret <password>'."
    }
}

# DISA STIG V-220641: Ensure Telnet service is disabled
deny contains res if {
    input.telnet_enabled == true
    res := {
        "rule_id": "STIG-V-220641",
        "severity": "High",
        "title": "Telnet Service Active",
        "remediation": "Disable Telnet and enforce SSH on all VTY lines."
    }
}

# CIS Cisco 1.1.4: Require at least one NTP server configured
deny contains res if {
    count(input.ntp_servers) == 0
    res := {
        "rule_id": "CIS-1.1.4",
        "severity": "Medium",
        "title": "No NTP Server Configured",
        "remediation": "Configure a secure clock source via 'ntp server <ip>'."
    }
}