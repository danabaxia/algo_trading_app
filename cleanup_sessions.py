import requests

url = "http://localhost:8000/sessions"

# Get all sessions
response = requests.get(url)
sessions = response.json()

# Delete all sessions except the first one
print(f"Found {len(sessions)} sessions. Deleting all...")
for session in sessions:
    try:
        response = requests.delete(f"{url}/{session['id']}")
        if response.status_code == 200:
            print(f"✓ Deleted: {session['name']} (ID: {session['id']})")
        else:
            print(f"✗ Failed to delete ID {session['id']}: {response.text}")
    except Exception as e:
        print(f"✗ Error deleting ID {session['id']}: {e}")

print("\nDone!")
