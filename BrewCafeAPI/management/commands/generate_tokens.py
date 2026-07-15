import csv
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Token seeding started.")
        count=50
        tokens=[]
        for i in range(1,count+1):
            username=f'load_test_user{i}'
            user,created=User.objects.get_or_create(username=username)
            if created:
                user.set_password(f'secure_pass_{i}')
                user.save()
        
            token,_=Token.objects.get_or_create(user=user)
            tokens.append(token.key)
        with open('tokens.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for key in tokens:
                writer.writerow([key])
        print("Token seeding complete!")