"""Static reference data for common network ports and protocols."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PortEntry:
    port: int
    protocol: str
    name: str
    description: str


PORTS: tuple[PortEntry, ...] = (
    PortEntry(20, "TCP", "FTP (data)", "File Transfer Protocol data channel."),
    PortEntry(21, "TCP", "FTP (control)", "File Transfer Protocol control/command channel."),
    PortEntry(22, "TCP", "SSH / SFTP", "Secure Shell remote login and secure file transfer."),
    PortEntry(23, "TCP", "Telnet", "Unencrypted remote login. Avoid on untrusted networks."),
    PortEntry(25, "TCP", "SMTP", "Mail transfer between mail servers."),
    PortEntry(53, "TCP/UDP", "DNS", "Domain Name System queries and zone transfers."),
    PortEntry(67, "UDP", "DHCP (server)", "Dynamic Host Configuration Protocol, server side."),
    PortEntry(68, "UDP", "DHCP (client)", "Dynamic Host Configuration Protocol, client side."),
    PortEntry(69, "UDP", "TFTP", "Trivial File Transfer Protocol, often used for network boot."),
    PortEntry(80, "TCP", "HTTP", "Unencrypted web traffic."),
    PortEntry(110, "TCP", "POP3", "Post Office Protocol v3 mail retrieval."),
    PortEntry(111, "TCP/UDP", "RPCbind", "Remote procedure call port mapper (NFS and friends)."),
    PortEntry(119, "TCP", "NNTP", "Network News Transfer Protocol (Usenet)."),
    PortEntry(123, "UDP", "NTP", "Network Time Protocol synchronization."),
    PortEntry(135, "TCP", "MS RPC", "Microsoft RPC endpoint mapper."),
    PortEntry(137, "UDP", "NetBIOS Name Service", "Windows NetBIOS name resolution."),
    PortEntry(139, "TCP", "NetBIOS Session", "Windows NetBIOS session service (legacy SMB)."),
    PortEntry(143, "TCP", "IMAP", "Internet Message Access Protocol mail retrieval."),
    PortEntry(161, "UDP", "SNMP", "Simple Network Management Protocol polling."),
    PortEntry(162, "UDP", "SNMP Trap", "SNMP trap/notification receiver."),
    PortEntry(179, "TCP", "BGP", "Border Gateway Protocol routing."),
    PortEntry(389, "TCP/UDP", "LDAP", "Lightweight Directory Access Protocol."),
    PortEntry(443, "TCP", "HTTPS", "TLS-encrypted web traffic."),
    PortEntry(445, "TCP", "SMB", "Server Message Block file/printer sharing."),
    PortEntry(464, "TCP/UDP", "Kerberos (change/set password)", "Kerberos password change service."),
    PortEntry(465, "TCP", "SMTPS", "SMTP over implicit TLS."),
    PortEntry(500, "UDP", "IKE / IPsec", "Internet Key Exchange for IPsec VPN negotiation."),
    PortEntry(514, "UDP", "Syslog", "Unencrypted syslog message forwarding."),
    PortEntry(515, "TCP", "LPD", "Line Printer Daemon protocol."),
    PortEntry(587, "TCP", "SMTP (submission)", "Authenticated mail submission from clients."),
    PortEntry(636, "TCP", "LDAPS", "LDAP over TLS."),
    PortEntry(853, "TCP/UDP", "DNS over TLS", "Encrypted DNS resolution (DoT)."),
    PortEntry(873, "TCP", "rsync", "rsync file synchronization daemon."),
    PortEntry(902, "TCP", "VMware Server", "VMware ESXi/vCenter host agent."),
    PortEntry(989, "TCP", "FTPS (data)", "FTP data channel over implicit TLS."),
    PortEntry(990, "TCP", "FTPS (control)", "FTP control channel over implicit TLS."),
    PortEntry(993, "TCP", "IMAPS", "IMAP over TLS."),
    PortEntry(995, "TCP", "POP3S", "POP3 over TLS."),
    PortEntry(1433, "TCP", "Microsoft SQL Server", "MSSQL database default port."),
    PortEntry(1521, "TCP", "Oracle DB", "Oracle database listener default port."),
    PortEntry(1723, "TCP", "PPTP", "Point-to-Point Tunneling Protocol VPN control."),
    PortEntry(1812, "UDP", "RADIUS (auth)", "RADIUS authentication."),
    PortEntry(1813, "UDP", "RADIUS (accounting)", "RADIUS accounting."),
    PortEntry(2049, "TCP/UDP", "NFS", "Network File System."),
    PortEntry(2181, "TCP", "ZooKeeper", "Apache ZooKeeper client port."),
    PortEntry(2375, "TCP", "Docker (unencrypted)", "Docker daemon API without TLS. Do not expose publicly."),
    PortEntry(2376, "TCP", "Docker (TLS)", "Docker daemon API with TLS."),
    PortEntry(3268, "TCP", "Global Catalog", "Active Directory Global Catalog (LDAP)."),
    PortEntry(3269, "TCP", "Global Catalog (TLS)", "Active Directory Global Catalog over TLS."),
    PortEntry(3306, "TCP", "MySQL / MariaDB", "MySQL/MariaDB database default port."),
    PortEntry(3389, "TCP/UDP", "RDP", "Windows Remote Desktop Protocol."),
    PortEntry(5060, "TCP/UDP", "SIP", "Session Initiation Protocol signaling (unencrypted)."),
    PortEntry(5061, "TCP", "SIP (TLS)", "SIP signaling over TLS."),
    PortEntry(5432, "TCP", "PostgreSQL", "PostgreSQL database default port."),
    PortEntry(5601, "TCP", "Kibana", "Kibana web UI default port."),
    PortEntry(5900, "TCP", "VNC", "Virtual Network Computing remote desktop."),
    PortEntry(5985, "TCP", "WinRM (HTTP)", "Windows Remote Management over HTTP."),
    PortEntry(5986, "TCP", "WinRM (HTTPS)", "Windows Remote Management over HTTPS."),
    PortEntry(6379, "TCP", "Redis", "Redis in-memory data store default port."),
    PortEntry(6443, "TCP", "Kubernetes API", "Kubernetes API server default port."),
    PortEntry(8080, "TCP", "HTTP (alt)", "Common alternate HTTP port for proxies and app servers."),
    PortEntry(8443, "TCP", "HTTPS (alt)", "Common alternate HTTPS port."),
    PortEntry(9092, "TCP", "Kafka", "Apache Kafka broker default port."),
    PortEntry(9200, "TCP", "Elasticsearch (HTTP)", "Elasticsearch REST API default port."),
    PortEntry(9300, "TCP", "Elasticsearch (transport)", "Elasticsearch node-to-node transport port."),
    PortEntry(11211, "TCP/UDP", "Memcached", "Memcached default port."),
    PortEntry(27017, "TCP", "MongoDB", "MongoDB database default port."),
)


def search_ports(query: str) -> tuple[PortEntry, ...]:
    """Filter PORTS by port number, protocol, name, or description (case-insensitive substring match)."""
    needle = (query or "").strip().lower()
    if not needle:
        return PORTS
    return tuple(
        entry
        for entry in PORTS
        if needle in str(entry.port)
        or needle in entry.protocol.lower()
        or needle in entry.name.lower()
        or needle in entry.description.lower()
    )
