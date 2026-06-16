import json

with open('My workflow.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

count = 0
for node in data.get('nodes', []):
    if node['type'] == 'n8n-nodes-base.httpRequest':
        url = node.get('parameters', {}).get('url', '')
        if 'dummy-file-generator.com' in url:
            node['parameters']['url'] = "=http://localhost:5000/api/documents/{{$json.attachment_type}}"
            count += 1

if count > 0:
    with open('My workflow.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

print(f"Updated {count} HTTP Request nodes to point to local Flask API.")
