import requests
import json

url = "http://localhost:8000/sessions"

# Test 1: Create a session
print("Test 1: Creating session...")
data = {
    "name": "Test Duplicate",
    "strategies": ["GoldenCross_SMA"],
    "mode": "PAPER"
}
response = requests.post(url, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# Test 2: Try to create duplicate
print("Test 2: Trying to create duplicate...")
response2 = requests.post(url, json=data)
print(f"Status: {response2.status_code}")
print(f"Response: {response2.json()}\n")

# Test 3: List sessions
print("Test 3: Listing sessions...")
response3 = requests.get(url)
sessions = response3.json()
print(f"Found {len(sessions)} sessions")
for s in sessions:
    print(f"  - {s['name']} (ID: {s['id']}, Status: {s['status']})")

# Test 4: Delete the test session
if sessions:
    session_id = sessions[0]['id']
    print(f"\nTest 4: Deleting session {session_id}...")
    response4 = requests.delete(f"{url}/{session_id}")
    print(f"Status: {response4.status_code}")
    print(f"Response: {response4.json()}")
