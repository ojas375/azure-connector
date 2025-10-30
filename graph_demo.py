import os
import json
import requests
from msal import ConfidentialClientApplication

# --- CONFIG (rotate your secret; prefer env vars) ---
CLIENT_ID = "062afed7-121c-4feb-b831-4b1548b53a3e"
TENANT_ID = "c60ddd5e-0f69-4da3-a677-8c7167d8dc3b"
CLIENT_SECRET = "0vp8Q~ywpqThMRBFYs~UZZRH4O9Xrf4yXhe5_bnw"  # ← rotate and replace; or use env: os.getenv("AZURE_CLIENT_SECRET")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/.default"]  # client credentials requires resource/.default

# --- MSAL APP ---
app = ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=AUTHORITY,
)

# --- TOKEN (no 'account' here) ---
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

# --- CALL GRAPH (/users) with pagination ---
users = []
url = "https://graph.microsoft.com/v1.0/users?$top=999"  # app perms need e.g., User.Read.All (application) + admin consent
while url:
    resp = requests.get(url, headers=headers, timeout=30)
    if not resp.ok:
        raise RuntimeError(f"Graph call failed: {resp.status_code} - {resp.text}")
    data = resp.json()
    users.extend(data.get("value", []))
    url = data.get("@odata.nextLink")  # follow nextLink if present

print(json.dumps(users, indent=2))
print(f"\nTotal users: {len(users)}")


