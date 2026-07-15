from django.shortcuts import render, get_object_or_404
from rest_framework import generics,status
from rest_framework.response import Response
from .models import Status,MenuItem,Cart,Order,OrderItem,Category
from django.contrib.auth.models import Group,User
from .serializers import MenuItemSerializer,UserSerializer,CartSerializer,OrderSerializer,CategorySerializer
from .permissions import IsManager,OrderBelongsToUser
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.utils import timezone
from django.db import transaction
from .payment import PaymentInterface

class MenuItemView(generics.ListCreateAPIView):
    queryset=MenuItem.objects.all()
    serializer_class=MenuItemSerializer

    def get_queryset(self):
        category_name=self.request.query_params.get('category')
        to_price=self.request.query_params.get('to_price')
        queryset=MenuItem.objects.select_related('category')
        ordering = self.request.query_params.get('ordering')
        if category_name:
            queryset=queryset.filter(category__slug__iexact=category_name)
        if to_price:
            try:
                queryset=queryset.filter(price__lte=to_price)
            except ValueError:
                pass
        if ordering:
            ordering_fields = ordering.split(',')
            queryset = queryset.order_by(*ordering_fields)
        if not ordering:
            queryset=queryset.order_by('id')
        return queryset

    def get_permissions(self):
        if self.request.method=='GET':
            return []
        return [IsAuthenticated(),IsManager()]

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset=MenuItem.objects.all()
    serializer_class=MenuItemSerializer

    def get_permissions(self):
        if self.request.method=='GET':
            return []
        return [IsAuthenticated(),IsManager()]

class CategoryView(generics.ListCreateAPIView):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer

    def get_permissions(self):
        if self.request.method=='GET':
            return []
        return [IsAdminUser()]

class SingleCategoryView(generics.RetrieveDestroyAPIView):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[IsAdminUser]

class ManagerView(generics.ListCreateAPIView):
    queryset=User.objects.filter(groups__name='Manager')
    serializer_class=UserSerializer
    permission_classes=[IsAuthenticated,IsManager]
    
    def post(self,request,*args,**kwargs):
        username=request.data.get('username')
        if username:
            user=get_object_or_404(User,username=username)
            managers=Group.objects.get(name='Manager')
            managers.user_set.add(user)
            serializer=self.get_serializer(user)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response({'message':'Bad Input for Username.'},status=status.HTTP_400_BAD_REQUEST)



class ManagerDeleteView(generics.DestroyAPIView):
    queryset = User.objects.filter(groups__name='Manager')
    permission_classes = [IsAuthenticated, IsManager]

    def destroy(self, request, *args, **kwargs):
        user = self.get_object() 
        
        managers = Group.objects.get(name='Manager')
        managers.user_set.remove(user)
        
        return Response(
            {"detail": "User removed from Manager group."}, 
            status=status.HTTP_200_OK
        )

class DeliveryCrewView(generics.ListCreateAPIView):
    queryset=User.objects.filter(groups__name='Delivery crew')
    serializer_class=UserSerializer
    permission_classes=[IsAuthenticated,IsManager]
    
    def post(self,request,*args,**kwargs):
        username=request.data.get('username')
        if username:
            user=get_object_or_404(User,username=username)
            deliverycrew=Group.objects.get(name='Delivery crew')
            deliverycrew.user_set.add(user)
            serializer=self.get_serializer(user)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response({'message':'Bad Input for Username.'},status=status.HTTP_400_BAD_REQUEST)



class DeliveryCrewDeleteView(generics.DestroyAPIView):
    queryset = User.objects.filter(groups__name='Delivery crew')
    permission_classes = [IsAuthenticated, IsManager]

    def destroy(self, request, *args, **kwargs):
        user = self.get_object() 
        
        deliverycrew = Group.objects.get(name='Delivery crew')
        deliverycrew.user_set.remove(user)
        
        return Response(
            {"detail": "User removed from Delivery crew group."}, 
            status=status.HTTP_200_OK
        )

class CartView(generics.ListCreateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def delete(self,request,*args, **kwargs):
        items=self.get_queryset()
        items.delete()
        return Response(status=status.HTTP_200_OK)
    
    def post(self,request,*args,**kwargs):
        menuitem_id=request.data.get('menuitem_id')
        quantity=int(request.data.get('quantity',1))
        menuitem=get_object_or_404(MenuItem,id=menuitem_id)

        cart_queryset=Cart.objects.filter(user=request.user,menuitem=menuitem)
        if cart_queryset.exists():
            cart_item=cart_queryset.first()
            cart_item.quantity+=quantity
            cart_item.price= cart_item.quantity * menuitem.price
            cart_item.save()
        else:
            cart_item= Cart.objects.create(user=request.user,
                                           menuitem=menuitem,
                                           quantity=quantity,
                                           unit_price=menuitem.price,
                                           price=menuitem.price*quantity)
        serializer=self.get_serializer(cart_item)
        return Response(serializer.data,status=status.HTTP_201_CREATED)

class OrderView(generics.ListCreateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=OrderSerializer

    def get_queryset(self):
        if self.request.user.groups.filter(name='Manager').exists():
            queryset= Order.objects.filter(payment_state=Status.COMPLETED).select_related('user', 'delivery_crew')
        elif self.request.user.groups.filter(name='Delivery crew').exists():
            queryset= Order.objects.filter(payment_state=Status.COMPLETED).filter(delivery_crew=self.request.user).select_related('user','delivery_crew')
        else:
            queryset=Order.objects.filter(user=self.request.user,
                                          payment_state__in=[Status.COMPLETED, Status.FAILED]
                                          ).select_related('user','delivery_crew')
        
        status_param = self.request.query_params.get('status')
        date_param = self.request.query_params.get('date')
        
        if status_param is not None:
            # Safely handle string to boolean/integer conversion depending on how your model stores status
            queryset = queryset.filter(status=status_param)
            
        if date_param:
            queryset = queryset.filter(date=date_param)

        # 3. Manual Sorting Capability (e.g., ?ordering=-date or ?ordering=total)
        ordering = self.request.query_params.get('ordering')
        if ordering:
            ordering_fields = ordering.split(',')
            queryset = queryset.order_by(*ordering_fields)
        
        return queryset
    
    def post(self,request,*args,**kwargs):
        cart_queryset=Cart.objects.filter(user=request.user)
        if cart_queryset:
            total_price=0
            for item in cart_queryset:
                total_price+=item.price
            new_order=Order.objects.create(user=request.user,total=total_price,date=timezone.now().date())
            orderitem_list=[]
            for item in cart_queryset:
                new_orderitem=OrderItem(order=new_order,menuitem=item.menuitem,quantity=item.quantity,unit_price=item.unit_price,price=item.price)
                orderitem_list.append(new_orderitem)
            OrderItem.objects.bulk_create(orderitem_list)
            #Cart.objects.filter(user=request.user).delete()
            serializer=self.get_serializer(new_order)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        
        return Response(status=status.HTTP_404_NOT_FOUND)

class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=OrderSerializer

    def get_queryset(self):
        if self.request.user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        if self.request.user.groups.filter(name='Delivery crew').exists():
            return Order.objects.filter(delivery_crew=self.request.user)
        return Order.objects.filter(user=self.request.user)
    
    def update(self,request,*args,**kwargs):
        user=request.user
        order=self.get_object()
        if user.groups.filter(name='Manager').exists():
            update_keys=list(request.data.keys())
            allowed_keys=['delivery_crew','status']
            for key in update_keys:
                if key not in allowed_keys:
                    return Response({"detail": "You do not have permission to modify this order."}, status=status.HTTP_403_FORBIDDEN)
            if 'delivery_crew' in request.data:
                # If you pass an ID, grab the User instance for the delivery crew
                from django.contrib.auth.models import User
                try:
                    crew_user = User.objects.get(id=request.data['delivery_crew'])
                    order.delivery_crew = crew_user
                except User.DoesNotExist:
                    return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
            if 'status' in request.data:
                order.status = request.data['status']
            order.save()
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        
        if user.groups.filter(name='Delivery crew').exists():
            update_keys=list(request.data.keys())
            if len(update_keys)!=1 or update_keys[0]!='status':
                return Response(status=status.HTTP_403_FORBIDDEN)
            order.status=request.data['status']
            order.save()
            return Response(self.get_serializer(order).data, status=status.HTTP_200_OK)
        
        return Response({"detail": "You do not have permission to modify this order."}, status=status.HTTP_403_FORBIDDEN)
    
    def destroy(self,request,*args,**kwargs):
        user=request.user
        if user.groups.filter(name='Manager').exists():
            return super().destroy(request,*args,**kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)
    
class OrderPaymentView(generics.GenericAPIView):
    permission_classes=[IsAuthenticated,OrderBelongsToUser]
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_for_update()
    
    def post(self,request,*args,**kwargs):
        with transaction.atomic():
            order=self.get_object()
            self.check_object_permissions(request,order)
            if order.payment_state==Status.COMPLETED or order.payment_state==Status.PROCESSING:
                return Response(
                        data={'State': 'Error', 'Reason': 'Payment already processed or in progress.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
            token = request.data.get('token')
            if not token:
                return Response(
                    data={'error': 'Payment token is required.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            order.payment_state= Status.PROCESSING
            order.save()

        response=PaymentInterface.make_payment(order.id,order.total,token)
        if response['success']:
            with transaction.atomic():
                order.payment_state=Status.COMPLETED
                order.transaction_id=response['transaction_id']
                order.save()
                Cart.objects.filter(user=request.user).delete()
            return Response(data={'State':'Success'},status=status.HTTP_200_OK)
        else:
            with transaction.atomic():
                order=self.get_object()
                self.check_object_permissions(request, order)
                order.payment_state=Status.FAILED
                order.save()
            return Response(data={'State':'Failed', 'Reason':response['error_code']},
                            status=status.HTTP_400_BAD_REQUEST)