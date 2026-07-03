import pytest
from rest_framework.test import APIClient
from LittleLemonAPI.models import Category,MenuItem
from django.contrib.auth.models import Group,User

@pytest.fixture
def new_user(db):
    testuser=User.objects.create_user(username='testuser')
    return testuser

@pytest.fixture
def manager_user(db):
    manager_user=User.objects.create_user(username='manageruser')
    mygroup,_=Group.objects.get_or_create(name='Manager')
    manager_user.groups.add(mygroup)
    return manager_user

@pytest.fixture
def deliverycrew_user(db):
    deliverycrew_user=User.objects.create_user(username='deliverycrewuser')
    mygroup,_=Group.objects.get_or_create(name='Delivery crew')
    deliverycrew_user.groups.add(mygroup)
    return deliverycrew_user

@pytest.fixture
def new_admin(db):
    admin_user=User.objects.create_superuser(username='admin_user',password='admin@lemon',is_staff=True,is_superuser=True)
    return admin_user

@pytest.fixture
def new_category(db):
    testcategory=Category.objects.create(title='Dessert',slug='dessert')
    return testcategory

@pytest.fixture
def new_menuitem(new_category,db):
    myitem=MenuItem.objects.create(title='Fruit Cake', price=10.00, featured=False,category=new_category)
    return myitem

@pytest.fixture
def new_client():
    myclient=APIClient()
    return myclient
    