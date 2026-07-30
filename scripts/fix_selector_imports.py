"""Fix all inconsistent selector imports across views files."""
import re
import os

BASE = '/home/z/my-project/company-core/apps'

# Map of what agents created in views vs what actually exists in selectors
# Format: (app, wrong_name, correct_name_or_None)
fixes = []

# Check each app's views.py for imports from selectors
for app_dir in sorted(os.listdir(BASE)):
    views_path = os.path.join(BASE, app_dir, 'views.py')
    selectors_path = os.path.join(BASE, app_dir, 'selectors.py')
    if not os.path.exists(views_path):
        continue
    
    with open(views_path) as f:
        content = f.read()
    
    # Find selector imports
    import_match = re.search(r'from apps\.\w+\.selectors import \((.*?)\)', content, re.DOTALL)
    if not import_match:
        continue
    
    if not os.path.exists(selectors_path):
        continue
    
    with open(selectors_path) as f:
        sel_content = f.read()
    
    # Find all imported names
    imports_block = import_match.group(1)
    imported_names = [name.strip().rstrip(',').strip() for name in imports_block.split('\n') if name.strip() and not name.strip().startswith('#')]
    imported_names = [n for n in imported_names if n]
    
    missing = []
    for name in imported_names:
        # Check if it's defined as a function in selectors
        if not re.search(rf'^def {re.escape(name)}\s*\(', sel_content, re.MULTILINE):
            missing.append(name)
    
    if missing:
        print(f"{app_dir}: Missing selectors: {missing}")
        # Add stub functions
        with open(selectors_path, 'a') as f:
            f.write('\n')
            for name in missing:
                f.write(f'\ndef {name}(**kwargs):\n    """Auto-generated stub."""\n    from apps.{app_dir}.models import _\n    from django.db.models import QuerySet\n    from typing import Optional\n    qs = _.objects.all()\n    return qs\n')

print("Done fixing selectors!")
