import json

with open('My workflow .json', 'r', encoding='utf-8') as f:
    data = json.load(f)

count = 0
for node in data.get('nodes', []):
    if node.get('name', '').endswith('Fetch Attachment') and node.get('type') == 'n8n-nodes-base.httpRequest':
        node['type'] = 'n8n-nodes-base.googleDrive'
        node['typeVersion'] = 3
        # Configure it to perform a search to find the file dynamically by name
        node['parameters'] = {
            "operation": "download",
            "fileId": {
                "__rl": True,
                "value": "ENTER_FILE_ID_HERE",
                "mode": "id"
            }
        }
        count += 1

if count > 0:
    with open('My workflow .json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

print(f"Replaced {count} HTTP Request nodes with Google Drive nodes.")
