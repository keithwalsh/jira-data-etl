import re

def extract_text_from_content(data):
    if not isinstance(data, dict) or 'content' not in data:
        return data if isinstance(data, str) else ""
    
    result = ""
    for item in data['content']:
        if item['type'] in ['paragraph', 'heading']:
            for text_block in item['content']:
                text = text_block.get('text', '')
                if 'marks' in text_block:
                    for mark in text_block['marks']:
                        if mark['type'] == 'strong':
                            text = f"**{text}**"
                        elif mark['type'] == 'link':
                            text = f"[{text}]({mark['attrs']['href']})"
                result += text + ('\n' if text_block.get('type') == 'hardBreak' else '')
            result += '\n'
        elif item['type'] == 'bulletList':
            for list_item in item['content']:
                result += "* " + extract_text_from_content(list_item) + '\n'
    return result.strip()

def extract_issue_number(url):
    match = re.search(r'/issue/(\d+)/', url)
    return match.group(1) if match else "No match found"