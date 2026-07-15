import pytest
from rest_framework import status
from django.contrib.auth.models import Group,User

@pytest.mark.django_db
def test_user_can_register(new_client):
    payload={'username':'testuser','password':'my@complex_password!'}
    myresponse=new_client.post('/api/users/',data=payload)
    assert myresponse.status_code==status.HTTP_201_CREATED

@pytest.mark.django_db
def test_user_can_receive_token(new_client):
    User.objects.create_user(username='testuser',password='my@complex_password!')
    myresponse=new_client.post('/token/login',data={'username':'testuser','password':'my@complex_password!'})
    assert myresponse.status_code==status.HTTP_200_OK
    assert myresponse.data['auth_token'] is not None

@pytest.mark.django_db
def test_admin_can_assign_user_to_manager_group(new_user,new_client,new_admin):
    Group.objects.get_or_create(name='Manager')
    new_client.force_authenticate(user=new_admin)
    myresponse=new_client.post('/api/groups/manager/users',data={'username':new_user.username})
    assert myresponse.status_code==status.HTTP_201_CREATED
    new_user.refresh_from_db()
    assert new_user.groups.filter(name='Manager').exists()==True


@pytest.mark.django_db
def test_manager_assign_user_to_delivery_crew(new_user,new_client,manager_user):
    Group.objects.get_or_create(name='Delivery crew')
    new_client.force_authenticate(user=manager_user)
    myresponse=new_client.post('/api/groups/delivery-crew/users',data={'username':new_user.username})
    assert myresponse.status_code==status.HTTP_201_CREATED
    assert new_user.groups.filter(name='Delivery crew').exists()==True


@pytest.mark.django_db
def test_manager_can_see_all_registered_users(new_client,manager_user):
    new_client.force_authenticate(user=manager_user)
    myresponse=new_client.get('/api/users/')
    assert myresponse.status_code==status.HTTP_200_OK
