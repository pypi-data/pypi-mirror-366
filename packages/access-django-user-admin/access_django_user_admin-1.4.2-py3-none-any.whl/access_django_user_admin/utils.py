# access_django_user_admin/utils.py
from django.conf import settings
import os


def get_base_template():
    app_name = getattr(settings, 'APP_NAME', None)
    print(f"DEBUG: APP_NAME = '{app_name}'")

    template_mapping = {
        'Service Index': 'services/base_nav_full.html',
        'Dashboard': 'dashboard/base_nav_full.html', 
        'ACCESS Operations API': 'web/base_nav_full.html',
    }

    result = template_mapping.get(app_name, 'base_nav_full.html')
    print(f"DEBUG: Returning template: '{result}'")
    return result


