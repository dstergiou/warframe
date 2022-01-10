from db import get_items_to_buy, get_items_to_sell
from warframe_market import get_info_from_market, login_to_warframe_market, sell_to_market

MIN_PRICE = 10


def calculate_sell_price(price:int) -> int:
    if price <= MIN_PRICE:
        return 0
    else:
        return price - 1 

if __name__ == '__main__':
    # Login to warframe market
    token = login_to_warframe_market()
    
    # Calculate what i need to buy
    # items_to_buy = get_items_to_buy()
    # for item in items_to_buy:
    #     id, price = get_info_from_market(item)
    #     print(f'{item}\t{price}')
    
    
    # Calculate what i can sell
    sell_list = []
    items_to_sell = get_items_to_sell()
    for item, quantity in items_to_sell.items():
        item_id, price = get_info_from_market(item)
        calculated_price = calculate_sell_price(price)
        if calculated_price != 0:
            order = {
                'item' : item_id, 
                'item_name': item,
                'price': calculated_price, 
                'quantity' : quantity
            }
            sell_list.append(order)
    print(sell_list)