"""Static reference data mapping Microsoft 365 license SKU strings to product names.

Values verified directly against Microsoft's official "Product names and
service plan identifiers for licensing" CSV
(https://learn.microsoft.com/en-us/entra/identity/users/licensing-service-plan-reference)
as of 2026-08-06, not reconstructed from memory. Not exhaustive -- that
source lists thousands of rows (including retired/regional/add-on SKUs)
and changes over time; this covers the SKUs most commonly seen in MSP
tenant license audits.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SkuEntry:
    sku_string: str
    guid: str
    product_name: str


SKUS: tuple[SkuEntry, ...] = (
    SkuEntry("O365_BUSINESS_ESSENTIALS", "3b555118-da6a-4418-894f-7df1e2096870", "Microsoft 365 Business Basic"),
    SkuEntry("O365_BUSINESS_PREMIUM", "f245ecc8-75af-4f8e-b61f-27d8114de5f3", "Microsoft 365 Business Standard"),
    SkuEntry("SPB", "cbdc14ab-d96c-4c30-b9f4-6ada7cdc1d46", "Microsoft 365 Business Premium"),
    SkuEntry("SPE_E3", "05e9a617-0261-4cee-bb44-138d3ef5d965", "Microsoft 365 E3"),
    SkuEntry("SPE_E5", "06ebc4ee-1bb5-47dd-8120-11324bc54e06", "Microsoft 365 E5"),
    SkuEntry("SPE_F1", "66b55226-6b4f-492c-910c-a3b7a3c9d993", "Microsoft 365 F3"),
    SkuEntry("ENTERPRISEPACK", "6fd2c87f-b296-42f0-b197-1e91e994b900", "Office 365 E3"),
    SkuEntry("ENTERPRISEPREMIUM", "c7df2760-2c81-4ef7-b578-5b5392b571df", "Office 365 E5"),
    SkuEntry("STANDARDPACK", "18181a46-0d4e-45cd-891e-60aabd171b4e", "Office 365 E1"),
    SkuEntry("DESKLESSPACK", "4b585984-651b-448a-9e53-3b10f069cf7f", "Office 365 F3"),
    SkuEntry("EXCHANGESTANDARD", "4b9405b0-7788-4568-add1-99614e613b69", "Exchange Online (Plan 1)"),
    SkuEntry("EXCHANGEENTERPRISE", "19ec0d23-8335-4cbd-94ac-6050e30712fa", "Exchange Online (Plan 2)"),
    SkuEntry("EXCHANGEARCHIVE_ADDON", "ee02fd1b-340e-4a4b-b355-4a514e4c8943", "Exchange Online Archiving for Exchange Online"),
    SkuEntry("EXCHANGEDESKLESS", "80b2d799-d2ba-4d2a-8842-fb0d0f3a4b82", "Exchange Online Kiosk"),
    SkuEntry("SHAREPOINTSTANDARD", "1fc08a02-8b3d-43b9-831e-f76859e04e1a", "SharePoint Online (Plan 1)"),
    SkuEntry("SHAREPOINTENTERPRISE", "a9732ec9-17d9-494c-a51c-d6b45b384dcb", "SharePoint Online (Plan 2)"),
    SkuEntry("MCOSTANDARD", "d42c793f-6c78-4f43-92ca-e8f6a02b035f", "Skype for Business Online (Plan 2)"),
    SkuEntry("MCOMEETADV", "0c266dff-15dd-4b49-8397-2bb16070ed52", "Microsoft 365 Audio Conferencing"),
    SkuEntry("MCOEV", "e43b5b99-8dfb-405f-9987-dc307f34bcbd", "Microsoft Teams Phone Standard"),
    SkuEntry("POWER_BI_STANDARD", "a403ebcc-fae0-4ca2-8c8c-7a907fd6c235", "Microsoft Fabric (Free)"),
    SkuEntry("POWER_BI_PRO", "f8a1db68-be16-40ed-86d5-cb42ce701560", "Power BI Pro"),
    SkuEntry("FLOW_FREE", "f30db892-07e9-47e9-837c-80727f46fd3d", "Microsoft Power Automate Free"),
    SkuEntry("POWERAPPS_VIRAL", "dcb1a3ae-b33f-4487-846a-a640262fadf4", "Microsoft Power Apps Plan 2 Trial"),
    SkuEntry("PROJECTPREMIUM", "09015f9f-377f-4538-bbb5-f75ceb09358a", "Project Online Premium"),
    SkuEntry("PROJECTPROFESSIONAL", "53818b1b-4a27-454b-8896-0dba576410e6", "Planner and Project Plan 3"),
    SkuEntry("PROJECTESSENTIALS", "776df282-9fc0-4862-99e2-70e561b9909e", "Project Online Essentials"),
    SkuEntry("VISIOCLIENT", "c5928f49-12ba-48f7-ada3-0d743a3601d5", "Visio Plan 2"),
    SkuEntry("VISIOONLINE_PLAN1", "4b244418-9658-4451-a2b8-b5e2b364e9bd", "Visio Plan 1"),
    SkuEntry("EMS", "efccb6f7-5641-4e0e-bd10-b4976e1bf68e", "Enterprise Mobility + Security E3"),
    SkuEntry("EMSPREMIUM", "b05e124f-c7cc-45a0-a6aa-8cf78c946968", "Enterprise Mobility + Security E5"),
    SkuEntry("AAD_PREMIUM", "078d2b04-f1bd-4111-bbd4-b4b1b354cef4", "Microsoft Entra ID P1"),
    SkuEntry("AAD_PREMIUM_P2", "84a661c4-e949-4bd2-a560-ed7766fcaf2b", "Microsoft Entra ID P2"),
    SkuEntry("INTUNE_A", "061f9ace-7d42-4136-88ac-31dc755f143f", "Intune"),
    SkuEntry("ATP_ENTERPRISE", "4ef96642-f096-40de-a3e9-d83fb2f90211", "Microsoft Defender for Office 365 (Plan 1)"),
    SkuEntry("THREAT_INTELLIGENCE", "3dd6cf57-d688-4eed-ba52-9e40b5468c3e", "Microsoft Defender for Office 365 (Plan 2)"),
    SkuEntry("WIN_DEF_ATP", "111046dd-295b-4d6d-9724-d52ac90bd1f2", "Microsoft Defender for Endpoint"),
    SkuEntry("MFA_STANDALONE", "cb2020b1-d8f6-41c0-9acd-8ff3d6d7831b", "Microsoft Azure Multi-Factor Authentication"),
    SkuEntry("RIGHTSMANAGEMENT", "c52ea49f-fe5d-4e95-93ba-1de91d380f89", "Azure Information Protection Plan 1"),
    SkuEntry("WACONEDRIVESTANDARD", "e6778190-713e-4e4f-9119-8b8238de25df", "OneDrive for Business (Plan 1)"),
    SkuEntry("WACONEDRIVEENTERPRISE", "ed01faf2-1d88-4947-ae91-45ca18703a96", "OneDrive for Business (Plan 2)"),
    SkuEntry("DYN365_ENTERPRISE_PLAN1", "ea126fc5-a19e-42e2-a731-da9d437bffcf", "Dynamics 365 Customer Engagement Plan"),
    SkuEntry("Microsoft_365_Copilot", "639dec6b-bb19-468b-871c-c5c441c4b0cb", "Microsoft Copilot for Microsoft 365"),
)

_BY_SKU: dict[str, SkuEntry] = {entry.sku_string.lower(): entry for entry in SKUS}
_BY_GUID: dict[str, SkuEntry] = {entry.guid.lower(): entry for entry in SKUS}


def search_skus(query: str) -> tuple[SkuEntry, ...]:
    """Filter SKUS by SKU string, GUID, or product name (case-insensitive substring match)."""
    needle = (query or "").strip().lower()
    if not needle:
        return SKUS
    return tuple(
        entry
        for entry in SKUS
        if needle in entry.sku_string.lower() or needle in entry.guid.lower() or needle in entry.product_name.lower()
    )


def lookup_sku(value: str) -> SkuEntry | None:
    """Look up a single SKU by exact SKU string or GUID match."""
    needle = (value or "").strip().lower()
    if not needle:
        return None
    return _BY_SKU.get(needle) or _BY_GUID.get(needle)
