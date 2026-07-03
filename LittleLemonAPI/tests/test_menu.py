import pytest
from rest_framework import status
from LittleLemonAPI.models import Category,MenuItem

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
def test_admin_can_add_categories(new_admin,new_client):
    test_category={'title':'Salads','slug':'salads'}
    new_client.force_authenticate(user=new_admin)
    myresponse=new_client.post('/api/categories',data=test_category)
    assert myresponse.status_code==status.HTTP_201_CREATED
    assert Category.objects.filter(title='Salads').exists()==True

@pytest.mark.django_db
def test_admin_can_add_menu_items(new_admin,new_client,new_category):
    new_client.force_authenticate(user=new_admin)
    testitem={'title':'Banana Bread', 'price':3.00, 'featured':False,'category':new_category.id}
    myresponse=new_client.post('/api/menu-items',data=testitem)
    assert myresponse.status_code==status.HTTP_201_CREATED
    assert MenuItem.objects.filter(title='Banana Bread').exists()==True

@pytest.mark.django_db
def test_get_menu_items(new_client):
    myresponse=new_client.get('/api/menu-items')
    assert myresponse.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_item(new_client,new_category):
    test_item={'title':'Cake','price':10.0,'category':new_category.id}
    myresponse=new_client.post('/api/menu-items',data=test_item)
    assert myresponse.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_managers_can_create_item(manager_user,new_client,new_category):
    test_item={'title':'Cake','price':10.0,'category':new_category.id}
    new_client.force_authenticate(user=manager_user)
    myresponse=new_client.post('/api/menu-items',data=test_item)
    assert myresponse.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_get_single_menu_item(new_menuitem,new_client):
    myresponse=new_client.get(f'/api/menu-items/{new_menuitem.id}')
    assert myresponse.status_code == status.HTTP_200_OK
    assert myresponse.data['title'] == 'Fruit Cake'
    assert myresponse.data['category'] == new_menuitem.category.id


@pytest.mark.django_db
def test_non_manager_authenticated_user_cannot_create_item(new_client,new_category,new_user):
    new_client.force_authenticate(user=new_user)
    testitem={'title':'Cake','price':10.0,'category':new_category.id}
    myresponse=new_client.post('/api/menu-items',data=testitem)
    assert myresponse.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db 
def test_delivery_crew_cannot_create_item(new_client,new_category,deliverycrew_user):
    new_client.force_authenticate(user=deliverycrew_user)
    testitem={'title':'Cake','price':10.0,'category':new_category.id}
    myresponse=new_client.post('/api/menu-items',data=testitem)
    assert myresponse.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_manager_cannot_add_categories(new_client,manager_user):
    new_client.force_authenticate(user=manager_user)
    test_category={'title':'Chinese','slug':'chinese'}
    myresponse=new_client.post('/api/categories',data=test_category)
    assert myresponse.status_code==status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_customer_cannot_add_categories(new_client,new_user):
    new_client.force_authenticate(user=new_user)
    test_category={'title':'Chinese','slug':'chinese'}
    myresponse=new_client.post('/api/categories',data=test_category)
    assert myresponse.status_code==status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_manager_can_update_item_of_day(manager_user,new_client,new_menuitem):
    new_client.force_authenticate(user=manager_user)
    payload={'featured':True}
    myresponse=new_client.patch(f'/api/menu-items/{new_menuitem.id}',payload)
    assert myresponse.status_code==status.HTTP_200_OK
    new_menuitem.refresh_from_db()
    assert new_menuitem.featured==True