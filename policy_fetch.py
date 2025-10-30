import os
import json
import requests
from msal import ConfidentialClientApplication

CLIENT_ID = os.getenv("CLIENT_ID", "062afed7-121c-4feb-b831-4b1548b53a3e")
TENANT_ID = os.getenv("TENANT_ID", "c60ddd5e-0f69-4da3-a677-8c7167d8dc3b")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "0vp8Q~ywpqThMRBFYs~UZZRH4O9Xrf4yXhe5_bnw")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/.default"]

app = ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=AUTHORITY,
)
tok = app.acquire_token_for_client(scopes=SCOPES)
if "access_token" not in tok:
    raise RuntimeError(f"Token fail: {tok.get('error')} - {tok.get('error_description')}")

headers = {"Authorization": f"Bearer {tok['access_token']}", "Content-Type": "application/json"}

def get_all(url):
    items = []
    while url:
        r = requests.get(url, headers=headers, timeout=60)
        if not r.ok:
            raise RuntimeError(f"GET {url} -> {r.status_code} {r.text}")
        data = r.json()
        items.extend(data.get("value", []) if isinstance(data, dict) else [])
        url = data.get("@odata.nextLink") if isinstance(data, dict) else None
    return items

# 1) Security defaults (enabled/disabled)
sec_defaults_url = "https://graph.microsoft.com/v1.0/policies/identitySecurityDefaultsEnforcementPolicy"
sec_defaults = requests.get(sec_defaults_url, headers=headers, timeout=60).json()

# 2) Conditional Access policies
cap_url = "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies?$top=999"
conditional_access_policies = get_all(cap_url)

# 3) Named locations (used in CA policies)
nl_url = "https://graph.microsoft.com/v1.0/identity/conditionalAccess/namedLocations?$top=999"
named_locations = get_all(nl_url)

# 4) Authentication methods policy (tenant-level MFA config surface)
auth_methods_policy_url = "https://graph.microsoft.com/v1.0/policies/authenticationMethodsPolicy"
auth_methods_policy = requests.get(auth_methods_policy_url, headers=headers, timeout=60).json()

print("=== Identity Security Defaults ===")
print(json.dumps(sec_defaults, indent=2))

print("\n=== Conditional Access Policies ===")
print(json.dumps(conditional_access_policies, indent=2))
print(f"\nTotal CA policies: {len(conditional_access_policies)}")

print("\n=== Named Locations ===")
print(json.dumps(named_locations, indent=2))
print(f"\nTotal named locations: {len(named_locations)}")

print("\n=== Authentication Methods Policy ===")
print(json.dumps(auth_methods_policy, indent=2))
