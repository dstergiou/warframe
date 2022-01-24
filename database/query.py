from operator import itemgetter

from database.google_sheets import OwnedItem
from warframe_market import warframe_market


def find_most_expensive_items_to_sell(profile: str, item_list: OwnedItem, num: int = 20, ) -> list[list[str, int, int]]:
    """
    Go through the list of owned items and find the most expensive ones on warframe.warframe_market
    Since we have a limit of 100 orders, we will return 95 (in case we have non-prime orders going)

    Args:
        profile (str): Our profile name on warframe.market
        item_list (str): JSON file containing the results from "get_items_to_sell"
        num (int): Number of deals to return

    Returns:
        list[list[str, int, int]]: List of lists (e.g [[item1, price, quantity], [item2, price, quantity]])
    """

    deals_to_make = []
    for item in item_list:
        print(f'Checking {item}...')
        price = warframe_market.find_lowest_price_for_item(profile, item)
        quantity = item_list[item]
        deals_to_make.append([item, price, quantity])

    return sorted(deals_to_make, key=itemgetter(1), reverse=True)[:num]
