import time


class PaymentInterface:
    @staticmethod
    def make_payment(orderid:int,total:float,token:str):
        response={'success':False,'transaction_id':None,'error_code':None}
        time.sleep(0.20)
        if token=="tok_success":
            response['success']=True
            response['transaction_id']='QFert34Zdaju87909123m00uKp33'
            return response
        elif token=="tok_failed":
            response['error_code']='Incorrect Card'
            return response
        

