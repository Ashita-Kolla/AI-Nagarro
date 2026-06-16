import json
import uuid

with open('My workflow.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = data.get('nodes', [])
connections = data.get('connections', {})

def find_node(name):
    for n in nodes:
        if n['name'] == name:
            return n
    return None

def generate_id():
    return str(uuid.uuid4())

# The departments and their Action Switches
depts = [
    {"name": "HR", "switch": "HR Action Switch"},
    {"name": "IT", "switch": "IT Action Switch"},
    {"name": "Finance", "switch": "Finance Action Switch"},
    {"name": "QA", "switch": "QA Action Switch"},
    {"name": "PM", "switch": "PM Action Switch"}
]

for dept_info in depts:
    dept = dept_info["name"]
    switch_name = dept_info["switch"]
    
    switch_connections = connections.get(switch_name, {}).get('main', [])
    if len(switch_connections) < 2:
        continue # Doesn't have a send_email branch
    
    # send_email is index 1
    send_email_targets = switch_connections[1]
    if not send_email_targets:
        continue
        
    email_node_name = send_email_targets[0]['node']
    email_node = find_node(email_node_name)
    if not email_node:
        continue
        
    print(f"Processing {dept}: Found email node {email_node_name}")
    
    # Let's see if we already processed it
    if "Check Attachment" in email_node_name or "Send Email (No Attach)" in email_node_name:
        print("Already processed.")
        continue

    # Create IF Node
    if_node_name = f"{dept} Check Attachment"
    if_node = {
      "parameters": {
        "conditions": {
          "options": {
            "caseSensitive": True,
            "leftValue": "",
            "typeValidation": "strict",
            "version": 3
          },
          "conditions": [
            {
              "id": generate_id(),
              "leftValue": "={{$json.requires_attachment}}",
              "rightValue": True,
              "operator": {
                "type": "boolean",
                "operation": "true",
                "name": "filter.operator.true"
              }
            }
          ],
          "combinator": "and"
        },
        "options": {}
      },
      "id": generate_id(),
      "name": if_node_name,
      "type": "n8n-nodes-base.if",
      "typeVersion": 2.3,
      "position": [
        email_node['position'][0],
        email_node['position'][1]
      ]
    }
    nodes.append(if_node)
    
    # Create Fetch Node (Dummy HTTP)
    fetch_node_name = f"{dept} Fetch Attachment"
    fetch_node = {
      "parameters": {
        "method": "GET",
        "url": "=https://dummy-file-generator.com/api/file?type={{$json.attachment_type}}",
        "sendHeaders": True,
        "headerParameters": {
          "parameters": [
            {
              "name": "Accept",
              "value": "application/pdf"
            }
          ]
        },
        "options": {
          "response": {
            "response": {
              "responseFormat": "file"
            }
          }
        }
      },
      "id": generate_id(),
      "name": fetch_node_name,
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [
        email_node['position'][0] + 200,
        email_node['position'][1] - 100
      ]
    }
    nodes.append(fetch_node)
    
    # Create Email Attach Node (Duplicate of original but with attachment)
    email_attach_name = f"{dept} Send Email (Attach)"
    email_attach_node = json.loads(json.dumps(email_node)) # deep copy
    email_attach_node['id'] = generate_id()
    email_attach_node['name'] = email_attach_name
    email_attach_node['position'] = [
        email_node['position'][0] + 400,
        email_node['position'][1] - 100
    ]
    if "options" not in email_attach_node["parameters"]:
        email_attach_node["parameters"]["options"] = {}
    email_attach_node["parameters"]["options"]["appendAttribution"] = False
    # Add attachment field
    email_attach_node["parameters"]["options"]["attachments"] = "data"
    nodes.append(email_attach_node)
    
    # Rename original email node
    new_original_name = f"{dept} Send Email (No Attach)"
    email_node['name'] = new_original_name
    email_node['position'] = [
        email_node['position'][0] + 200,
        email_node['position'][1] + 100
    ]
    
    # Update connections
    # 1. Switch -> If Node
    switch_connections[1][0]['node'] = if_node_name
    
    # 2. If node outputs
    connections[if_node_name] = {
        "main": [
            [{"node": fetch_node_name, "type": "main", "index": 0}], # True
            [{"node": new_original_name, "type": "main", "index": 0}] # False
        ]
    }
    
    # 3. Fetch node -> Email Attach
    connections[fetch_node_name] = {
        "main": [
            [{"node": email_attach_name, "type": "main", "index": 0}]
        ]
    }
    
    # 4. Old email node targets
    old_email_targets = connections.get(email_node_name, {}).get("main", [])
    
    # Update the key in connections to new name
    if email_node_name in connections:
        connections[new_original_name] = connections.pop(email_node_name)
    else:
        connections[new_original_name] = {"main": []}
        
    # Set targets for attached email node
    connections[email_attach_name] = {"main": json.loads(json.dumps(old_email_targets))}

with open('My workflow.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Updated workflow with IF nodes and attachment logic!")
