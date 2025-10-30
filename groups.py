import os
import json
import requests
from msal import ConfidentialClientApplication

# --- CONFIG (ROTATE your secret; prefer env vars in real use) ---
CLIENT_ID = "062afed7-121c-4feb-b831-4b1548b53a3e"
TENANT_ID = "c60ddd5e-0f69-4da3-a677-8c7167d8dc3b"
CLIENT_SECRET = "0vp8Q~ywpqThMRBFYs~UZZRH4O9Xrf4yXhe5_bnw"  # <-- rotate & replace

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/.default"]

# --- MSAL APP ---
app = ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=AUTHORITY,
)

# --- TOKEN (no 'account' with client credentials) ---
result = app.acquire_token_for_client(scopes=SCOPES)
if "access_token" not in result:
    raise RuntimeError(
        f"Failed to obtain token: {result.get('error')} - {result.get('error_description')}"
    )

access_token = result["access_token"]
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}

# --- CALL GRAPH (/groups) with pagination ---
# Requires Application permission: Group.Read.All (or Directory.Read.All) + admin consent
groups = []
# Pick only useful fields to keep payload sane; add/remove as you wish
select = ",".join([
    "id","displayName","description","mail","mailNickname","mailEnabled",
    "securityEnabled","groupTypes","visibility","createdDateTime"
])
url = f"https://graph.microsoft.com/v1.0/groups?$top=999&$select={select}"

while url:
    resp = requests.get(url, headers=headers, timeout=60)
    if not resp.ok:
        raise RuntimeError(f"Graph call failed: {resp.status_code} - {resp.text}")
    data = resp.json()
    groups.extend(data.get("value", []))
    url = data.get("@odata.nextLink")  # follow nextLink if present

print(json.dumps(groups, indent=2))
print(f"\nTotal groups: {len(groups)}")
