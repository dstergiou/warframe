import requests
import time
import json
import os
from dotenv import load_dotenv
from requests.exceptions import HTTPError

URL = 'https://api.warframe.market/v1'
load_dotenv()

def get_info_from_market(item:str, info:str):  
    
    headers = {
        'accept': 'application/json',
        'platform': 'pc',
    }

    try:
        response = requests.get(f'{URL}/items/{item}/orders', headers=headers)
        time.sleep(0.4)
        response.raise_for_status()
        data = response.json()
    except HTTPError as http_err:
        print(f'HTTP Error occured: {http_err}')
    except Exception as err:
        print(f'Error occured: {err}')
        
    orders = data['payload']['orders']
    
    if info == 'id':
        item_id = data['payload']['orders'][0]['id']
        return item_id

    if info == 'price':
        lowest_price = 10000
        for order in orders:
            if order['order_type'] == 'sell' and order['user']['status'] == 'ingame':
                if int(order['platinum']) < lowest_price:
                    lowest_price = int(order['platinum'])
        return lowest_price
             
def login_to_warframe_market() -> str: 
    
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'JWT',
        'Accept': 'application/json',
        'auth_type' : 'header',
        'language' : 'en',
        'platform' : 'pc',
    }
    
    data = {
        'email' : os.environ.get('EMAIL'),
        'password' : os.environ.get('PASSWORD'),
        'auth_type' : 'header',
    }
    
    try:
        response = requests.post(f'{URL}/auth/signin', headers=headers, data=json.dumps(data))
        response.raise_for_status()
        token = response.headers["Authorization"]
        return token
            
    except HTTPError as http_err:
        print(f'HTTP Error occured: {http_err}')
    except Exception as err:
        print(f'Error occured: {err}')
        
def sell_to_market(token:str, id:str, price:int, quantity:int)->str:
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : token,
        'Accept': 'application/json',
        'auth_type' : 'header',
        'language' : 'en',
        'platform' : 'pc',
    }
           
    data = {
        'item_id' : id,
        'order_type' : 'sell',
        'platinum' : price,
        'quantity' : quantity,
    }
    
    try:
        response = requests.post(f'{URL}/profile/orders', headers=headers, data=json.dumps(data))
        response.raise_for_status()
        data = response.json()
        order_created = data['payload']['order']['creation_date']
        return order_created
    except HTTPError as http_err:
        print(f'HTTP Error occured: {http_err}')
    except Exception as err:
        print(f'Error occured: {err}')

if __name__ == '__main__':
    token = login_to_warframe_market()
    # print(get_price_from_market('mirage_prime_systems'))
    print(sell_to_market(token, '5a2feeb1c2c9e90cbdaa23d2', 1000, 1))
