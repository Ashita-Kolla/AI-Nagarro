import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

def generate_static():
    # Setup Jinja
    env = Environment(loader=FileSystemLoader('backend/templates'))
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Create export directory
    export_dir = 'frontend/public/gdrive_exports'
    os.makedirs(export_dir, exist_ok=True)
    
    # Templates to render
    templates = ['invoice.html', 'payslip.html', 'policy.html']
    
    for template_name in templates:
        template = env.get_template(template_name)
        rendered_html = template.render(date=current_date)
        
        output_path = os.path.join(export_dir, template_name)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_static()
