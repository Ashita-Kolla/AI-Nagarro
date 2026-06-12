import os
import re

kb_dir = "frontend/public/kb"
md_files = [f for f in os.listdir(kb_dir) if f.endswith('.md')]

template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Nagarro Knowledge Base</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Merriweather:wght@700&display=swap');

        *, *::before, *::after {{ box-sizing: border-box; }}

        :root {{
            --blue: #2563eb;
            --blue-light: #eff6ff;
            --blue-border: #bfdbfe;
            --slate-900: #0f172a;
            --slate-800: #1e293b;
            --slate-700: #334155;
            --slate-500: #64748b;
            --slate-400: #94a3b8;
            --slate-200: #e2e8f0;
            --slate-100: #f1f5f9;
            --slate-50: #f8fafc;
            --red-100: #fee2e2;
            --red-700: #b91c1c;
            --red-border: #fca5a5;
            --green-100: #dcfce7;
            --green-700: #15803d;
            --amber-100: #fef3c7;
            --amber-700: #b45309;
        }}

        html {{ scroll-behavior: smooth; }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 15px;
            line-height: 1.75;
            color: var(--slate-700);
            background: var(--slate-50);
            margin: 0;
            padding: 0;
        }}

        /* TOP BAR */
        .topbar {{
            background: var(--slate-900);
            color: white;
            padding: 12px 40px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 13px;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .topbar-brand {{
            font-weight: 700;
            font-size: 15px;
            color: white;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .topbar-brand::before {{
            content: '';
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #22c55e;
            border-radius: 50%;
        }}
        .topbar-meta {{
            color: var(--slate-400);
        }}

        /* LAYOUT */
        .layout {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 48px 24px;
            display: grid;
            grid-template-columns: 240px 1fr;
            gap: 48px;
            align-items: start;
        }}

        /* TOC SIDEBAR */
        .toc {{
            position: sticky;
            top: 72px;
            background: white;
            border: 1px solid var(--slate-200);
            border-radius: 12px;
            padding: 24px;
            font-size: 13px;
        }}
        .toc-title {{
            font-weight: 700;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--slate-500);
            margin-bottom: 12px;
        }}
        .toc a {{
            display: block;
            color: var(--slate-500);
            text-decoration: none;
            padding: 4px 0;
            border-left: 2px solid transparent;
            padding-left: 10px;
            margin-left: -10px;
            transition: all 0.15s;
            line-height: 1.4;
        }}
        .toc a:hover {{
            color: var(--blue);
            border-left-color: var(--blue);
        }}
        .toc a.toc-h3 {{
            padding-left: 20px;
            margin-left: -10px;
            font-size: 12px;
            color: var(--slate-400);
        }}

        /* MAIN CONTENT */
        .content {{
            background: white;
            border: 1px solid var(--slate-200);
            border-radius: 12px;
            overflow: hidden;
        }}

        .doc-header {{
            background: linear-gradient(135deg, var(--slate-900) 0%, #1e3a5f 100%);
            padding: 48px 48px 40px;
            color: white;
        }}
        .doc-header h1 {{
            font-family: 'Merriweather', Georgia, serif;
            font-size: 2rem;
            font-weight: 700;
            margin: 0 0 16px 0;
            line-height: 1.25;
        }}
        .doc-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 24px;
            font-size: 12px;
            color: #93c5fd;
            margin-top: 16px;
        }}
        .doc-meta span {{ display: flex; align-items: center; gap: 6px; }}
        .doc-badge {{
            display: inline-flex;
            align-items: center;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            color: #e2e8f0;
            font-size: 11px;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 20px;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }}

        .doc-body {{
            padding: 48px;
        }}

        /* TYPOGRAPHY */
        h2 {{
            font-family: 'Merriweather', Georgia, serif;
            font-size: 1.35rem;
            font-weight: 700;
            color: var(--slate-900);
            margin: 48px 0 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid var(--slate-200);
            scroll-margin-top: 80px;
        }}
        h2:first-of-type {{ margin-top: 0; }}

        h3 {{
            font-size: 1rem;
            font-weight: 700;
            color: var(--blue);
            margin: 32px 0 12px;
            scroll-margin-top: 80px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        h3::before {{
            content: '';
            display: inline-block;
            width: 4px;
            height: 16px;
            background: var(--blue);
            border-radius: 2px;
            flex-shrink: 0;
        }}

        p {{
            margin: 0 0 16px;
            color: var(--slate-700);
        }}

        strong {{
            color: var(--slate-900);
            font-weight: 600;
        }}

        ul, ol {{
            margin: 0 0 20px;
            padding-left: 24px;
        }}
        li {{ margin-bottom: 8px; color: var(--slate-700); }}
        li::marker {{ color: var(--blue); }}

        /* NUMBERED STEPS */
        .steps {{ counter-reset: step; list-style: none; padding: 0; }}
        .steps li {{
            counter-increment: step;
            display: flex;
            gap: 16px;
            margin-bottom: 20px;
            padding: 16px 20px;
            background: var(--slate-50);
            border: 1px solid var(--slate-200);
            border-radius: 10px;
        }}
        .steps li::before {{
            content: counter(step);
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 28px;
            height: 28px;
            background: var(--blue);
            color: white;
            font-size: 12px;
            font-weight: 700;
            border-radius: 50%;
            flex-shrink: 0;
            margin-top: 2px;
        }}

        /* TABLES */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0 28px;
            font-size: 14px;
        }}
        thead tr {{
            background: var(--slate-900);
            color: white;
        }}
        thead th {{
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        tbody tr {{ border-bottom: 1px solid var(--slate-200); }}
        tbody tr:nth-child(even) {{ background: var(--slate-50); }}
        tbody tr:hover {{ background: var(--blue-light); }}
        td {{
            padding: 12px 16px;
            vertical-align: top;
        }}

        /* ESCALATION / CALLOUT BOXES */
        .callout {{
            display: flex;
            gap: 14px;
            padding: 16px 20px;
            border-radius: 10px;
            margin: 24px 0;
            font-size: 14px;
            line-height: 1.6;
        }}
        .callout-icon {{ font-size: 18px; flex-shrink: 0; margin-top: 2px; }}
        .callout.red {{
            background: var(--red-100);
            border: 1px solid var(--red-border);
            color: var(--red-700);
        }}
        .callout.amber {{
            background: var(--amber-100);
            border: 1px solid #fcd34d;
            color: var(--amber-700);
        }}
        .callout.blue {{
            background: var(--blue-light);
            border: 1px solid var(--blue-border);
            color: #1e40af;
        }}
        .callout.green {{
            background: var(--green-100);
            border: 1px solid #86efac;
            color: var(--green-700);
        }}

        /* DIVIDER */
        hr {{
            border: none;
            border-top: 1px solid var(--slate-200);
            margin: 48px 0;
        }}

        /* OVERVIEW BLOCK */
        .overview-block {{
            background: var(--blue-light);
            border-left: 4px solid var(--blue);
            border-radius: 0 8px 8px 0;
            padding: 20px 24px;
            margin: 0 0 40px;
            font-size: 14.5px;
            color: #1e3a5f;
        }}

        /* FOOTER */
        .doc-footer {{
            margin-top: 64px;
            padding: 24px 0 0;
            border-top: 1px solid var(--slate-200);
            font-size: 12px;
            color: var(--slate-400);
            display: flex;
            justify-content: space-between;
        }}

        /* RESPONSIVE */
        @media (max-width: 900px) {{
            .layout {{ grid-template-columns: 1fr; }}
            .toc {{ position: static; }}
            .doc-header {{ padding: 32px; }}
            .doc-body {{ padding: 32px; }}
        }}
    </style>
</head>
<body>
    <div class="topbar">
        <a class="topbar-brand" href="#">Nagarro Knowledge Base</a>
        <span class="topbar-meta">Internal Use Only — Confidential</span>
    </div>
    <div class="layout">
        <nav class="toc">
            <div class="toc-title">Contents</div>
            {toc}
        </nav>
        <article class="content">
            <div class="doc-header">
                {header}
            </div>
            <div class="doc-body">
                {body}
                <div class="doc-footer">
                    <span>Nagarro Internal Knowledge Base</span>
                    <span>Classification: Internal Use Only</span>
                </div>
            </div>
        </article>
    </div>
</body>
</html>"""


def slugify(text):
    text = re.sub(r'^\d+[\.\d]*\s+', '', text)
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def md_to_html(md):
    """Convert markdown to structured HTML with styled components."""
    lines = md.split('\n')
    html_lines = []
    in_table = False
    table_lines = []
    in_list = False
    list_lines = []
    list_type = None
    in_para = False
    para_lines = []

    def flush_para():
        nonlocal in_para, para_lines
        if para_lines:
            content = ' '.join(para_lines).strip()
            if content:
                html_lines.append(f'<p>{content}</p>')
        para_lines = []
        in_para = False

    def flush_list():
        nonlocal in_list, list_lines, list_type
        if list_lines:
            tag = 'ol' if list_type == 'ol' else 'ul'
            # Check if all items are "Step N –" pattern
            is_steps = all(re.match(r'\*\*Step \d+', li) for li in list_lines if li.strip())
            if is_steps:
                items_html = ''.join(f'<li>{li}</li>' for li in list_lines)
                html_lines.append(f'<ol class="steps">{items_html}</ol>')
            else:
                items_html = ''.join(f'<li>{li}</li>' for li in list_lines)
                html_lines.append(f'<{tag}>{items_html}</{tag}>')
        list_lines = []
        in_list = False
        list_type = None

    def flush_table():
        nonlocal in_table, table_lines
        if table_lines:
            rows = [r for r in table_lines if '|' in r and not re.match(r'^\|[\s\-\|]+\|$', r)]
            if len(rows) >= 2:
                header = rows[0]
                body_rows = rows[1:]
                def parse_row(row):
                    cells = [c.strip() for c in row.strip('|').split('|')]
                    return cells
                th_cells = parse_row(header)
                thead = '<thead><tr>' + ''.join(f'<th>{c}</th>' for c in th_cells) + '</tr></thead>'
                tbody_rows = []
                for row in body_rows:
                    tds = parse_row(row)
                    tbody_rows.append('<tr>' + ''.join(f'<td>{c}</td>' for c in tds) + '</tr>')
                tbody = '<tbody>' + ''.join(tbody_rows) + '</tbody>'
                html_lines.append(f'<table>{thead}{tbody}</table>')
        table_lines = []
        in_table = False

    def process_inline(text):
        # Bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        # Italic
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        # Code
        text = re.sub(r'`([^`]+)`', r'<code style="background:#f1f5f9;padding:1px 5px;border-radius:4px;font-size:13px;font-family:monospace">\1</code>', text)
        return text

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Blank line
        if not stripped:
            flush_para()
            if in_list: flush_list()
            if in_table: flush_table()
            html_lines.append('')
            i += 1
            continue

        # HR
        if re.match(r'^---+$', stripped):
            flush_para()
            flush_list()
            flush_table()
            html_lines.append('<hr>')
            i += 1
            continue

        # H1 (skip — handled in header separately)
        if stripped.startswith('# ') and not stripped.startswith('## '):
            flush_para(); flush_list(); flush_table()
            i += 1
            continue

        # H2
        if stripped.startswith('## '):
            flush_para(); flush_list(); flush_table()
            text = stripped[3:]
            slug = slugify(text)
            html_lines.append(f'<h2 id="{slug}">{process_inline(text)}</h2>')
            i += 1
            continue

        # H3
        if stripped.startswith('### '):
            flush_para(); flush_list(); flush_table()
            text = stripped[4:]
            slug = slugify(text)
            html_lines.append(f'<h3 id="{slug}">{process_inline(text)}</h3>')
            i += 1
            continue

        # Table row
        if stripped.startswith('|'):
            flush_para(); flush_list()
            in_table = True
            table_lines.append(stripped)
            i += 1
            continue
        else:
            if in_table:
                flush_table()

        # Escalation callout
        if '**Escalation Policy:**' in stripped:
            flush_para(); flush_list()
            text = process_inline(stripped)
            html_lines.append(f'<div class="callout red"><span class="callout-icon">⚠️</span><div>{text}</div></div>')
            i += 1
            continue

        # Ordered list
        if re.match(r'^\d+[\.\)]\s', stripped):
            flush_para()
            if not in_list or list_type != 'ol':
                if in_list: flush_list()
                in_list = True
                list_type = 'ol'
            content = re.sub(r'^\d+[\.\)]\s+', '', stripped)
            list_lines.append(process_inline(content))
            i += 1
            continue
        else:
            if in_list and list_type == 'ol':
                flush_list()

        # Unordered list
        if re.match(r'^[-\*]\s', stripped):
            flush_para()
            if not in_list or list_type != 'ul':
                if in_list: flush_list()
                in_list = True
                list_type = 'ul'
            content = re.sub(r'^[-\*]\s+', '', stripped)
            list_lines.append(process_inline(content))
            i += 1
            continue
        else:
            if in_list and list_type == 'ul':
                flush_list()

        # Checkbox list items (e.g. "- ☐ Item")
        if re.match(r'^[-\*]\s[☐☑✅]', stripped):
            flush_para()
            if not in_list:
                in_list = True
                list_type = 'ul'
            content = re.sub(r'^[-\*]\s+', '', stripped)
            list_lines.append(process_inline(content))
            i += 1
            continue

        # Document metadata lines (bold key: value)
        if re.match(r'^\*\*[^*]+:\*\*', stripped):
            flush_para(); flush_list()
            html_lines.append(f'<p style="margin:2px 0;font-size:13px;color:#64748b">{process_inline(stripped)}</p>')
            i += 1
            continue

        # Regular paragraph text
        flush_list(); flush_table()
        in_para = True
        para_lines.append(process_inline(stripped))
        i += 1

    flush_para()
    flush_list()
    flush_table()

    return '\n'.join(html_lines)


def extract_header(md):
    """Extract h1 title and metadata from the top of the document."""
    lines = md.split('\n')
    title = ''
    meta = []
    body_start = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('# ') and not stripped.startswith('## '):
            title = stripped[2:]
        elif re.match(r'^\*\*[^*]+:\*\*', stripped):
            key_val = re.match(r'\*\*([^*]+):\*\*\s*(.*)', stripped)
            if key_val:
                meta.append((key_val.group(1), key_val.group(2)))
        elif stripped == '---':
            body_start = i + 1
            break

    badges = [f'<span class="doc-badge">{v}</span>' for k, v in meta if k in ['Version', 'Classification']]
    meta_items = [f'<span>📋 {k}: {v}</span>' for k, v in meta]

    header_html = f'<h1>{title}</h1>'
    if meta_items:
        header_html += f'<div class="doc-meta">{"".join(meta_items)}</div>'
    if badges:
        header_html += f'<div style="margin-top:16px;display:flex;gap:8px">{"".join(badges)}</div>'

    return header_html, title, body_start


def build_toc(html_body):
    """Build a table of contents from h2/h3 headings."""
    toc_items = []
    for m in re.finditer(r'<h([23]) id="([^"]+)">([^<]+)</h[23]>', html_body):
        level, slug, text = m.group(1), m.group(2), m.group(3)
        css = 'toc-h3' if level == '3' else ''
        toc_items.append(f'<a href="#{slug}" class="{css}">{text}</a>')
    return '\n'.join(toc_items)


# Generate HTML for all MD files
for file in sorted(md_files):
    with open(os.path.join(kb_dir, file), 'r', encoding='utf-8') as f:
        md = f.read()

    header_html, title, body_start = extract_header(md)

    # Process body from after the HR separator
    body_md = '\n'.join(md.split('\n')[body_start:])
    body_html = md_to_html(body_md)

    # Overview block — first paragraph after separator
    first_p_match = re.search(r'<p>(.*?)</p>', body_html)
    if first_p_match:
        overview_text = first_p_match.group(0)
        body_html = body_html.replace(overview_text,
            f'<div class="overview-block">{first_p_match.group(1)}</div>', 1)

    toc = build_toc(body_html)

    final_html = template.format(
        title=title,
        header=header_html,
        body=body_html,
        toc=toc
    )

    out_file = file.replace('.md', '.html')
    with open(os.path.join(kb_dir, out_file), 'w', encoding='utf-8') as f:
        f.write(final_html)

    print(f'Done: {out_file}')

print('\nAll professional HTML docs generated!')
