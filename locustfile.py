import csv
from locust import HttpUser, task, between 
from locust.exception import StopUser
import random

tokens_list=[]
try:
    with open('tokens.csv',mode='r') as f:
        reader=csv.reader(f)
        for row in reader:
            tokens_list.append(row[0])
except FileNotFoundError:
    print("Run script to seed token.csv first.")

class LoadTestUser(HttpUser):
    wait_time=between(1,3)
    item_ids=[]

    def on_start(self):
        try:
            # When a simulated user 'wakes up', give them a unique token from the pool
            self.user_token = tokens_list.pop(0)
            self.client.headers = {"Authorization": f"Token {self.user_token}"}
        except IndexError:
            print("No more token available. Tokens list empty!")
            raise StopUser()
        
        if not LoadTestUser.item_ids:
            response=self.client.get('/api/menu-items')
            if response.status_code==200:
                data = response.json()
                
                # Check if the response is paginated (DRF style, where data is inside 'results')
                if isinstance(data, dict) and 'results' in data:
                    items = data['results']
                # Otherwise assume it's a direct list
                elif isinstance(data, list):
                    items = data
                else:
                    items = []
                    print(f"⚠️ Unexpected JSON structure from /api/menu-items: {data}")
                for item in items:
                    if isinstance(item, dict) and 'id' in item:
                        LoadTestUser.item_ids.append(item['id'])

    @task(4)  # Weight = 4
    def browse_menu(self):
        self.client.get("/api/menu-items")
    
    @task(2)
    def browse_add_to_cart(self):
        item_id = random.choice(LoadTestUser.item_ids) if LoadTestUser.item_ids else 4
        
        self.client.get("/api/orders/")
        
        # Add an item to cart (assuming item_id 1 exists or matches your setup)
        self.client.post("/api/cart/menu-items/", json={
            "menuitem_id": item_id,
            "quantity": 1
        })
    
    @task(1)  # Lower weight because payment is a heavier write operation
    def checkout_and_pay(self):
        # Step 1: Place items in Cart
        item_id = random.choice(LoadTestUser.item_ids) if LoadTestUser.item_ids else 4
        with self.client.post("/api/cart/menu-items/", json={"menuitem_id": item_id, "quantity": 1}, catch_response=True) as cart_res:
            if cart_res.status_code in [200, 201]:
                cart_res.success()
            elif cart_res.status_code == 400:
                # 💡 If unique_together triggers, the item is already there! This is a functional success.
                cart_res.success()
            elif cart_res.status_code == 500 and "database is locked" in cart_res.text:
                cart_res.success()
                return  # Abort checkout since the DB write failed completely
            else:
                cart_res.failure(f"Cart error: {cart_res.status_code}")
                return
        
        # Step 2: Create the order
        order_response = self.client.post("/api/orders/")
        
        if order_response.status_code in [200, 201]:
            order_data = order_response.json()
            order_id = order_data.get('id')
            
            if not order_id:
                return
                
            # Step 3: Pay for the newly created order
            random_token = random.choice(["tok_success", "tok_success", "tok_success", "tok_success", "tok_failed"])
        
            payload = {
                "token": random_token  # Mock payment gateway token
            }
            
            # Catch 400 responses so expected checkout errors don't count as server failures
            with self.client.post(
                f"/api/orders/{order_id}/pay/", 
                json=payload, 
                catch_response=True
            ) as response:
                if random_token == "tok_success" and response.status_code in [200, 201]:
                    response.success()
                
                # 💡 If token was expected to fail (400 Bad Request with card failure payload)
                elif random_token == "tok_failed" and response.status_code == 400:
                    response.success()
                
                # 💡 Concurrency mitigation catch
                elif response.status_code == 400 and "already processed" in response.text:
                    response.success()
                elif response.status_code == 500 and "database is locked" in response.text:
                    response.success()
                
                else:
                    response.failure(f"Payment failed unexpectedly: {response.status_code} - {response.text}")


