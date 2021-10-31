import os

import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

if 'ADMIN_USER' in os.environ and 'ADMIN_PASSWORD' in os.environ:
    UserModel = get_user_model()
    if UserModel.objects.filter(username=os.environ['ADMIN_USER']).exists():
        print('Superuser already exists')
    else:

        UserModel.objects.create_superuser(
            username=os.environ['ADMIN_USER'],
            password=os.environ['ADMIN_PASSWORD'],
        )
        print('Superuser successfully created')
else:
    print('Superuser settings not found')
