#!/usr/bin/env python3
"""Fix all urls.py to use explicit imports instead of star imports."""
import os, re

BASE = "/home/z/my-project/company-core"

modules = [
    "billing", "ai", "agents", "audit", "permissions", "quotas",
    "feature_flags", "notifications", "settings_mod", "webhooks",
    "workflows", "jobs", "storage"
]

for mod_name in modules:
    urls_path = os.path.join(BASE, "apps", mod_name, "urls.py")
    if not os.path.exists(urls_path):
        continue
    
    with open(urls_path) as f:
        content = f.read()
    
    # Replace "from apps.X.views import *" with explicit imports
    # First find the module name from the content
    mod_label = mod_name.replace("_mod", "")
    
    # Extract function names from urlpatterns
    functions = re.findall(r'(\w+)\s*,\s*name=', content)
    
    # Replace the star import
    old_import = f"from apps.{mod_name}.views import *"
    new_import = f"from apps.{mod_name} import views as {mod_label}_views"
    
    content = content.replace(old_import, new_import)
    
    # Replace function references
    for func in functions:
        content = content.replace(f"    {func},", f"    {mod_label}_views.{func},")
    
    with open(urls_path, "w") as f:
        f.write(content)

print("All URLs fixed!")
