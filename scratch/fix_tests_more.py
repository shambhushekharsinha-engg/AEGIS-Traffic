import re

def fix_tests():
    with open("c:/AEGIS-Traffic/app/tests/test_traffic.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # fix test_fastapi_endpoints_clearance
    content = content.replace(
        'assert analyze_response.status_code == 200',
        'assert analyze_response.status_code == 202'
    )
    
    # fix test_operational_modes
    content = content.replace(
        'assert lockdown_response.status_code == 200',
        'assert lockdown_response.status_code == 202'
    )
    content = content.replace(
        'assert manual_response.status_code == 200',
        'assert manual_response.status_code == 202'
    )
    content = content.replace(
        'assert predictive_response.status_code == 200',
        'assert predictive_response.status_code == 202'
    )
    
    # For test_fastapi_endpoints_clearance: replace `assert "scenario" in analyze_data` with `assert "task_id" in analyze_data`
    content = content.replace(
        'assert "scenario" in analyze_data',
        'assert "task_id" in analyze_data'
    )
    
    with open("c:/AEGIS-Traffic/app/tests/test_traffic.py", "w", encoding="utf-8") as f:
        f.write(content)

fix_tests()
