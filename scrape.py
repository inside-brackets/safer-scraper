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


def extract(page):
    try:
        # extracting fields
        entity = {}
        for i in range(2, 13):
            field_name = page.find_element_by_css_selector('center tr:nth-child(' + str(i) + ') .querylabel').text
            field_value = page.find_element_by_css_selector(
                'p+ center tr:nth-child(' + str(i) + ') .querylabelbkg+ .queryfield').text
            entity[field_name.replace(":", "")] = field_value
        entity['drivers'] = page.find_element_by_css_selector('tr:nth-child(11) .queryfield~ .querylabelbkg+ td').text

        # clean entities
        for key in entity.keys():
            entity[key] = entity[key].strip()
            entity[key] = entity[key].replace("\n", " ")

        # operation classification:
        operation_class = []
        for i in range(1, 4):
            for j in range(2, 6):
                if i == 3 and j == 5:
                    continue
                field_name = page.find_element_by_css_selector(
                    'tr:nth-child(14) tr td:nth-child(' + str(i) + ') tr:nth-child(' + str(j) + ') font').text
                field_value = page.find_element_by_css_selector(
                    'tr:nth-child(14) tr td:nth-child(' + str(i) + ') tr:nth-child(' + str(j) + ') .queryfield').text
                if field_value == 'X':
                    operation_class.append(field_name)
        entity['operation_class'] = operation_class

        # Carrier Operation:
        carrier_operations = []
        for i in range(1, 4):
            field_name = page.find_element_by_css_selector('tr:nth-child(16) td:nth-child(' + str(i) + ') td font').text
            field_value = page.find_element_by_css_selector(
                'tr:nth-child(16) tr td:nth-child(' + str(i) + ') .queryfield').text
            if field_value == 'X':
                carrier_operations.append(field_name)
        entity['carrier_operations'] = carrier_operations

        # cargo carried:
        cargo_carried = []
        for i in range(1, 4):
            for j in range(2, 12):
                if i == 3 and j == 11:
                    continue
                field_name = page.find_element_by_css_selector(
                    'tr:nth-child(19) tr td:nth-child(' + str(i) + ') tr:nth-child(' + str(j) + ') font').text
                field_value = page.find_element_by_css_selector(
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
    call = True
    entity = extract(page)
    if entity != -1:
        if 'CARRIER' not in entity.get('Entity Type'):
            call = False
        if 'AUTHORIZED FOR Property' not in entity.get('Operating Status'):
            call = False
        if not any(state in entity.get('Physical Address') for state in states_list):
            call = False
        if len(intersection(entity.get('operation_class'), operation_class_check)) != 0:
            call = False
        if len(intersection(entity.get('cargo_carried'), cargo_carried_check)) != 0:
            call = False
        return call, entity
    else:
        return False, entity


def save_entity(page, mc):
    check, entity = check_callable(page)
    if entity == -1:
        return -1  # for not scraping error
    if check:
        entries = [str(mc)]
        for value in entity.values():
            entries.append(value)
        csv_file = open(r'./files/carriers.csv', 'a', newline='', encoding="utf-8")
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(entries)
        csv_file.close()
        return 0  # for no errors
    else:
        return -2  # for not callable
    # save data to a file
