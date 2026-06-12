import urllib.request
import urllib.error
import json

WEBHOOK_URL = "https://ashitakolla.app.n8n.cloud/webhook/service-desk"

def test_email_sending():
    test_cases = [
        "email me HR document",
        "email me the payslip",
        "send me an email for the payslip",
        "send an email to the hr for leave on 12th june 2026"
    ]
    
    for msg in test_cases:
        payload = {
            "message": msg,
            "context": None
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(WEBHOOK_URL, data=data, headers={"Content-Type": "application/json"})

        print(f"\nSending request for: '{msg}'...")
        try:
            with urllib.request.urlopen(req) as response:
                response_data = json.loads(response.read().decode('utf-8'))
                print("Response status:", response_data.get("status"))
                print("Response action:", response_data.get("action"))
                if response_data.get("status") == "email_sent" or response_data.get("action") == "send_email":
                    print("[SUCCESS]: Triggered email sending action.")
                else:
                    print("[FAILED]: Did not trigger email sending action.")
                    # Print full response for debugging
                    print(json.dumps(response_data, indent=2))
        except urllib.error.URLError as e:
            print(f"[ERROR]: Failed to connect. Details: {e}")

if __name__ == "__main__":
    test_email_sending()
