import os, glob, re
for f in glob.glob('c:/Complaint System/Support Analysis System/Frontend/templates/*.html'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if 'url_for(\'notifications\')' in content and 'unread_notifications_count' not in content:
        pattern = r'(<a href="\{\{\s*url_for\(\'notifications\'\)\s*\}\}" style="position:relative;">\s*Notifications\s*)(</a>)'
        replacement = r'\1{% if unread_notifications_count > 0 %}<span class="badge bg-danger rounded-pill" style="position:absolute;top:50%;right:10px;transform:translateY(-50%);font-size:0.65rem;">{{ unread_notifications_count }}</span>{% endif %}\2'
        new_content = re.sub(pattern, replacement, content)
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f'Updated {f}')
