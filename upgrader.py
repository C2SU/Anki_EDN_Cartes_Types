import os
import re

def upgrade_file(src_path, dest_path):
    with open(src_path, 'r', encoding='utf-8') as f:
        src = f.read()
    with open(dest_path, 'r', encoding='utf-8') as f:
        dest = f.read()

    # extract front additions from src:
    src_front = src.split('## Back Template')[0]
    front_additions_match = re.search(r'(<div style=\"display:none;\".*</script>)\s*```$', src_front, re.DOTALL)
    front_additions = front_additions_match.group(1) if front_additions_match else ''
        
    # extract back additions from src:
    src_back = src.split('## Styling')[0].split('## Back Template')[1]
    back_script_match = re.search(r'(<div style=\"display:none;\" id=\"flags.*</script>)\s*```$', src_back, re.DOTALL)
    if back_script_match:
        back_script = back_script_match.group(1)
    else:
        back_script_only = re.search(r'(<script>.*</script>)\s*```$', src_back, re.DOTALL)
        back_script = back_script_only.group(1) if back_script_only else ''

    # extract styling from src:
    styling = src.split('## Styling')[1]

    # Now patch dest
    dest_front = dest.split('## Back Template')[0]
    dest_front = re.sub(r'<script.*</script>\s*', '', dest_front, flags=re.DOTALL)
    dest_front = re.sub(r'(\s*```\s*)$', '\n\n' + front_additions.replace('\\', '\\\\') + r'\1', dest_front)

    dest_back_styling = dest.split('## Back Template')[1]
    dest_back = dest_back_styling.split('## Styling')[0]
    
    # remove old scripts from dest back
    dest_back = re.sub(r'<div style=\"display:none;\" id=\"flags\">.*?</div>\s*', '', dest_back, flags=re.DOTALL)
    dest_back = re.sub(r'<script.*?</script>\s*', '', dest_back, flags=re.DOTALL)
    
    # inject new back script before ```
    dest_back = re.sub(r'(\s*```\s*)$', '\n\n' + back_script.replace('\\', '\\\\') + r'\1', dest_back)
    dest_back = dest_back.replace('<span>{{Cartes liées}}</span>', '{{Cartes liées}}')
    
    new_dest = dest_front + '## Back Template' + dest_back + '## Styling' + styling
    
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(new_dest)
    print('Upgraded', dest_path)

if __name__ == '__main__':
    upgrade_file('sémio.txt', 'sémio2.txt')
    upgrade_file('sémio.txt', 'sémio3.txt')
    upgrade_file('syndrome.txt', 'syndrome2.txt')
