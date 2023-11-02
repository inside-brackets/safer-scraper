import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

states_list = ['AL ', 'AK ', 'AS ', 'AZ ', 'AR ', 'CA ', 'CO ', 'CT ', 'DE ', 'DC ', 'FM ', 'FL ', 'GA ', 'GU ', 'HI ', 'ID ', 'IL ',
               'IN ', 'IA ', 'KS ', 'KY ', 'LA ', 'ME ', 'MH ', 'MD ', 'MA ', 'MI ', 'MN ', 'MS ', 'MO ', 'MT ', 'NE ', 'NV ', 'NH ',
               'NJ ', 'NM ', 'NY ', 'NC ', 'ND ', 'MP ', 'OH ', 'OK ', 'OR ', 'PW ', 'PA ', 'PR ', 'RI ', 'SC ', 'SD ', 'TN ', 'TX ',
               'UT ', 'VT ', 'VI ', 'VA ', 'WA ', 'WV ', 'WI ', 'WY ']

operation_class_check = ['Migrant', 'U.S. Mail', "Fed. Gov't", "State Gov't", "Local Gov't", 'Indian Nation']
cargo_carried_check = ['Motor Vehicles', 'Household Goods', 'Drive/Tow away', 'Mobile Homes', 'Liquids/Gases', 'Intermodal Cont.', 'Passengers',
                       'Oilfield Equipment', 'Garbage/Refuse', 'US Mail', 'Chemicals', 'Water Well']
field_names = ["mc_number", "dba_name", "company_name", "address", "phone_number", "usdot_number", "power_units", "email", "c_status", "cargo_carried"]


def transform(entity):
    new_entity = {
        "mc_number": "",
        "company_name": entity['Legal Name'],
        "dba_name": entity['Legal Name'],
        "address": entity['Physical Address'],
        "phone_number": entity['Phone'],
        "usdot_number": entity['USDOT Number'],
        "power_units": entity['Power Units'],
        "email": "",
        "c_status": "unassigned",
        "cargo_carried": entity['cargo_carried'],
    }
    try:
        new_entity['email'] = entity['email']
    except:
        pass
    return new_entity


def extract(page):
    try:
        # extracting fields
        entity = {}
        for i in range(2, 13):
            field_name = page.find_element(By.CSS_SELECTOR,'center tr:nth-child(' + str(i) + ') .querylabel').text
            field_value = page.find_element(By.CSS_SELECTOR,
                'p+ center tr:nth-child(' + str(i) + ') .querylabelbkg+ .queryfield').text
            entity[field_name.replace(":", "")] = field_value

        # clean entities
        for key in entity.keys():
            entity[key] = entity[key].strip()
            entity[key] = entity[key].replace("\n", " ")



        # cargo carried:
        cargo_carried = []
        for i in range(1, 4):
            for j in range(2, 12):
                if i == 3 and j == 11:
                    continue
                field_name = page.find_element(By.CSS_SELECTOR,
                    'tr:nth-child(19) tr td:nth-child(' + str(i) + ') tr:nth-child(' + str(j) + ') font').text
                field_value = page.find_element(By.CSS_SELECTOR,
                    'tr:nth-child(19) tr td:nth-child(' + str(i) + ') tr:nth-child(' + str(j) + ') .queryfield').text
                if field_value == 'X':
                    cargo_carried.append(field_name)
        entity['cargo_carried'] = cargo_carried
        # check if carrier is authorized
        try:
            page.find_element_by_xpath("//font[contains(concat(' ',normalize-space(@color),' '),'red')]")
            return entity
        except:
            pass

        # extract email
        page.find_element_by_xpath("//a[text()='SMS Results']").click()
        try:
            page.find_element_by_xpath("//a[text()='Carrier Registration Details']").click()
        except TimeoutException:
            print(" Loading took too much time!")
        try:
            entity["email"] = WebDriverWait(page, 10).until(EC.presence_of_element_located((By.XPATH, "//label[contains(text(),'Email')]/following-sibling::span"))).text
        except TimeoutException:
            print(" Loading took too much time!")
        return entity
    except:
        return -1 # return error code


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def check_callable(page):
    is_callable = True
    entity = extract(page)
    if entity != -1:
        if 'CARRIER' not in entity.get('Entity Type'):
            is_callable = False
        if 'AUTHORIZED FOR Property' not in entity.get('Operating Status'):
            is_callable = False
        if not any(state in entity.get('Physical Address') for state in states_list):
            is_callable = False
        # if len(intersection(entity.get('operation_class'), operation_class_check)) != 0:
        #     is_callable = False
        # if len(intersection(entity.get('cargo_carried'), cargo_carried_check)) != 0:
        #     is_callable = False
        return is_callable, transform(entity)
    else:
        return False, entity


def save_entity(page, mc):
    is_callable, entity = check_callable(page)
    if entity == -1:
        return -1  # for not scraping error
    if is_callable:
        entity['mc_number'] = str(mc)
        with open(r'./files/carriers.csv', 'a', newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writerow(entity)
        return 0  # for no errors
    else:
        return -2  # for not callable
    # save data to a file
