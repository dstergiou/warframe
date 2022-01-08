from db import get_items_to_buy, get_items_to_sell
from warframe_market import get_info_from_market, login_to_warframe_market, sell_to_market


if __name__ == '__main__':
    # Login to warframe market
    token = login_to_warframe_market()
    
    # Calculate what i need to buy
    # items_to_buy = get_items_to_buy()
    # for item in items_to_buy:
    #     id, price = get_info_from_market(item)
    #     print(f'{item}\t{price}')
    
    
    # Calculate what i can sell
    sell_list =
    items_to_sell = get_items_to_sell()
    for item, quantity in items_to_sell.items():
        # print(f'{item} - {quantity}')
        
        