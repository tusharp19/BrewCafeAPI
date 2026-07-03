from django.urls import path
from LittleLemonAPI.views import SingleCategoryView,CategoryView,SingleOrderView,OrderView,MenuItemView, SingleMenuItemView,ManagerView,ManagerDeleteView,DeliveryCrewView,DeliveryCrewDeleteView,CartView

urlpatterns=[
    path('menu-items',MenuItemView.as_view()),
    path('menu-items/<int:pk>',SingleMenuItemView.as_view()),
    path('groups/manager/users',ManagerView.as_view()),
    path('groups/manager/users/<int:pk>',ManagerDeleteView.as_view()),
    path('groups/delivery-crew/users', DeliveryCrewView.as_view()),
    path('groups/delivery-crew/users/<int:pk>', DeliveryCrewDeleteView.as_view()),
    path('cart/menu-items',CartView.as_view()),
    path('orders',OrderView.as_view()),
    path('orders/<int:pk>',SingleOrderView.as_view()),
    path('categories',CategoryView.as_view()),
    path('categories/<int:pk>',SingleCategoryView.as_view()),
]