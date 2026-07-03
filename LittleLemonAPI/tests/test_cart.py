import pytest
from rest_framework import status
from LittleLemonAPI.models import Cart
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_customer_can_only_see_their_own_cart_items(new_user,new_client,new_menuitem):
    other_user=User.objects.create_user(username='other_user')
    item_qty=1
    item_unitprice=new_menuitem.price
    otheruser_cart=Cart.objects.create(user=other_user,
                        menuitem=new_menuitem,
                        quantity=item_qty,
                        unit_price=item_unitprice,
                        price=item_qty*item_unitprice)
    new_client.force_authenticate(user=new_user)
    myresponse=new_client.get('/api/cart/menu-items')
    assert myresponse.status_code==status.HTTP_200_OK
    assert myresponse.data['count']==0

@pytest.mark.django_db
def test_customer_can_see_their_cart(new_user,new_client,new_menuitem):
    item_qty=5
    item_up=new_menuitem.price
    total_itemprice=item_qty*item_up
    Cart.objects.create(user=new_user, menuitem=new_menuitem, 
                        quantity=item_qty, unit_price=item_up,
                        price=total_itemprice)
    new_client.force_authenticate(user=new_user)
    myresponse=new_client.get('/api/cart/menu-items')
    mydata=myresponse.data['results'][0]
    assert myresponse.status_code==status.HTTP_200_OK
    assert mydata['menuitem'].get('title')==new_menuitem.title
    assert mydata['quantity']==item_qty
    assert float(mydata['price'])==total_itemprice
