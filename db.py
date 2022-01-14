import gspread
from sqlite3  import Error
from typing import TypedDict

class OwnedItem(TypedDict):
    item_name: str
    quantity: int

DB_FILE = 'warframe.db'   
SHEET = 'Warframe'
WORKSHEET = 'Prime' 
RANGE = 'A2:R109'
KEY = 'sheets.json'

def read_data_from_sheet(sheet:str=SHEET, worksheet:str=WORKSHEET, range:str=RANGE) -> list[list[str]]:
    """
    Reads the Google Sheet that contains the information on prime items

    Args:
        sheet (str): Google Sheet name
        worksheet (str): Worksheet in the Google Sheet
        range (str): Range containing the values

    Returns:
        list[list[str]]: [description]
    """
    sa = gspread.service_account(filename=KEY)
    sheet = sa.open(sheet)
    worksheet = sheet.worksheet(worksheet)
    records = worksheet.get(range)
    return records

def get_all_prime_items() -> list[str]:
    """
    Returns names compatible with Warframe Market for the prime parts

    Returns:
        [list[str]]: List containing prime part names (e.g guandao_prime_blueprint)
    """
    records = read_data_from_sheet(sheet=SHEET, worksheet=WORKSHEET, range=RANGE)
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

def get_items_to_sell() -> OwnedItem:
    """
    Returns the names and quantity of prime parts that we can sell
    These are parts that we have already used / built
    
    Returns:
        OwnedItem: Item and and quantity (e.g 'zakti_prime_barrel': 4)
    """
    records = read_data_from_sheet(sheet=SHEET, worksheet=WORKSHEET, range=RANGE)
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

def get_items_to_buy() -> list[str]:
    """
    Returns a list of missing prime parts

    Returns:
        list[str]: List of missing prime parts (e.g. 'mag_prime_systems')
    """
    records = read_data_from_sheet(sheet=SHEET, worksheet=WORKSHEET, range=RANGE)
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
    
if __name__ == '__main__':
    # print(read_data_from_sheet())
    # db = create_db_connection()
    # create_db_table(db)
    # print(sheet_to_db(db))
    # print(get_items_to_buy())
    # primes = get_items_to_sell()
    # for key in primes:
    #     item_id, price = get_info_from_market(key)
    #     print(f'{key},{item_id},{primes[key]},{price}')
    
    print(get_items_to_sell())
    # pass