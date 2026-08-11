import re

with open('dashboard/components/sidebar.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Insert the new module after City Impact
new_module = '    ("📽️ Scenario Replay", "📽️ Scenario Replay"),\n'
code = code.replace('    ("dYO? City Impact", "dYO? City Impact"),', '    ("dYO? City Impact", "dYO? City Impact"),') # Using a regex to be safe about the emoji

code = re.sub(
    r'(\(".*? City Impact", ".*? City Impact"\),\n)',
    r'\1' + new_module,
    code
)

with open('dashboard/components/sidebar.py', 'w', encoding='utf-8') as f:
    f.write(code)
