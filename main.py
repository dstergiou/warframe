
import requests
import os
import json
import csv
import math

from datetime import datetime
from dataclasses import dataclass
from typing import List, Union
from requests.api import get
from requests.exceptions import HTTPError
from dotenv import load_dotenv
from logging import error
from time import sleep
from operator import itemgetter
 
from db import get_items_to_sell
 
# Config

# We won't list or sell anything under this much platinum
MIN_PRICE = 10 

# Random placeholder price for items we intend to sell for ducats
DUCAT_PRICE = 421     
DUCAT_RATIO = 8 

# Default sleep time to not annoy the warframe.market API
DEFAULT_SLEEP = 0.4

# How many orders to create initially
DEFAULT_ORDERS = 10

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
        'Content-Type': 'application/json',
        'Authorization': 'JWT',
        'Accept': 'application/json',
        'auth_type': 'header',
        'language': 'en',
        'platform': 'pc',
    }


@dataclass
class ExistingOrder:
    order_id: str
    quantity: int
    platinum: int
    item_id: str
    item_url: str
    ducats: int


@dataclass
class NewOrder:
    item_id: str
    price: int
    quantity: int
    
    
def get_existing_orders(profile: str = PROFILE_NAME) -> List[ExistingOrder]:
    """
    Get all selling orders for profile from warframe.market API

    Args:
        profile (str, optional): Profile name on Warframe market. Defaults to PROFILE_NAME.

    Returns:
        List[ExistingOrder]: A list of ExistingOrders
    """
    
    local_headers = {
        'accept': 'application/json',
        'platform': 'pc',
    }

    try:
        response = requests.get(f'{URL}/profile/{profile}/orders', headers=local_headers)
        response.raise_for_status()
        data = response.json()
        clean_json = data['payload']['sell_orders']
        existing_orders = []
        for line in clean_json:
            existing_orders.append(ExistingOrder(
                line['id'],
                line['quantity'],
                line['platinum'],
                line['item']['id'],
                line['item']['url_name'],
                line['item'].get('ducats'),
            ))
        return existing_orders

    except HTTPError as http_err:
        print(f'HTTP Error occurred: {http_err}')
    except Exception as err:
        print(f'Error occurred: {err}')


def find_lowest_price_for_order(order: ExistingOrder) -> list[int]:
    """
    Scan the warfame.market API for an item and return the lowest price the item
    sells for by a player who is currently "in game".

    Args:
        order (ExistingOrder): An ExistingOrder instance

    Returns:
        list[int]: A list of the 5 lowest prices
    """
    
    local_headers = {
        'accept': 'application/json',
        'platform': 'pc',
    }

    try:
        response = requests.get(f'{URL}/items/{order.item_url}/orders', headers=local_headers)
        response.raise_for_status()
        data = response.json()
        orders = data['payload']['orders']
        lowest_price = 100000  # I assume nothing sells for this much!!!
        price_list = []

        for order in orders:
            if order['order_type'] == 'sell' \
                    and order['user']['status'] == 'ingame' \
                    and order['user']['ingame_name'] != PROFILE_NAME:

                price_list.append(order['platinum'])
                if int(order['platinum']) < lowest_price:
                    lowest_price = int(order['platinum'])

        return sorted(price_list)[:5]

    except HTTPError as http_err:
        print(f'HTTP Error occurred: {http_err}')
    except Exception as err:
        print(f'Error occurred: {err}')
    

def find_lowest_price_for_item(item: str) -> list[int]:
    """
    Returns the lowest price for an item on warframe.market

    Args:
        item (str): Name of the item (e.g. mirage_prime_systems)

    Returns:
       list[int]: Returns 5 lowest prices
    """
    
    local_headers = {
        'accept': 'application/json',
        'platform': 'pc',
    }

    try:
        sleep(DEFAULT_SLEEP)
        response = requests.get(f'{URL}/items/{item}/orders', headers=local_headers)
        response.raise_for_status()
        data = response.json()
        orders = data['payload']['orders']
        lowest_price = 100000  # I assume nothing sells for this much!!!
        price_list = []

        for order in orders:
            if order['order_type'] == 'sell' \
                    and order['user']['status'] == 'ingame' \
                    and order['user']['ingame_name'] != PROFILE_NAME:

                price_list.append(order['platinum'])
                if int(order['platinum']) < lowest_price:
                    lowest_price = int(order['platinum'])

        # return lowest_price
        return sorted(price_list)[:5]

    except HTTPError as http_err:
        print(f'HTTP Error occurred: {http_err}')
    except Exception as err:
        print(f'Error occurred: {err}')
    

def calculate_new_sell_price(current_prices: list, min_price: int = MIN_PRICE) -> int:
    """
    Return a price that undercuts the competition by 1p
    If the undercutting price is below MIN_PRICE then return MIN_PRICE
    We don't want to sell for minimal platinum

    Args:
        current_prices (list): Lowest 5 prices found on warframe.market
        min_price (int, optional): Price we won't go below. Defaults to MIN_PRICE.

    Returns:
        int: Undercutting price
    """
    
    avg = sum(current_prices) / len(current_prices)
    if avg - 1 < min_price:
        return min_price
    return round(math.floor(avg))


def login_to_warframe_market(email: str = EMAIL, password: str = PASSWORD) -> str:
    """
    Logins to warframe.market and returns a JWT token for authenticated calls

    Returns:
        str: JWT token needed for authenticated calls to warframe.market API
    """
    
    data = {
        'email': email,
        'password': password,
        'auth_type': 'header',
    }
    
    try:
        response = requests.post(f'{URL}/auth/signin', headers=headers, data=json.dumps(data))
        response.raise_for_status()
        authentication_token = response.headers["Authorization"]
        return authentication_token
            
    except HTTPError as http_err:
        print(f'HTTP Error occurred: {http_err}')
    except Exception as err:
        print(f'Error occurred: {err}')


def update_existing_order(auth_token: str, order: ExistingOrder, price: int) -> datetime:
    """
    Updates an existing warframe.market order

    Args:
        auth_token (str): JWT Authentication token
        order (ExistingOrder): Order to be updated
        price (int): Target price

    Returns:
        datetime: Timestamp of the updated order
    """
    
    order_id = order.order_id
    authorization_header = {
          'Authorization': auth_token,
    }
    
    update_headers = headers | authorization_header
    
    data = {
        'platinum': price,
    }
    
    try:
        sleep(DEFAULT_SLEEP)
        response = requests.put(f'{URL}/profile/orders/{order_id}', headers=update_headers, data=json.dumps(data))
        response.raise_for_status()
        response_data = response.json()
        confirmation_date = response_data['payload']['order']['last_update']
        update_time = datetime.strptime(confirmation_date, "%Y-%m-%dT%H:%M:%S.%f%z") 
        return update_time
            
    except HTTPError as http_err:
        print(f'HTTP Error occurred: {http_err}')
    except Exception as err:
        print(f'Error occurred: {err}')


def calculate_ducats_to_plat_ratio(order: ExistingOrder) -> float:
    """
    Calculates the ducats / platinum ratio

    Args:
        order (ExistingOrder): Order for which to calculate the ratio

    Returns:
        float: Ducats to Platinum ratio
    """
    if order.ducats is None:
        return DUCAT_RATIO + 1
    return round(order.ducats / order.platinum, 2)


def get_item_id_from_market(item: str) -> str:
    """
    Return the id of an item when provided the name (e.g: hikou_prime_blueprint)

    Args:
        item (str): Item name (e.g: hikou_prime_blueprint)

    Returns:
        str: ID of the item on warframe.market (e.g: '5a2feeb1c2c9e90cbdaa23d2')
    """
    try:
        response = requests.get(f'{URL}/items/{item}', headers=headers)
        sleep(DEFAULT_SLEEP)
        response.raise_for_status()
        data = response.json()
        item_id = data['payload']['item']['id']
        return item_id

    except HTTPError as http_err:
        print(f'HTTP Error occurred: {http_err}')
    except Exception as err:
        print(f'Error occurred: {err}')


def get_item_id_from_file(item: str) -> str:
    """
    Find the warframe.market ID from the local database

    Args:
        item (str): Item name (e.g. mirage_prime_systems)

    Returns:
        str: Item ID as defined on warframe.market (e.g. 5a2feeb1c2c9e90cbdaa23d2)
    """
    
    with open('items.db', 'r', newline='') as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            if item == row[0]:
                return row[1]
    return "Not found"


def create_new_order(auth_token: str, item: NewOrder) -> str:
    """
    Sells an item on warframe.market
    
    Args:
        auth_token (str): JWT Token
        item (NewOrder): An object containing item_id, price and quantity
    Returns:
        str: Date that the sell order was accepted
    """
    
    authorization_header = {
          'Authorization': auth_token,
    }
    
    update_headers = headers | authorization_header
           
    data = {
        'item_id': item.item_id,
        'order_type': 'sell',
        'platinum': item.price,
        'quantity': item.quantity,
    }
    
    try:
        sleep(DEFAULT_SLEEP)
        response = requests.post(f'{URL}/profile/orders', headers=update_headers, data=json.dumps(data))
        response.raise_for_status()
        data = response.json()
        order_created = data['payload']['order']['creation_date']
        return order_created
    
    except HTTPError as http_err:
        print(f'HTTP Error occurred: {http_err}')
    except Exception as err:
        print(f'Error occurred: {err}')


def find_most_expensive_items_to_sell(file: str, num: int = DEFAULT_ORDERS) -> list[list[str, int, int]]:
    """
    Go through the list of owned items and find the most expensive ones on warframe.market
    Since we have a limit of 100 orders, we will return 95 (in case we have non-prime orders going)

    Args:
        file (str): JSON file containing the results from "get_items_to_sell" from db.py
        num (int): Number of deals to return

    Returns:
        list[list[str, int, int]]: List of lists (e.g [[item1, price, quantity], [item2, price, quantity]])
    """
    
    deals_to_make = []
    data = json.loads(file)
    for item in data:
        print(f'Checking {item}...')
        price_list = find_lowest_price_for_item(item)
        price = min(price_list)
        quantity = data[item]
        deals_to_make.append([item, price, quantity])
            
    return sorted(deals_to_make, key=itemgetter(1), reverse=True)[:num]


def menu_menu() -> None:
    print(f'1. Create initial orders')
    print(f'2. Update existing orders')


def menu_initial_orders(num: int = DEFAULT_ORDERS) -> int:
    """
     Create the initial orders to be posted
     Args:
         num (int): Number of orders to be created

     Returns:
         int: Number of orders created
     """

    items_to_sell = get_items_to_sell()
    best_deals_to_make = find_most_expensive_items_to_sell(items_to_sell, num=num)
    order_counter = 0
    for deal in best_deals_to_make:
        item_id = get_item_id_from_file(deal[0])
        price = deal[1]
        quantity = deal[2]
        new_order = NewOrder(item_id=item_id, price=price, quantity=quantity)
        try:
            _ = create_new_order(token, new_order)
            order_counter += 1
        except Exception as e:
            print(f'Order was not created. Error: {e}')

    return order_counter


def menu_update_orders() -> None:
    """
     Updated existing orders

     """

    try:
        orders = get_existing_orders()

        if not len(orders):
            print(f'No orders found - quiting')
            quit()

        for order in orders:
            lowest_price_on_market = find_lowest_price_for_order(order)
            target_price = calculate_new_sell_price(lowest_price_on_market)
            dpr = calculate_ducats_to_plat_ratio(order)
            if dpr <= DUCAT_RATIO:
                target_price = DUCAT_PRICE
            _ = update_existing_order(token, order, target_price)
            action_message = (
                f'{datetime.now().strftime("%H:%M:%S")}, '
                f'ITEM: {order.item_url}, '
                f'PRICE: {order.platinum}, '
                f'LOWEST: {min(lowest_price_on_market)}, '
                f'TARGET: {target_price}, '
                f'DPR: {dpr}'
            )

            print(action_message)

    except Exception as e:
        print(f'Something went wrong: {e}')
        quit()


if __name__ == '__main__':
    try:
        token = login_to_warframe_market()
    except Exception as error:
        print(f'Login failed with error: {error}')

    menu_menu()
    menu_input = int(input('> '))
    match menu_input:
        case 1:
            menu_initial_orders()
            quit()
        case 2:
            menu_update_orders()
            quit()
