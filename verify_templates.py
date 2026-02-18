import os
import django
from django.conf import settings
from django.template import Engine, Context, Template

import sys
BASE_DIR = r"d:\Project\Git Hub\Ecommerse"
sys.path.append(os.path.join(BASE_DIR, 'techshop'))

if not settings.configured:
    settings.configure(
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'techshop', 'templates')],
            'APP_DIRS': True,
        }],
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'store',
            'cart',
            'orders',
        ]
    )
    django.setup()

def check_template(template_name):
    try:
        engine = Engine.get_default()
        template = engine.get_template(template_name)
        print(f"SUCCESS: Template '{template_name}' syntax is valid.")
    except Exception as e:
        print(f"ERROR: Template '{template_name}' has syntax errors: {e}")

# Check all templates recursively
template_dir = os.path.join(BASE_DIR, 'techshop', 'templates')
for root, dirs, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html'):
            # Get relative path for template loader
            rel_path = os.path.relpath(os.path.join(root, file), template_dir)
            # Iterate through all templates but replace backslash with forward slash for Django
            check_template(rel_path.replace(os.sep, '/'))

