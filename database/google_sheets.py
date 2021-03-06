import gspread
from typing import TypedDict


class OwnedItem(TypedDict):
    item_name: str
    quantity: int


SHEET = 'Warframe'
PRIME_WORKSHEET = 'Prime' 
PRIME_RANGE = 'A2:R109'
ITEM_WORKSHEET = 'Items'
ITEM_RANGE = 'A1:B100'
MODS_WORKSHEET = 'Mods'
MODS_RANGE = 'A1:B100'
KEY = 'database/sheets.json'


def read_data_from_sheet(sheet: str = SHEET, worksheet: str = PRIME_WORKSHEET, cell_range: str = PRIME_RANGE) -> list[list[str]]:
    """
    Reads the Google Sheet that contains the information on prime items

    Args:
        sheet (str): Google Sheet name
        worksheet (str): Worksheet in the Google Sheet
        cell_range (str): Range containing the values

    Returns:
        list[list[str]]: [description]
    """
    sa = gspread.service_account(filename=KEY)
    sheet = sa.open(sheet)
    worksheet = sheet.worksheet(worksheet)
    records = worksheet.get(cell_range)
    return records


def get_all_prime_items() -> list[str]:
    """
    Returns names compatible with Warframe Market for the prime parts

    Returns:
        [list[str]]: List containing prime part names (e.g guandao_prime_blueprint)
    """
    records = read_data_from_sheet(sheet=SHEET, worksheet=PRIME_WORKSHEET, cell_range=PRIME_RANGE)
    all_items = []
        
    for row in records:      
        base_name = row[0].replace(" ", "_")
        blueprint = row[1]
        first_component = row[4]
        second_component = row[7]
        third_component = row[10]
        fourth_component = row[13]
    
        # Blueprint
        if len(blueprint):
            if base_name.lower() == 'kavasa':
                continue
            item_name = f'{base_name}_prime_{blueprint.replace(" ", "_")}'.lower()
            all_items.append(item_name)
        
        # First component
        if len(first_component):
            item_name = f'{base_name}_prime_{first_component.replace(" ", "_")}'.lower()
            all_items.append(item_name)
            
        # Second component
        if len(second_component):
            item_name = f'{base_name}_prime_{second_component.replace(" ", "_")}'.lower()
            all_items.append(item_name)
            
        # Third component
        if len(third_component):
            item_name = f'{base_name}_prime_{third_component.replace(" ", "_")}'.lower()
            all_items.append(item_name)

        # Fourth component
        if len(fourth_component):
            item_name = f'{base_name}_prime_{fourth_component.replace(" ", "_")}'.lower()
            all_items.append(item_name)

    return all_items


def get_prime_items_to_sell() -> OwnedItem:
    """
    Returns the names and quantity of prime parts that we can sell
    These are parts that we have already used / built
    
    Returns:
        str: Item and quantity (e.g 'zakti_prime_barrel': 4)
    """
    records = read_data_from_sheet(sheet=SHEET, worksheet=PRIME_WORKSHEET, cell_range=PRIME_RANGE)
    owned_items = {} 
        
    for row in records:
        if row[16] == 'BUILD':
            continue
        base_name = row[0].replace(" ", "_")
        blueprint = row[1]
        blueprint_quantity = int(row[2]) if len(row[2]) else 0
        first_component = row[4]
        first_component_quantity = int(row[5]) if len(row[5]) else 0
        second_component = row[7]
        second_component_quantity = int(row[8]) if len(row[8]) else 0
        third_component = row[10]
        third_component_quantity = int(row[11]) if len(row[11]) else 0
        fourth_component = row[13]
        fourth_component_quantity = int(row[14]) if len(row[14]) else 0

        # Blueprint
        if len(blueprint) and blueprint_quantity > 0:
            item_name = f'{base_name}_prime_{blueprint.replace(" ", "_")}'.lower()
            owned_items[item_name] = blueprint_quantity
            
        # First component
        if len(first_component) and first_component_quantity > 0:
            item_name = f'{base_name}_prime_{first_component.replace(" ", "_")}'.lower()
            owned_items[item_name] = first_component_quantity
                
        # Second component
        if len(second_component) and second_component_quantity > 0:
            item_name = f'{base_name}_prime_{second_component.replace(" ", "_")}'.lower()
            owned_items[item_name] = second_component_quantity
                
        # Third component
        if len(third_component) and third_component_quantity > 0:
            item_name = f'{base_name}_prime_{third_component.replace(" ", "_")}'.lower()
            owned_items[item_name] = third_component_quantity

        # Fourth component
        if len(fourth_component) and fourth_component_quantity > 0:
            item_name = f'{base_name}_prime_{fourth_component.replace(" ", "_")}'.lower()
            owned_items[item_name] = fourth_component_quantity

    return owned_items


def get_prime_items_to_buy() -> list[str]:
    """
    Returns a list of missing prime parts

    Returns:
        list[str]: List of missing prime parts (e.g. 'mag_prime_systems')
    """
    records = read_data_from_sheet(sheet=SHEET, worksheet=PRIME_WORKSHEET, cell_range=PRIME_RANGE)
    needed_items = []
    
    for row in records:
        if row[16] == 'YES':
            continue
        
        base_name = row[0].replace(" ", "_")
        blueprint = row[1]
        blueprint_quantity = int(row[2]) if len(row[2]) else -1
        first_component = row[4]
        first_component_quantity = int(row[5]) if len(row[5]) else -1
        second_component = row[7]
        second_component_quantity = int(row[8]) if len(row[8]) else -1
        third_component = row[10]
        third_component_quantity = int(row[11]) if len(row[11]) else -1
        fourth_component = row[13]
        fourth_component_quantity = int(row[14]) if len(row[14]) else 0

    # Blueprint
        if len(blueprint) and blueprint_quantity == 0:
            item_name = f'{base_name}_prime_{blueprint.replace(" ", "_")}'.lower()
            needed_items.append(item_name)
        
    # First component
        if len(first_component) and first_component_quantity == 0:
            item_name = f'{base_name}_prime_{first_component.replace(" ", "_")}'.lower()
            needed_items.append(item_name)
            
    # Second component
        if len(second_component) and second_component_quantity == 0:
            item_name = f'{base_name}_prime_{second_component.replace(" ", "_")}'.lower()
            needed_items.append(item_name)
            
    # Third component
        if len(third_component) and third_component_quantity == 0:
            item_name = f'{base_name}_prime_{third_component.replace(" ", "_")}'.lower()
            needed_items.append(item_name)

    # Fourth component
        if len(fourth_component) and fourth_component_quantity == 0:
            item_name = f'{base_name}_prime_{fourth_component.replace(" ", "_")}'.lower()
            needed_items.append(item_name)

    return needed_items


def get_items_to_sell() -> OwnedItem:
    """
    Returns the names and quantity of items that we can sell
    These are parts that we have already used / built

    Returns:
        str: Item and quantity (e.g 'epitaph set': 4)
    """
    records = read_data_from_sheet(sheet=SHEET, worksheet=ITEM_WORKSHEET, cell_range=ITEM_RANGE)
    owned_items = {}

    for row in records:
        base_name = row[0]
        quantity = int(row[1])

        if len(base_name) and quantity > 0:
            owned_items[base_name] = quantity

    return owned_items


def get_mods_to_sell() -> OwnedItem:
    """
    Returns the names and quantity of mods that we can sell

    Returns:
        str: Item and quantity (e.g 'flow': 4)
    """
    records = read_data_from_sheet(sheet=SHEET, worksheet=MODS_WORKSHEET, cell_range=MODS_RANGE)
    owned_items = {}

    for row in records:
        base_name = row[0]
        quantity = int(row[1])

        if len(base_name) and quantity > 0:
            owned_items[base_name] = quantity

    return owned_items


if __name__ == '__main__':
    pass
