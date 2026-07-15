import pytest
from rest_framework import status
from LittleLemonAPI.models import Cart,Order,Status
from django.contrib.auth.models import Group,User
from django.utils import timezone

@pytest.mark.django_db
def test_customers_can_place_orders(new_user,new_client,new_menuitem):
    item_qty=2
    item_up=new_menuitem.price
    total_itemprice=item_qty*item_up
    Cart.objects.create(user=new_user, menuitem=new_menuitem, 
                        quantity=item_qty, unit_price=item_up,
                        price=total_itemprice)
    new_client.force_authenticate(user=new_user)
    myresponse=new_client.post('/api/orders')
    assert myresponse.status_code==status.HTTP_201_CREATED

@pytest.mark.django_db
def test_customer_can_browse_their_orders(new_user,new_client,new_menuitem):
    new_client.force_authenticate(user=new_user)
    myorder=Order.objects.create(user=new_user, total=20,date=timezone.now().date(),payment_state=Status.COMPLETED)
    first_user_response=new_client.get('/api/orders')
    other_user=User.objects.create_user(username='other_user')
    new_client.force_authenticate(user=other_user)
    second_user_response=new_client.get('/api/orders')
    assert first_user_response.data['count']==1
    assert second_user_response.data['count']==0
    assert first_user_response.data['count']!=second_user_response.data['count']
    assert first_user_response.data['results'][0]['user']==new_user.id

@pytest.mark.django_db
def test_manager_assigns_delivery_crew(new_client,manager_user,deliverycrew_user,new_user):
    myorder=Order.objects.create(user=new_user, total=20,date=timezone.now().date())
    new_client.force_authenticate(user=manager_user)
    myresponse=new_client.patch(f'/api/orders/{myorder.id}',data={'delivery_crew':deliverycrew_user.id})
    assert myresponse.status_code==status.HTTP_200_OK

@pytest.mark.django_db
def test_delivery_crew_can_change_order_status(deliverycrew_user,new_client,new_user):
    myorder=Order.objects.create(user=new_user, total=20,delivery_crew=deliverycrew_user,date=timezone.now().date(),payment_state=Status.COMPLETED)
    new_client.force_authenticate(user=deliverycrew_user)
    myresponse=new_client.patch(f'/api/orders/{myorder.id}',data={'status':True})
    assert myresponse.status_code==status.HTTP_200_OK
    myorder.refresh_from_db()
    assert myorder.status==True

@pytest.mark.django_db
def test_delivery_crew_cannot_change_order_price(deliverycrew_user,new_client,new_user):
    myorder=Order.objects.create(user=new_user, total=20,delivery_crew=deliverycrew_user,date=timezone.now().date())
    new_client.force_authenticate(user=deliverycrew_user)
    myresponse=new_client.patch(f'/api/orders/{myorder.id}',data={'total':0})
    assert myresponse.status_code==status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_delivery_crew_can_view_order(deliverycrew_user,new_client,new_user):
    Order.objects.create(user=new_user, total=20,delivery_crew=deliverycrew_user,date=timezone.now().date())
    new_client.force_authenticate(user=deliverycrew_user)
    myresponse=new_client.get('/api/orders')
    assert myresponse.status_code==status.HTTP_200_OK

@pytest.mark.django_db
def test_delivery_crew_cannot_see_other_orers(deliverycrew_user,new_client,new_user):
    myorder=Order.objects.create(user=new_user, total=20,delivery_crew=deliverycrew_user,date=timezone.now().date(),payment_state=Status.COMPLETED)
    new_client.force_authenticate(user=deliverycrew_user)
    myresponse=new_client.get('/api/orders')
    assert myresponse.status_code==status.HTTP_200_OK
    assert myresponse.data['count']==1
    otherdeliverycrew=User.objects.create_user(username='othercrew')
    deliverycrewgroup,_=Group.objects.get_or_create(name='Delivery crew')
    otherdeliverycrew.groups.add(deliverycrewgroup)
    new_client.force_authenticate(user=otherdeliverycrew)
    myresponse=new_client.get('/api/orders')
    assert myresponse.status_code==status.HTTP_200_OK
    assert myresponse.data['count']==0
