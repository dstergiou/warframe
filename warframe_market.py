import requests
import time
import json
import os
import csv
from dotenv import load_dotenv
from requests.exceptions import HTTPError
from db import get_items_to_sell, get_items_to_buy, get_all_prime_items

URL = 'https://api.warframe.market/v1'
load_dotenv()

def get_info_from_market(item:str):
    
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
    """
    Sells an item on warframe.market
    
    Args:
        token (str): JWT Token
        id (str): Warframe.market ID for the item to be sold
        price (int): Platinum price
        quantity (int): Quantity

    Returns:
        str: Date that the sell order was accepted
    """
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
        time.sleep(0.4)
        data = response.json()
        order_created = data['payload']['order']['creation_date']
        return order_created
    
    except HTTPError as http_err:
        print(f'HTTP Error occured: {http_err}')
    except Exception as err:
        print(f'Error occured: {err}')

def get_id_from_market(item):
    headers = {
        'accept': 'application/json',
        'platform': 'pc',
    }

    try:
        response = requests.get(f'{URL}/items/{item}', headers=headers)
        time.sleep(0.4)
        response.raise_for_status()
        data = response.json()
    except HTTPError as http_err:
        print(f'HTTP Error occured: {http_err}')
    except Exception as err:
        print(f'Error occured: {err}')
           
    item_id = data['payload']['item']['id']
    return item_id
    
    
if __name__ == '__main__':
    # pass
    token = login_to_warframe_market() 
    # print(get_info_from_market('mirage_prime_systems'))
    # print(sell_to_market(token, '5a2feeb1c2c9e90cbdaa23d2', 1000, 1))
    # print(get_items_to_sell())
    
    # primes = get_items_to_sell()
    # for key in primes:
    #     item_id = get_id_from_market(key)
    #     price = get_info_from_market(key)
    #     print(f'{key},{item_id},{primes[key]}, {price}')

    # print(sell_to_market(token,'5a4a4036dd791301749996ca', 10, 1))
    
    # with open('orders.csv') as csv_file:
    #     csv_reader = csv.reader(csv_file, delimiter=',')
    #     for row in csv_reader:
    #         print(sell_to_market(token, row[1], row[3], row[2]))
    with open('items.db', 'w', newline='') as f:
        writer = csv.writer(f)
        for item in get_all_prime_items():
            row = [item, get_id_from_market(item)]
            writer.writerow(row)