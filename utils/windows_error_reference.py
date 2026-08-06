"""Static reference data for common Windows/Win32 error codes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorEntry:
    code: int
    hex_code: str
    category: str
    name: str
    description: str


def _entry(code: int, category: str, name: str, description: str) -> ErrorEntry:
    return ErrorEntry(code, f"0x{code & 0xFFFFFFFF:08X}", category, name, description)


ERRORS: tuple[ErrorEntry, ...] = (
    _entry(0, "Win32", "ERROR_SUCCESS", "The operation completed successfully."),
    _entry(1, "Win32", "ERROR_INVALID_FUNCTION", "Incorrect function -- the requested operation isn't supported by the target."),
    _entry(2, "Win32", "ERROR_FILE_NOT_FOUND", "The system cannot find the file specified."),
    _entry(3, "Win32", "ERROR_PATH_NOT_FOUND", "The system cannot find the path specified."),
    _entry(5, "Win32", "ERROR_ACCESS_DENIED", "Access is denied -- permissions or a locked/in-use resource."),
    _entry(6, "Win32", "ERROR_INVALID_HANDLE", "The handle is invalid -- often a use-after-close bug in the calling application."),
    _entry(8, "Win32", "ERROR_NOT_ENOUGH_MEMORY", "Not enough storage is available to process this command."),
    _entry(14, "Win32", "ERROR_OUTOFMEMORY", "Not enough storage is available to complete this operation."),
    _entry(15, "Win32", "ERROR_INVALID_DRIVE", "The system cannot find the drive specified."),
    _entry(19, "Win32", "ERROR_WRITE_PROTECT", "The media is write protected."),
    _entry(21, "Win32", "ERROR_NOT_READY", "The device is not ready -- common for removable/network drives."),
    _entry(32, "Win32", "ERROR_SHARING_VIOLATION", "The process cannot access the file because it is being used by another process."),
    _entry(33, "Win32", "ERROR_LOCK_VIOLATION", "The process cannot access the file because another process has locked a portion of the file."),
    _entry(50, "Win32", "ERROR_NOT_SUPPORTED", "The network request is not supported."),
    _entry(53, "Win32", "ERROR_BAD_NETPATH", "The network path was not found."),
    _entry(64, "Win32", "ERROR_NETNAME_DELETED", "The specified network name is no longer available -- a session was dropped mid-operation."),
    _entry(65, "Win32", "ERROR_NETWORK_ACCESS_DENIED", "Network access is denied."),
    _entry(67, "Win32", "ERROR_BAD_NET_NAME", "The network name cannot be found -- check the share/UNC path."),
    _entry(80, "Win32", "ERROR_FILE_EXISTS", "The file exists."),
    _entry(87, "Win32", "ERROR_INVALID_PARAMETER", "The parameter is incorrect -- a very common generic API misuse error."),
    _entry(112, "Win32", "ERROR_DISK_FULL", "There is not enough space on the disk."),
    _entry(122, "Win32", "ERROR_INSUFFICIENT_BUFFER", "The data area passed to a system call is too small."),
    _entry(123, "Win32", "ERROR_INVALID_NAME", "The filename, directory name, or volume label syntax is incorrect."),
    _entry(126, "Win32", "ERROR_MOD_NOT_FOUND", "The specified module could not be found -- a missing DLL dependency."),
    _entry(127, "Win32", "ERROR_PROC_NOT_FOUND", "The specified procedure could not be found -- a DLL version mismatch."),
    _entry(183, "Win32", "ERROR_ALREADY_EXISTS", "Cannot create a file when that file already exists."),
    _entry(206, "Win32", "ERROR_FILENAME_EXCED_RANGE", "The filename or extension is too long."),
    _entry(232, "Win32", "ERROR_NO_DATA", "The pipe is being closed."),
    _entry(998, "Win32", "ERROR_NOACCESS", "Invalid access to a memory location -- an application-level access violation."),
    _entry(1053, "Service Control", "ERROR_SERVICE_REQUEST_TIMEOUT", "The service did not respond to the start or control request in a timely fashion."),
    _entry(1058, "Service Control", "ERROR_SERVICE_DISABLED", "The service cannot be started, either because it is disabled or because it has no enabled devices associated with it."),
    _entry(1060, "Service Control", "ERROR_SERVICE_DOES_NOT_EXIST", "The specified service does not exist as an installed service."),
    _entry(1068, "Service Control", "ERROR_SERVICE_DEPENDENCY_FAIL", "The dependency service or group failed to start."),
    _entry(1069, "Service Control", "ERROR_SERVICE_LOGON_FAILED", "The service did not start due to a logon failure -- check the service account credentials."),
    _entry(1075, "Service Control", "ERROR_SERVICE_DEPENDENCY_DELETED", "The dependency service does not exist or has been marked for deletion."),
    _entry(1219, "Win32", "ERROR_SESSION_CREDENTIAL_CONFLICT", "Multiple connections to a server or shared resource by the same user, using more than one credential, are not allowed -- classic SMB double-credential conflict."),
    _entry(1326, "Win32", "ERROR_LOGON_FAILURE", "Logon failure: unknown user name or bad password."),
    _entry(1327, "Win32", "ERROR_ACCOUNT_RESTRICTION", "Logon failure: user account restriction (e.g. blank passwords not allowed, logon hour restriction, or policy restriction)."),
    _entry(1330, "Win32", "ERROR_PASSWORD_EXPIRED", "Logon failure: the user's password has expired."),
    _entry(1331, "Win32", "ERROR_ACCOUNT_DISABLED", "Logon failure: the account is currently disabled."),
    _entry(1332, "Win32", "ERROR_NONE_MAPPED", "No mapping between account names and security IDs was done -- often a stale/orphaned SID."),
    _entry(1385, "Win32", "ERROR_LOGON_NOT_GRANTED", "Logon failure: the user has not been granted the requested logon type at this computer."),
    _entry(1722, "RPC", "RPC_S_SERVER_UNAVAILABLE", "The RPC server is unavailable -- often DNS, firewall, or the target service being down."),
    _entry(1723, "RPC", "RPC_S_SERVER_TOO_BUSY", "The RPC server is too busy to complete this operation."),
    _entry(1726, "RPC", "RPC_S_CALL_FAILED", "The remote procedure call failed."),
    _entry(1753, "RPC", "EPT_S_NOT_REGISTERED", "There are no more endpoints available from the endpoint mapper."),
    _entry(1789, "Win32", "ERROR_TRUST_FAILURE", "The trust relationship between the workstation and the primary domain failed -- classic \"reset the computer account\" symptom."),
    _entry(1790, "Win32", "ERROR_TRUSTED_DOMAIN_FAILURE", "The trust relationship between this workstation and the primary domain failed."),
    _entry(1792, "Win32", "ERROR_TRUST_FAILURE", "The network logon failed -- domain controller unreachable or trust broken."),
    _entry(1808, "Win32", "ERROR_NO_TRUST_LSA_SECRET", "The workstation does not have a trust secret."),
    _entry(1909, "Win32", "ERROR_ACCOUNT_LOCKED_OUT", "The referenced account is currently locked out and may not be logged on to."),
    _entry(31, "Win32", "ERROR_GEN_FAILURE", "A device attached to the system is not functioning."),
    _entry(1450, "Win32", "ERROR_NO_SYSTEM_RESOURCES", "Insufficient system resources exist to complete the requested service -- often too many open handles/non-paged pool exhaustion."),
    _entry(0x80070005, "HRESULT", "E_ACCESSDENIED", "General access denied HRESULT, commonly surfaced by Windows Update, MSI installers, and COM/OLE operations."),
    _entry(0x8007000E, "HRESULT", "E_OUTOFMEMORY", "Out of memory or resources, wrapped as an HRESULT (common in MSI/COM failures)."),
    _entry(0x80070490, "HRESULT", "ERROR_NOT_FOUND (HRESULT)", "Element not found -- common Windows Update / servicing stack corruption symptom."),
    _entry(0x800706BA, "HRESULT", "RPC_S_SERVER_UNAVAILABLE (HRESULT)", "The RPC server is unavailable, wrapped as an HRESULT (WMI/DCOM connectivity failures)."),
    _entry(0xC0000005, "NTSTATUS", "STATUS_ACCESS_VIOLATION", "The instruction referenced memory it doesn't have access to -- the underlying cause of most application crash/BSOD reports."),
    _entry(0xC000021A, "NTSTATUS", "STATUS_SYSTEM_PROCESS_TERMINATED", "A critical system process terminated unexpectedly -- typically precedes an automatic reboot (matches Kernel-Power Event 41)."),
    _entry(0xC0000034, "NTSTATUS", "STATUS_OBJECT_NAME_NOT_FOUND", "The object name was not found -- common boot-configuration/BCD corruption symptom."),
    _entry(0xC0000135, "NTSTATUS", "STATUS_DLL_NOT_FOUND", "A required DLL could not be found -- application won't start, missing runtime dependency."),
    _entry(0xC0000221, "NTSTATUS", "STATUS_IMAGE_CHECKSUM_MISMATCH", "The image checksum does not match -- corrupted executable/DLL, often disk or RAM failure."),
)


def search_errors(query: str) -> tuple[ErrorEntry, ...]:
    """Filter ERRORS by decimal code, hex code, category, name, or keyword (case-insensitive)."""
    needle = (query or "").strip().lower()
    if not needle:
        return ERRORS
    return tuple(
        entry
        for entry in ERRORS
        if needle in str(entry.code)
        or needle in entry.hex_code.lower()
        or needle in entry.category.lower()
        or needle in entry.name.lower()
        or needle in entry.description.lower()
    )
