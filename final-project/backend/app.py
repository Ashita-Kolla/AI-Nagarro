import os
from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/api/documents/<doc_type>')
def generate_document(doc_type):
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Map attachment types to their respective templates
    template_map = {
        'invoice': 'invoice.html',
        'payslip': 'payslip.html',
        'policy': 'policy.html',
        'hr_policy': 'policy.html'
    }
    
    # Default to policy if unknown
    template_name = template_map.get(doc_type.lower(), 'policy.html')
    
    return render_template(template_name, date=current_date)

if __name__ == '__main__':
    # Start the server
    app.run(host='0.0.0.0', port=5000, debug=True)
