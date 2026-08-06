"""Static reference data for common Windows Event Log IDs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EventEntry:
    event_id: int
    log: str
    source: str
    severity: str
    summary: str
    common_cause: str


EVENTS: tuple[EventEntry, ...] = (
    EventEntry(1074, "System", "USER32", "Info", "System shutdown/restart initiated", "A user or process initiated a shutdown, restart, or logoff."),
    EventEntry(6005, "System", "EventLog", "Info", "The Event log service was started", "Normal system boot; marks the start of a new uptime window."),
    EventEntry(6006, "System", "EventLog", "Info", "The Event log service was stopped", "Normal, clean system shutdown."),
    EventEntry(6008, "System", "EventLog", "Error", "The previous system shutdown was unexpected", "Unexpected shutdown (power loss, crash, or hard reset) -- no clean shutdown event was logged first."),
    EventEntry(6013, "System", "EventLog", "Info", "System uptime report", "Logged periodically with the system's uptime in seconds."),
    EventEntry(41, "System", "Kernel-Power", "Critical", "The system rebooted without cleanly shutting down first", "Power loss, hard reset, hang, or a BSOD before a graceful shutdown could occur."),
    EventEntry(1000, "Application", "Application Error", "Error", "Application crash", "An application (exe) crashed; the faulting module and offset are logged alongside this event."),
    EventEntry(1001, "Application", "Windows Error Reporting", "Info", "Fault bucket / crash report generated", "Follows a 1000 crash event; contains the WER bucket ID used to look up known issues."),
    EventEntry(1002, "Application", "Application Hang", "Error", "Application stopped responding", "An application hung (stopped responding to the message loop) and was reported by WER."),
    EventEntry(4624, "Security", "Microsoft-Windows-Security-Auditing", "Info", "An account was successfully logged on", "Successful interactive, network, RDP, or service logon. Check the Logon Type field for the specific method."),
    EventEntry(4625, "Security", "Microsoft-Windows-Security-Auditing", "Warning", "An account failed to log on", "Bad password, disabled account, or a brute-force/spray attempt against a domain or local account."),
    EventEntry(4634, "Security", "Microsoft-Windows-Security-Auditing", "Info", "An account was logged off", "Normal logoff, paired with the 4624 that started the session."),
    EventEntry(4648, "Security", "Microsoft-Windows-Security-Auditing", "Info", "A logon was attempted using explicit credentials", "A process (e.g. RunAs, scheduled task, or a script) explicitly supplied different credentials than the current session."),
    EventEntry(4672, "Security", "Microsoft-Windows-Security-Auditing", "Info", "Special privileges assigned to new logon", "An account with administrative/sensitive privileges (e.g. SeDebugPrivilege) just logged on."),
    EventEntry(4720, "Security", "Microsoft-Windows-Security-Auditing", "Info", "A user account was created", "New local or domain user account creation -- review who created it and why."),
    EventEntry(4726, "Security", "Microsoft-Windows-Security-Auditing", "Info", "A user account was deleted", "Local or domain user account deletion."),
    EventEntry(4740, "Security", "Microsoft-Windows-Security-Auditing", "Warning", "A user account was locked out", "Too many failed logon attempts triggered an account lockout policy."),
    EventEntry(4767, "Security", "Microsoft-Windows-Security-Auditing", "Info", "A user account was unlocked", "An administrator or self-service reset unlocked a previously locked-out account."),
    EventEntry(4771, "Security", "Microsoft-Windows-Security-Auditing", "Warning", "Kerberos pre-authentication failed", "Usually a bad password against a domain account; the failure code field narrows the cause."),
    EventEntry(4776, "Security", "Microsoft-Windows-Security-Auditing", "Info", "The domain controller attempted to validate credentials (NTLM)", "NTLM authentication attempt against a DC; check the error code for success/failure detail."),
    EventEntry(4104, "Windows PowerShell", "Microsoft-Windows-PowerShell", "Info", "PowerShell script block logged", "Script Block Logging captured a block of executed PowerShell code -- useful for incident investigation."),
    EventEntry(7000, "System", "Service Control Manager", "Error", "A service failed to start", "The named service failed to start at boot or on-demand -- check the service's own log for the underlying cause."),
    EventEntry(7001, "System", "Service Control Manager", "Error", "A service failed to start due to a dependency failure", "A service this one depends on didn't start, so the dependent service couldn't start either."),
    EventEntry(7009, "System", "Service Control Manager", "Error", "A timeout occurred while waiting for a service to connect", "The service did not signal it was running within the expected startup timeout."),
    EventEntry(7011, "System", "Service Control Manager", "Warning", "A timeout occurred while waiting for a transaction response from a service", "The service is unresponsive to a control request (e.g. stop/pause) within the timeout window."),
    EventEntry(7031, "System", "Service Control Manager", "Error", "A service terminated unexpectedly", "The service crashed or exited unexpectedly; the SCM may attempt an automatic restart depending on its recovery settings."),
    EventEntry(7034, "System", "Service Control Manager", "Error", "A service terminated unexpectedly (deprecated form)", "Older equivalent of 7031, seen on some Windows versions."),
    EventEntry(7036, "System", "Service Control Manager", "Info", "A service entered the running or stopped state", "Routine start/stop status change; very high volume, usually filtered out in log review."),
    EventEntry(10016, "System", "DistributedCOM", "Warning", "A DCOM permission error", "An application tried to use DCOM without the required local activation/launch permissions -- usually benign, but noisy."),
    EventEntry(1102, "Security", "Microsoft-Windows-Eventlog", "Warning", "The audit log was cleared", "Someone manually cleared the Security event log -- a common anti-forensics step worth investigating who and why."),
    EventEntry(5140, "Security", "Microsoft-Windows-Security-Auditing", "Info", "A network share object was accessed", "A file share (e.g. an SMB share) was accessed over the network."),
    EventEntry(5145, "Security", "Microsoft-Windows-Security-Auditing", "Info", "A network share object was checked to see whether access is granted", "Detailed per-file share access check, high volume when enabled."),
    EventEntry(4738, "Security", "Microsoft-Windows-Security-Auditing", "Info", "A user account was changed", "An attribute on a domain/local user account was modified (group membership, password policy flags, etc.)."),
    EventEntry(4732, "Security", "Microsoft-Windows-Security-Auditing", "Info", "A member was added to a security-enabled local group", "Local group membership change, e.g. someone was added to local Administrators."),
    EventEntry(4728, "Security", "Microsoft-Windows-Security-Auditing", "Info", "A member was added to a security-enabled global group", "Domain group membership change, e.g. someone was added to Domain Admins."),
    EventEntry(1116, "System", "Microsoft-Windows-Windows Defender", "Warning", "Windows Defender detected malware or other potentially unwanted software", "Real-time protection flagged a threat; check whether remediation (1117) followed."),
    EventEntry(1117, "System", "Microsoft-Windows-Windows Defender", "Info", "Windows Defender took action to protect the system", "Follows a 1116 detection; the action taken (quarantine, remove, allow) is logged in the event detail."),
    EventEntry(4657, "Security", "Microsoft-Windows-Security-Auditing", "Info", "A registry value was modified", "Registry auditing captured a value change -- useful for tracking persistence mechanisms or config drift."),
)


def search_events(query: str) -> tuple[EventEntry, ...]:
    """Filter EVENTS by event ID, log, source, severity, or keyword (case-insensitive substring match)."""
    needle = (query or "").strip().lower()
    if not needle:
        return EVENTS
    return tuple(
        entry
        for entry in EVENTS
        if needle in str(entry.event_id)
        or needle in entry.log.lower()
        or needle in entry.source.lower()
        or needle in entry.severity.lower()
        or needle in entry.summary.lower()
        or needle in entry.common_cause.lower()
    )
