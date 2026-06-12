import json

with open('My workflow.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

agents = ['HR LLM Agent', 'IT LLM Agent', 'Finance LLM Agent', 'QA LLM Agent', 'PM LLM Agent']

for node in data.get('nodes', []):
    if node['name'] in agents:
        dept = node['name'].split(' ')[0]
        new_prompt = f"""=You are an experienced {dept} agent at an enterprise company.

User intent: {{{{ $json.intent }}}}
User message: {{{{ $(\"Webhook\").item.json.body.message }}}}

Carefully read the user's message and decide the single best action.

AVAILABLE ACTIONS:
- send_email: CRITICAL PRIORITY. ALWAYS choose this action if the user asks to receive an email, send an email, mail them, or contains phrases like "email me", "send me an email", "send an email", "mail me". This action takes absolute precedence over all other actions.
- create_ticket: ALWAYS USE THIS ACTION for ANY questions, how-tos, "how do I", policy inquiries, troubleshooting, or general requests. This action routes the user to the internal Knowledge Base to find a solution (unless they asked to be emailed).
- ask_clarification: ONLY use if the message is 100% gibberish.
- escalate: ONLY use for legal threats or critical outages.

Examples:
- "email me HR document" -> send_email
- "email me the payslip" -> send_email
- "send me an email for the payslip" -> send_email
- "send an email to the hr for leave on 12th june 2026" -> send_email
- "How do I generate an invoice?" -> create_ticket
- "My VPN is broken" -> create_ticket
- "What is the policy on leave?" -> create_ticket

Return ONLY raw valid JSON. DO NOT wrap the JSON in markdown blocks (e.g. no ```json).
{{
  "action": "create_ticket|send_email|ask_clarification|escalate",
  "priority": "low|medium|high",
  "summary": "one line summary",
  "email_subject": "",
  "email_body": ""
}}"""
        node['parameters']['text'] = new_prompt

with open('My workflow.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Prompts fixed.")
