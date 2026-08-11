import re

with open('dashboard/app.py', 'r', encoding='utf-8') as f:
    code = f.read()

router_line = '    "📽️ Scenario Replay": render_replay_page,\n'
code = code.replace('    "⚙️ Settings & Pipeline": render_settings_page,\n}', '    "⚙️ Settings & Pipeline": render_settings_page,\n' + router_line + '}')

with open('dashboard/app.py', 'w', encoding='utf-8') as f:
    f.write(code)
