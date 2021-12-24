from db import get_items_to_buy, get_items_to_sell, get_all_prime_items
from warframe_market import get_info_from_market, login_to_warframe_market, sell_to_market
from tqdm import tqdm
from operator import itemgetter


my_items = items_to_sell()
# first_item = list(my_items.keys())[0]
# orders, price = get_price_from_market(first_item)
# print(f'Found {orders} with lowest price {price}')

# all_items = list(my_items.items())
# results = []
# sum = 0

# for item in tqdm(all_items):
#     item_name = item[0]
#     price = get_price_from_market(item_name)
#     sum += price
#     results.append([item_name, price])
    
# scoring = sorted(results, key=itemgetter(1), reverse=True)

# print(scoring)
# print(f'Total: {sum}')

# sum = 0

# wanted = items_to_buy()
# for item in tqdm(wanted):
#     price = get_price_from_market(item)
#     sum += price
#     results.append([item, price])
    
# scoring = sorted(results, key=itemgetter(1), reverse=True)
# print(scoring)
# print(f'Total: {sum}')

# testids = all_prime_items()[:3]

# for item in testids:
#     print(get_info_from_market(item, 'id'))


def create_name_to_id_database():
    """
    Reads all prime items names and fetches their ID from Warframe market
    The ID is needed if we want to place orders
    """
    all_items = get_all_prime_items()[:10]
    rows = []
    for item in all_items:
        print(f'Processing: {item}')
        id = get_info_from_market(item, 'id')
        rows.append([item, id]) 



token = login_to_warframe_market()
sell_to_market(token, '59e203ce115f1d887cfd7ac6', 10000, 1)


# if __name__ == '__main__':
#     create_name_to_id_database()