# access_django_user_admin/utils.py
from django.conf import settings
import os


def get_base_template():
    app_name = getattr(settings, 'APP_NAME', None)

    # Mapping the APP_NAME to the correct template path
    template_mapping = {
        'Service Index': 'services/base_nav_full.html',
        'Dashboard': 'dashboard/base_nav_full.html',
        'ACCESS Operations API': 'web/base_nav_full.html',
    }

    return template_mapping.get(app_name, 'base_nav_full.html')

def get_current_app_name():
    return getattr(settings, 'APP_NAME', 'Unknown App')




