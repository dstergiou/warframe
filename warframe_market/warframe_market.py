import requests
import json

from dataclasses import dataclass
from time import sleep
from requests.exceptions import HTTPError

WARFRAME_MARKET_API = 'https://api.warframe.market/v1'
DEFAULT_SLEEP = 0.4

warframe_market_standard_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'JWT',
        'Accept': 'application/json',
        'auth_type': 'header',
        'language': 'en',
        'platform': 'pc',
    }


@dataclass
class ExistingPrimeOrder:
    """
    Existing Order representing a Prime Item
    Can also be used for standard items but the ducats value will be none
    """
    order_id: str
    quantity: int
    platinum: int
    item_id: str
    item_url: str
    ducats: int = None


@dataclass
class NewPrimeOrder:
    """
    New Order to be placed
    """
    item_id: str
    price: int
    quantity: int


def login_to_warframe_market(email: str, password: str) -> str:
    """
    Logins to warframe.warframe_market and returns a JWT token for authenticated calls

    Returns:
        str: JWT token needed for authenticated calls to warframe.warframe_market API
    """

    data = {
        'email': email,
        'password': password,
        'auth_type': 'header',
    }

    try:
        response = requests.post(f'{WARFRAME_MARKET_API}/auth/signin',
                                 headers=warframe_market_standard_headers, data=json.dumps(data))
        response.raise_for_status()
        authentication_token = response.headers["Authorization"]
        return authentication_token

    except HTTPError as http_err:
        print(f'HTTP Error occurred: {http_err}')
    except Exception as err:
        print(f'Error occurred: {err}')


def get_existing_orders(profile: str) -> list[ExistingPrimeOrder]:
    """
    Get all selling orders for profile from warframe.warframe_market API

    Args:
        profile (str, optional): Profile name on Warframe warframe_market. Defaults to PROFILE_NAME.

    Returns:
        List[ExistingPrimeOrder]: A list of ExistingOrders
    """

    try:
        response = requests.get(f'{WARFRAME_MARKET_API}/profile/{profile}/orders',
                                headers=warframe_market_standard_headers)
        response.raise_for_status()
        data = response.json()
        clean_json = data['payload']['sell_orders']
        existing_orders = []
        for line in clean_json:
            existing_orders.append(ExistingPrimeOrder(
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


def find_lowest_price_for_item(profile: str, item: str) -> int:
    """
    Returns the lowest price for an item on warframe.warframe_market

    Args:
        item (str): Name of the item (e.g. mirage_prime_systems)
        profile (str): Our profile name on warframe.market (so we don't undercut ourselves)

    Returns:
       int: Returns the lowest price
    """

    try:
        sleep(DEFAULT_SLEEP)
        response = requests.get(f'{WARFRAME_MARKET_API}/items/{item}/orders', headers=warframe_market_standard_headers)
        response.raise_for_status()
        data = response.json()
        orders = data['payload']['orders']
        lowest_price = 100000  # I assume nothing sells for this much!!!

        for order in orders:
            if order['order_type'] == 'sell' \
                    and order['user']['status'] == 'ingame' \
                    and order['user']['ingame_name'] != profile:

                if int(order['platinum']) < lowest_price:
                    lowest_price = int(order['platinum'])

        return lowest_price

    except HTTPError as http_err:
        print(f'HTTP Error occurred: {http_err}')
    except Exception as err:
        print(f'Error occurred: {err}')


def delete_existing_order(auth_token: str, order: ExistingPrimeOrder) -> str:
    """
    Deletes an existing warframe.warframe_market order

    Args:
        auth_token (str): JWT Authentication token
        order (ExistingPrimeOrder): Order to be updated

    Returns:
        str: Order ID of the deleted order
    """

    order_id = order.order_id
    authorization_header = {
        'Authorization': auth_token,
    }

    update_headers = warframe_market_standard_headers | authorization_header

    try:
        sleep(DEFAULT_SLEEP)
        response = requests.delete(f'{WARFRAME_MARKET_API}/profile/orders/{order_id}', headers=update_headers)
        response.raise_for_status()
        response_data = response.json()
        deleted_order = response_data['payload']['order_id']

        return deleted_order

    except HTTPError as http_err:
        print(f'HTTP Error occurred: {http_err}')
    except Exception as err:
        print(f'Error occurred: {err}')


def create_new_order(auth_token: str, item: NewPrimeOrder) -> str:
    """
    Sells an item on warframe.warframe_market

    Args:
        auth_token (str): JWT Token
        item (NewPrimeOrder): An object containing item_id, price and quantity
    Returns:
        str: Date that the sell order was accepted
    """

    authorization_header = {
        'Authorization': auth_token,
    }

    update_headers = warframe_market_standard_headers | authorization_header

    data = {
        'item_id': item.item_id,
        'order_type': 'sell',
        'platinum': item.price,
        'quantity': item.quantity,
    }
    
    mod_data = {
        'mod_rank' : 0,
    }

    try:
        sleep(DEFAULT_SLEEP)
        response = requests.post(f'{WARFRAME_MARKET_API}/profile/orders', headers=update_headers, data=json.dumps(data))
        response.raise_for_status()
        data = response.json()
        order_created = data['payload']['order']['creation_date']
        return order_created

    except HTTPError as http_err:
        print(f'HTTP Error occurred: {http_err}')
    except Exception as err:
        print(f'Error occurred: {err}')


def update_existing_order(auth_token: str, order: ExistingPrimeOrder, price: int) -> str:
    """
    Updates an existing warframe.warframe_market order

    Args:
        auth_token (str): JWT Authentication token
        order (ExistingPrimeOrder): Order to be updated
        price (int): Target price

    Returns:
        str: Timestamp of the updated order
    """

    order_id = order.order_id
    authorization_header = {
        'Authorization': auth_token,
    }

    update_headers = warframe_market_standard_headers | authorization_header

    data = {
        'platinum': price,
    }

    try:
        sleep(DEFAULT_SLEEP)
        response = requests.put(f'{WARFRAME_MARKET_API}/profile/orders/{order_id}',
                                headers=update_headers, data=json.dumps(data))
        response.raise_for_status()
        response_data = response.json()
        confirmation_date = response_data['payload']['order']['last_update']
        return confirmation_date

    except HTTPError as http_err:
        print(f'HTTP Error occurred: {http_err}')
    except Exception as err:
        print(f'Error occurred: {err}')


def get_item_id_from_market(item: str) -> str:
    """
    Return the id of an item when provided the name (e.g: hikou_prime_blueprint)

    Args:
        item (str): Item name (e.g: hikou_prime_blueprint)

    Returns:
        str: ID of the item on warframe.warframe_market (e.g: '5a2feeb1c2c9e90cbdaa23d2')
    """
    try:
        response = requests.get(f'{WARFRAME_MARKET_API}/items/{item}', headers=warframe_market_standard_headers)
        sleep(DEFAULT_SLEEP)
        response.raise_for_status()
        data = response.json()
        item_id = data['payload']['item']['id']
        return item_id

    except HTTPError as http_err:
        print(f'HTTP Error occurred: {http_err}')
    except Exception as err:
        print(f'Error occurred: {err}')



if __name__ == '__main__':
    # print(find_lowest_price_for_item('nekros_prime_systems', 'Kaeriyana'))
    print(get_existing_orders('Kaeriyana'))
