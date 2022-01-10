
import requests
import os
import json

from datetime import datetime
from dataclasses import dataclass
from typing import List
from requests.api import get
from requests.exceptions import HTTPError
from dotenv import load_dotenv
from logging import error
from time import sleep
 
# Config

# We won't list or sell anything under this much platinum
MIN_PRICE = 10                

# Base URL for Warframe market
URL = 'https://api.warframe.market/v1'  

# Name of profile on Warframe.market
PROFILE_NAME = 'Kaeriyana'

# Load credentials for Warframe market
load_dotenv()
EMAIL = os.environ.get('EMAIL')
PASSWORD = os.environ.get('PASSWORD')


# Generic headers for warframe.market API
headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'JWT',
        'Accept': 'application/json',
        'auth_type' : 'header',
        'language' : 'en',
        'platform' : 'pc',
    }

@dataclass
class ExistingOrder:
    order_id: str
    quantity: int
    platinum: int
    item_id: str
    item_url: str
    
    
def get_listed_orders(profile:str = PROFILE_NAME) -> List[ExistingOrder]:
    """
    Get all selling orders for profile from warframe.market API

    Args:
        profile (str, optional): Profile name on Warframe market. Defaults to PROFILE_NAME.

    Returns:
        List[ExistingOrder]: A list of ExistingOrders
    """
    
    headers = {
        'accept': 'application/json',
        'platform': 'pc',
    }

    try:
        response = requests.get(f'{URL}/profile/{PROFILE_NAME}/orders', headers=headers)
        response.raise_for_status()
        data = response.json()
    except HTTPError as http_err:
        print(f'HTTP Error occured: {http_err}')
    except Exception as err:
        print(f'Error occured: {err}')
    
    clean_json = data['payload']['sell_orders']
    orders = []
    
    for line in clean_json:
        orders.append(ExistingOrder(
            line['id'],
            line['quantity'],
            line['platinum'],
            line['item']['id'],
            line['item']['url_name'] 
        ))
    
    return orders
    
def find_lowest_price_for_item(order: ExistingOrder) -> list:
    """
    Scan the warfame.market API for an item and return the lowest price the item
    sells for by a player who is currently "in game".

    Args:
        order (ExistingOrder): An ExistingOrder instance

    Returns:
        list: A list of the 5 lowest prices
    """
    
    headers = {
        'accept': 'application/json',
        'platform': 'pc',
    }

    try:
        response = requests.get(f'{URL}/items/{order.item_url}/orders', headers=headers)
        response.raise_for_status()
        data = response.json()
    except HTTPError as http_err:
        print(f'HTTP Error occured: {http_err}')
    except Exception as err:
        print(f'Error occured: {err}')
    
    orders = data['payload']['orders']
    lowest_price = 100000          # I assume nothing sells for this much!!!
    price_list = []
    
    for order in orders:
        if order['order_type'] == 'sell' and order['user']['status'] == 'ingame':
            price_list.append(order['platinum'])
            if int(order['platinum']) < lowest_price:
                lowest_price = int(order['platinum'])
                
                
    # return lowest_price
    return sorted(price_list)[:5]
    
def calculate_new_sell_price(current_prices: list, min_price: int = MIN_PRICE) -> int:
    """
    Return a price that undercuts the competition by 1p
    If the undercutting price is below MIN_PRICE then return MIN_PRICE
    We don't want to sell for minimal platinum

    Args:
        current_prices (list): Lowest 5 prices found on warframe.market
        min_price (int, optional): Price we won't go below. Defaults to MIN_PRICE.

    Returns:
        int: Undercuttting price
    """
    
    if min(current_prices) -1 < min_price:
        return min(current_prices)
    
    return min(current_prices) - 1

def login_to_warframe_market(email: str = EMAIL, password: str = PASSWORD ) -> str:
    """
    Logins to warframe.market and returns a JWT token for authenticated calls

    Returns:
        str: JWT token needed for authenticated calls to warframe.market API
    """
    
    data = {
        'email' : email,
        'password' : password,
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

def update_existing_order(token: str, order: ExistingOrder, price: int) -> datetime:
    """
    Updates an existing warframe.market order

    Args:
        token (str): JWT Authentication token
        order (ExistingOrder): Order to be updated
        price (int): Target price

    Returns:
        str: Timestamp of the updated order
    """
    
    order_id = order.order_id
    authorization_header = {
          'Authorization' : token,
    }
    
    update_headers = headers | authorization_header
    
    data = {
        'platinum' : price,
    }
    
    try:
        sleep(0.4)
        response = requests.put(f'{URL}/profile/orders/{order_id}', headers=update_headers, data=json.dumps(data))
        response.raise_for_status()
        response_data = response.json()
        confirmation_date = response_data['payload']['order']['last_update']
        update_time = datetime.strptime(confirmation_date, "%Y-%m-%dT%H:%M:%S.%f%z") 
        return update_time
            
    except HTTPError as http_err:
        print(f'HTTP Error occured: {http_err}')
    except Exception as err:
        print(f'Error occured: {err}')



if __name__ == '__main__':
    while True:
        try:
            token = login_to_warframe_market()
            orders = get_listed_orders()
            
            for order in orders:
                lowest_price_on_market = find_lowest_price_for_item(order)
                target_price = calculate_new_sell_price(lowest_price_on_market)
                last_updated = update_existing_order(token, order, target_price)
                message = (
                    f'[CHECK], '
                    f'{datetime.now().strftime("%H:%M:%S")}, '
                    f'ITEM: {order.item_url}, '
                    f'PRICE: {order.platinum}, ' 
                    f'LOWEST: {min(lowest_price_on_market)}, '
                    f'TARGET: {target_price}, '
                    f'CONFIRM: {last_updated}'
                )
                print(message)
            sleep(1800)

        except Exception as error:
            print(f'Something went wrong: {error}')
            quit()