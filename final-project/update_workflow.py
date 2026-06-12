import json
import re

def slugify(text):
    text = re.sub(r'^\d+\.\d+\s+', '', text)
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

with open('My workflow.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for node in data.get('nodes', []):
    if node['name'] == 'Knowledge Resolver Vector Search':
        js_code = node['parameters']['jsCode']
        
        prefix_map = {
            'fin': 'Finance_Manual',
            'hr': 'HR_Manual',
            'it': 'IT_Manual',
            'pm': 'PM_Manual',
            'qa': 'QA_Manual'
        }
        
        # We need to parse the JSON array embedded in JS to add the anchor links.
        # But wait, the script we ran earlier already injected `"reference_link": "/kb/Finance_Manual.html",`
        # We need to also add the `#issue-slug` to it.
        # It's easier to just match the `id` and the `issue` from the json.
        
        def repl(match):
            id_val = match.group(1)
            issue_val = match.group(2)
            
            prefix = id_val.split('-')[0]
            doc = prefix_map.get(prefix, 'System_Manual')
            slug = slugify(issue_val)
            
            return f'"id": "{id_val}",\n    "reference_link": "/kb/{doc}.html#{slug}",\n    "issue": "{issue_val}"'
        
        # Regex to match:
        # "id": "fin-001",
        # "reference_link": "/kb/Finance_Manual.html",
        # "issue": "Invoice generation"
        
        pattern = r'"id":\s*"([^"]+)",\s*(?:"reference_link":\s*"[^"]+",\s*)?"issue":\s*"([^"]+)"'
        js_code = re.sub(pattern, repl, js_code)
        
        node['parameters']['jsCode'] = js_code

with open('My workflow.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Successfully added deep links to My workflow.json!")
