# -*- coding: utf-8 -*-
from enum import Enum

from pydantic import BaseModel


class IOCType(str, Enum):
    # Réseau
    ip_address = "ip_address"  # Exemple: "192.168.1.100", "8.8.8.8"
    domain_name = "domain_name"  # Exemple: "malicious-domain.com"
    url = "url"  # Exemple: "http://evil.example.com/path"
    uri_path = "uri_path"  # Exemple: "/admin/login.php"
    port = "port"  # Exemple: "443", "8080"
    dns_query = "dns_query"  # Exemple: "api.badsite.io"
    token = "token"  # Exemple: "f9403fc5f537b4ab332d"

    # Fichier
    file_name = "file_name"  # Exemple: "invoice.exe", "payload.dll"
    file_path = "file_path"  # Exemple: "C:\\Users\\Public\\malware.exe"
    file_hash_md5 = "file_hash_md5"  # Exemple: "5d41402abc4b2a76b9719d911017c592"
    file_hash_sha1 = (
        "file_hash_sha1"  # Exemple: "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12"
    )
    file_hash_sha256 = "file_hash_sha256"  # Exemple: "3a7bd3e2360a3d29ee5f82d4a8f3bf2f3f5ebf25c6f1b6c1bdc8763b403a9afd"
    file_size = "file_size"  # Exemple: "54321" (en octets)
    file_signature = "file_signature"  # Exemple: "MZ..." (signature binaire)

    # Email
    email_subject = "email_subject"  # Exemple: "Important Invoice Attached"
    email_address_sender = "email_address_sender"  # Exemple: "attacker@phishing.com"
    email_address_recipient = "email_address_recipient"  # Exemple: "victim@company.com"
    email_attachment_name = (
        "email_attachment_name"  # Exemple: "invoice.pdf", "info.scr"
    )

    # Utilisateurs / Comptes
    user_account = "user_account"  # Exemple: "eviladmin", "backupuser01"
    user_password = "user_password"  # Exemple: "P@ssw0rd!", "Welcome123"

    # Système / Host
    registry_key = "registry_key"  # Exemple: "HKEY_LOCAL_MACHINE\\Software\\Malware"
    firewall_rule_name = "firewall_rule_name"  # Exemple: "Malicious Backdoor Port 4444"
    mutex = "mutex"  # Exemple: "Global\\MyMalwareMutex"
    process_name = "process_name"  # Exemple: "evil.exe"
    process_path = "process_path"  # Exemple: "C:\\Windows\\System32\\evil.exe"
    service_name = "service_name"  # Exemple: "malicious_service"
    driver_name = "driver_name"  # Exemple: "bad_driver.sys"
    command_line = "command_line"  # Exemple: "powershell.exe -EncodedCommand ..."
    scheduled_task = (
        "scheduled_task"  # Exemple: "\\Microsoft\\Windows\\Update\\FakeTask"
    )
    pipe_name = "pipe_name"  # Exemple: "\\.\pipe\MalPipe"
    hostname = "hostname"  # Exemple: "infected-host.local"

    # Comportement / Divers
    c2_server = "c2_server"  # Exemple: "c2.evilserver.com"
    malware_family = "malware_family"  # Exemple: "Emotet", "Trickbot"
    threat_actor = "threat_actor"  # Exemple: "APT28", "FIN7"
    exploit = "exploit"  # Exemple: "CVE-2021-34527"
    tls_cert = "tls_cert"  # Exemple: "CN=malicious.com, O=BadCorp, C=RU"
    user_agent = "user_agent"  # Exemple: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
    script_content = "script_content"  # Exemple: "Set-ExecutionPolicy Bypass; IEX (New-Object Net.WebClient)..."
    yara_rule = (
        "yara_rule"  # Exemple: "rule Malware_Match { strings: $a = \"malicious\" ... }"
    )


class Ioc(BaseModel):
    type: IOCType
    value: str
    description_fr: str
    description_en: str
