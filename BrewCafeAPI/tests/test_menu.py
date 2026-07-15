import pytest
from rest_framework import status
from BrewCafeAPI.models import Category,MenuItem

@pytest.mark.django_db
@pytest.mark.parametrize("desserts, mains", [
    (
        [('Chocolate Cake', 12.00),('Vanilla Cake', 9.00),('Plum Cake', 10.00)],
        [('Veg Pizza', 5.00),('Three Cheese Pizza', 6.50),('Red Pasta', 3.50),('White Pasta', 4.00),('Pink Pasta', 4.50)]
    )
])
def test_customer_can_access_menu_items_by_categories(new_client,new_category,desserts,mains):
    for title,price in desserts:
        MenuItem.objects.create(title=title, price=price, featured=False,category=new_category)
    mycategory=Category.objects.create(title='Main Course', slug='main-course')
    for title,price in mains:
        MenuItem.objects.create(title=title, price=price, featured=False,category=mycategory)
    dessert_items=new_client.get(f'/api/menu-items?category={new_category.slug}')
    maincourse_items=new_client.get(f'/api/menu-items?category={mycategory.slug}')
    assert dessert_items.status_code==status.HTTP_200_OK
    assert maincourse_items.status_code==status.HTTP_200_OK
    assert dessert_items.data['count']==3
    assert maincourse_items.data['count']==5
    assert maincourse_items.data['results'][0]['title']=='Veg Pizza'
    assert maincourse_items.data['next'] is not None

@pytest.mark.django_db
@pytest.mark.parametrize("item_list", [
    [("Chocolate Cake", 12.00),("Vanilla Cake", 9.00), ("Plum Cake", 13.00)]
])
def test_customer_can_sort_menu_items_by_price(new_category,new_client,item_list):
    for title,price in item_list:
        MenuItem.objects.create(title=title, price=price, featured=False,category=new_category)
    myresponse=new_client.get('/api/menu-items?ordering=price')
    result=myresponse.data['results']
    assert myresponse.status_code==status.HTTP_200_OK
    assert result[0]['title']=='Vanilla Cake'
    assert result[1]['title']=='Chocolate Cake'
    assert float(result[0]['price'])<=float(result[1]['price'])

@pytest.mark.django_db
@pytest.mark.parametrize("item_list", [
    [("Chocolate Cake", 12.00),("Vanilla Cake", 9.00), ("Plum Cake", 13.00),("Fruit Cake",10.00)]
])
def test_menu_items_are_paginated(new_category,new_client,new_user,item_list):
    for title,price in item_list:
        MenuItem.objects.create(title=title, price=price, featured=False,category=new_category)
    new_client.force_authenticate(user=new_user)
    myresponse=new_client.get('/api/menu-items')
    assert myresponse.status_code==status.HTTP_200_OK
    assert myresponse.data['count']==4
    assert len(myresponse.data['results'])<myresponse.data['count']
    assert myresponse.data['next'] is not None


@pytest.mark.django_db
def test_get_menu_items(new_client):
    myresponse=new_client.get('/api/menu-items')
    assert myresponse.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_single_menu_item(new_menuitem,new_client):
    myresponse=new_client.get(f'/api/menu-items/{new_menuitem.id}')
    assert myresponse.status_code == status.HTTP_200_OK
    assert myresponse.data['title'] == 'Fruit Cake'
    assert myresponse.data['category'] == new_menuitem.category.id


@pytest.mark.django_db
@pytest.mark.parametrize("user_fixture,expected_response,created",[
    ("new_admin",status.HTTP_201_CREATED,True),
    ("manager_user",status.HTTP_201_CREATED,True),
    ("new_user",status.HTTP_403_FORBIDDEN,False),
    ("deliverycrew_user",status.HTTP_403_FORBIDDEN,False),
    (None,status.HTTP_401_UNAUTHORIZED,False)
])
def test_user_group_adds_item(new_client,request,new_category,user_fixture,expected_response,created):
    if user_fixture:
        testuser=request.getfixturevalue(user_fixture)
        new_client.force_authenticate(user=testuser)
    
    testitem={'title':'Cake','price':10.0,'category':new_category.id}
    myresponse=new_client.post('/api/menu-items',data=testitem)
    assert myresponse.status_code == expected_response
    assert MenuItem.objects.filter(title='Cake').exists()==created

@pytest.mark.django_db
@pytest.mark.parametrize("user_fixture,expected_response,created",[
    ("new_admin",status.HTTP_201_CREATED,True),
    ("manager_user",status.HTTP_403_FORBIDDEN,False),
    ("new_user",status.HTTP_403_FORBIDDEN,False)
])
def test_user_group_add_categories(new_client,request,user_fixture,expected_response,created):
    testuser=request.getfixturevalue(user_fixture)
    new_client.force_authenticate(user=testuser)
    testcategory={'title':'Chinese','slug':'chinese'}
    myresponse=new_client.post('/api/categories',data=testcategory)
    assert myresponse.status_code==expected_response
    assert Category.objects.filter(title='Chinese').exists()==created


@pytest.mark.django_db
def test_manager_can_update_item_of_day(manager_user,new_client,new_menuitem):
    new_client.force_authenticate(user=manager_user)
    payload={'featured':True}
    myresponse=new_client.patch(f'/api/menu-items/{new_menuitem.id}',payload)
    assert myresponse.status_code==status.HTTP_200_OK
    new_menuitem.refresh_from_db()
    assert new_menuitem.featured==True