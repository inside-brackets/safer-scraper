from selenium import webdriver
from scrape import *
from send_emails import *
import pandas as pd
# import pyttsx3
# import chromedriver_autoinstaller


# is called in start_searching method
def search(mc):
    driver.get("https://safer.fmcsa.dot.gov/CompanySnapshot.aspx")
    driver.find_element_by_xpath('//input[@id=2]').click()
    driver.find_element_by_xpath('//input[@id=4]').send_keys(mc)
    driver.find_element_by_xpath('//input[@value="Search"]').click()
    return driver


# is called in start_searching method
def notify():
    print("\nThere maybe something wrong with your internet or proxy. Please check and retry after few minutes.")
    delete_last_3mc()
    # engine = pyttsx3.init()
    # voices = engine.getProperty('voices')
    # engine.setProperty('voice', voices[1].id)
    # engine.setProperty('rate', 150)
    # engine.say("\nGive it a rest and run after deleting last 3 entries in the start mc file")
    # engine.runAndWait()


# is called in promt_for_start_mc method
def get_last_mc():
    file_r = open('./files/start_mc.csv', 'r')
    data = pd.read_csv(file_r)
    searched_mc = data['MC'].to_numpy()
    last_mc = int(searched_mc[-1])  # where to start searching
    file_r.close()
    return last_mc


# is called in main
def start_mc_menu():
    # chromedriver_autoinstaller.install()
    try:
        last_mc = get_last_mc()
        print(f' Continuing where you left off. (At: {last_mc})')
        start = last_mc + 1
    except:
        while True:
            start = int(input("\n Enter a Start MC: "))
            if isinstance(start, int):
                break
            else:
                print("Invalid MC")
    try:
        global driver
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument("--disable-extensions")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome("chromedriver.exe", options=options)
    except Exception as e:
        print(" ", e)
    else:
        start_searching(start)


# search mc's
def start_searching(start):
    retry = 0
    counter_504 = 0
    break_outer = False
    for i in range(start, 9999999):
        csv_file = open('./files/start_mc.csv', 'a', newline='', encoding="utf-8")  # open file to save the last search mc
        csv_writer = csv.writer(csv_file)

        # search current mc
        while True:
            try:
                search(i)
            except:
                if retry == 0:
                    print('MC:' + str(i) + ' Status: 504')
                    retry += 1
                elif retry <= 2:
                    print(" retrying: " + str(i) + " try: " + str(retry))
                    retry += 1
                else:
                    retry = 0
                    counter_504 += 1
                    if counter_504 == 3:
                        break_outer = True
                    csv_writer.writerow([str(i), '504'])
                    break

            # if data exists
            else:
                try:
                    record = driver.find_element_by_xpath('//i').text
                except:
                    print(' MC:' + str(i) + ' Status: "i" element not found')
                else:
                    # if records exists call save
                    if record == "Company Snapshot":
                        save_status = save_entity(driver, i)
                        if save_status == 0:
                            print(' MC:' + str(i) + ' Status: saved')
                            csv_writer.writerow([str(i), 'saved'])
                        elif save_status == -1:
                            print(' MC:' + str(i) + ' Status: could not scrap')
                            csv_writer.writerow([str(i), 'could not scrap'])
                        elif save_status == -2:
                            print(' MC:' + str(i) + ' Status: not callable')
                            csv_writer.writerow([str(i), 'not callable'])
                    # if mc has no record save it for future references
                    else:
                        print(' MC:' + str(i) + ' Status: no record')
                        csv_writer.writerow([str(i), 'no record'])
                break
        csv_file.close()
        if break_outer:
            notify()
            break


def print_agents_list():
    with open('./files/sales_agents.txt') as agents_file:
        print("\n")
        for i, line in enumerate(agents_file.readlines()):
            name = line.split(',')[0]
            email = line.split(',')[1]
            print(f' {i+1:02d} Name:  {name}\n    Email: {email}')
        else:
            print("There are no agents in the database")
            input("\nPress any key to go back.")



def main_menu():
    while True:
        print("\n 1: Start Scraping.")
        print(" 2: Email Employees.")
        print(" 3: Add new employee.")
        print(" 4: Delete employee.")
        print(" 5: Get logs.")
        print(" 6: Print Agent's list.")
        print(" 7: Email Carriers")
        print(" 0: Exit")
        try:
            choice = int(input("\n Enter an option: "))
        except:
            print("\n Not a valid option.")
            continue
        if choice == 1:
            start_mc_menu()
        elif choice == 2:
            send_employee_daily_work()
        elif choice == 3:
            add_employee()
        elif choice == 4:
            name = input('\n Enter Name: ')
            if delete_agent(name):
                print(f' {name} is removed from the database.')
            else:
                print(f' Could not find an agent with name: {name}')
        elif choice == 5:
            get_logs()
        elif choice == 6:
            print_agents_list()
        elif choice == 7:
            print("\n Feature coming soon.")
        elif choice == 0:
            break
        else:
            print("\n Not a valid option.")
            continue


def get_no_of_carriers():
    with open('./files/carriers.csv', 'r') as carriers_file:
        line_count = 0
        for line in carriers_file.readlines():
            if line_count == 0:
                line_count += 1
                continue
            line_count += 1
    return line_count


def get_sent_leads():
    with open('./files/sales_work_logs.txt', 'r') as carriers_file:
        line_count = 0
        for line in carriers_file.readlines():
            line_count += 1
    return line_count


def get_logs():
    print(" -"*30)
    carriers = get_no_of_carriers()
    sent_leads = get_sent_leads()
    print(f" Database currently has: {carriers} Carriers")
    print(f" Number of leads sent to agents: {sent_leads}")
    print(f" Remaining Carriers: {carriers-sent_leads}")
    print(" -"*30)


if __name__ == '__main__':
    get_logs()
    main_menu()
