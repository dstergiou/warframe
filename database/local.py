import csv


def get_item_id_from_file(item: str) -> str:
    """
    Find the warframe.warframe_market ID from the local database

    Args:
        item (str): Item name (e.g. mirage_prime_systems)

    Returns:
        str: Item ID as defined on warframe.warframe_market (e.g. 5a2feeb1c2c9e90cbdaa23d2)
    """

    with open('database/prime_items.db', 'r', newline='') as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            if item == row[0]:
                return row[1]
    return "Not found"
