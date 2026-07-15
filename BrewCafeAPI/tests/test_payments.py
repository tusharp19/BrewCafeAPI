from unittest.mock import patch

import pytest
from rest_framework import status
from BrewCafeAPI.models import Status

@pytest.mark.django_db
@pytest.mark.parametrize("user,expected_response",[
    ("new_user",status.HTTP_200_OK),
    ("other_user",status.HTTP_404_NOT_FOUND),
    (None,status.HTTP_401_UNAUTHORIZED)
])
@patch('BrewCafeAPI.views.PaymentInterface.make_payment')
def test_user_allowed_to_pay(fake_payment,request,new_client,new_user_order,user,expected_response):
    if user:
        testuser=request.getfixturevalue(user)
        new_client.force_authenticate(testuser)
    fake_payment.return_value={
        'success': True,
        'transaction_id': 'MOCK_SUCCESS',
        'error_code': None
    }
    response=new_client.post(f'/api/orders/{new_user_order.id}/pay/',data={"token":"tok_success"})
    assert response.status_code==expected_response
    
@pytest.mark.django_db
@patch('BrewCafeAPI.views.PaymentInterface.make_payment')
def test_payment_success_path(fake_payment,new_client,new_user,new_user_order):
    fake_payment.return_value={
        'success': True,
        'transaction_id': 'MOCK_SUCCESS',
        'error_code': None
    }
    new_client.force_authenticate(new_user)
    response=new_client.post(f'/api/orders/{new_user_order.id}/pay/',data={"token":"tok_success"})
    assert response.status_code==status.HTTP_200_OK
    assert response.data['State']=='Success'
    new_user_order.refresh_from_db()
    assert new_user_order.payment_state==Status.COMPLETED
    assert new_user_order.transaction_id == 'MOCK_SUCCESS'

@pytest.mark.django_db
@patch('BrewCafeAPI.views.PaymentInterface.make_payment')
def test_payment_fail_path(fake_payment,new_client,new_user,new_user_order):
    fake_payment.return_value={
        'success': False,
        'transaction_id': None,
        'error_code': 'CONNECTION_TIMEOUT'
    }
    new_client.force_authenticate(new_user)
    response=new_client.post(f'/api/orders/{new_user_order.id}/pay/',data={"token":"tok_failed"})
    assert response.status_code==status.HTTP_400_BAD_REQUEST
    assert response.data['State']=='Failed'
    assert response.data['Reason']=='CONNECTION_TIMEOUT'

@pytest.mark.django_db
@patch('BrewCafeAPI.views.PaymentInterface.make_payment')
def test_payment_path_spy(fake_payment,new_client,new_user,new_user_order):
    fake_payment.return_value={
        'success': False,
        'transaction_id': None,
        'error_code': 'CONNECTION_TIMEOUT'
    }
    test_token={"token":"tok_failed"}
    new_client.force_authenticate(new_user)
    response=new_client.post(f'/api/orders/{new_user_order.id}/pay/',data=test_token)
    
    fake_payment.assert_called_with(
        new_user_order.id, 
        new_user_order.total, 
        "tok_failed"
    )
    
    called_with_args,called_with_kwargs= fake_payment.call_args
    assert called_with_args[0] == new_user_order.id
    assert called_with_args[1] == new_user_order.total
    assert called_with_args[2] == 'tok_failed'