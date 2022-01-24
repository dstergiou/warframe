import os
import json

from dotenv import load_dotenv

from database.google_sheets import OwnedItem
from database.google_sheets import get_prime_items_to_sell, get_items_to_sell
from database.local import get_item_id_from_file
from database.query import find_most_expensive_items_to_sell

from warframe_market import warframe_market

# Load credentials for Warframe warframe_market
load_dotenv()
EMAIL = os.environ.get('EMAIL')
PASSWORD = os.environ.get('PASSWORD')
PROFILE_NAME = os.environ.get('PROFILE_NAME')

# Login to warframe.market
token = warframe_market.login_to_warframe_market(EMAIL, PASSWORD)

# Grab existing orders
print(f'Receiving orders...')
existing_orders = warframe_market.get_existing_orders(PROFILE_NAME)

# If we have active sell orders, delete them
if len(existing_orders):
    print(f'Orders found: {len(existing_orders)}. Deleting')
    for existing_order in existing_orders:
        print(f'Deleting order {existing_order.order_id}')
        _ = warframe_market.delete_existing_order(token, existing_order)
else:
    print('No ordered to delete - skipping')

# Check inventory status
print(f'Preparing to find new orders - Standard items')
standard_items: OwnedItem = get_items_to_sell()
print(f'Preparing to find new orders - Prime items')
# prime_items: OwnedItem = get_prime_items_to_sell()
prime_items = {}
combined_items: OwnedItem = standard_items | prime_items

print(f'Querying warframe.market for current prices')
best_deals = find_most_expensive_items_to_sell(PROFILE_NAME, combined_items, 20)

for deal in best_deals:
    item_id = get_item_id_from_file(deal[0])
    if item_id == "Not found":
        item_id = warframe_market.get_item_id_from_market(deal[0])
    price = int(deal[1])
    quantity = int(deal[2])
    new_order = warframe_market.NewPrimeOrder(item_id, price, quantity)
    print(f'Adding order: {item_id}')
    _ = warframe_market.create_new_order(token, new_order)
