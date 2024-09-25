from selenium import webdriver
from create_files_for_scraper import create_files_for_scraper
from scrape import *
import pandas as pd


LIMIT = 0


# is called in start_searching method
def search(mc):
    driver.get("https://safer.fmcsa.dot.gov/CompanySnapshot.aspx")
    driver.find_element(By.XPATH, '//input[@id=2]').click()
    driver.find_element(By.XPATH, '//input[@id=4]').send_keys(mc)
    driver.find_element(By.XPATH, '//input[@value="Search"]').click()
    return driver


# is called in start_searching method
def notify():
    print("\nThere maybe something wrong with your internet or proxy. Please check and retry after few minutes.")
    delete_last_3mc()
    input("Press enter to quit...")


def delete_last_3mc():
    with open('./files/start_mc.csv') as agents_file:
        with open('./files/temp.txt', 'w') as temp_file:
            for line in agents_file.readlines()[:-3]:
                    temp_file.write(line)

    with open('./files/temp.txt') as temp_file:
        with open('./files/start_mc.csv', 'w') as agents_file:
            for line in temp_file.readlines():
                agents_file.write(line)


# is called in promt_for_start_mc method
def get_last_mc():
    file_r = open('./files/start_mc.csv', 'r')
    data = pd.read_csv(file_r)
    searched_mc = data['MC'].to_numpy()
    last_mc = int(searched_mc[-1])  # where to start searching
    start_mc = int(searched_mc[0])
    file_r.close()
    return [last_mc, start_mc]


# is called in main
def start_mc_menu():
    try:
        [last_mc, start_mc] = get_last_mc()
        print(f' Continuing where you left off. (At: {last_mc})')
        start = last_mc + 1
        if start >= start_mc+LIMIT:
            print(f" This Worker has cleared it's directive: scrape upto {start_mc + LIMIT - 1}")
            input("Press enter to quit...")
            return

    except:
        while True:
            start = int(input("\n Enter a Start MC: "))
            start_mc = start
            if isinstance(start, int):
                break
            else:
                print("Invalid MC")
    try:
        global driver
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        options = webdriver.ChromeOptions()
        options.headless = False
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument("--disable-extensions")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(" ", e)
    else:
        print(" Current Directive of this worker is to scrape upto:", start_mc + LIMIT - 1)
        start_searching(start, start_mc)


# search mc's
def start_searching(start, first_start):
    retry = 0
    counter_504 = 0
    break_outer = False
    for i in range(start, LIMIT + first_start):
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
                    record = driver.find_element(By.XPATH, '//i').text
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
                            print(' MC:' + str(i) + ' Status: could not scrape')
                            csv_writer.writerow([str(i), 'could not scrape'])
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


def get_no_of_carriers():
    with open('./files/carriers.csv', 'r') as carriers_file:
        lines = carriers_file.readlines()[1:]
    return len(lines)


def get_logs():
    print(" -"*30)
    carriers = get_no_of_carriers()
    print(f" Carriers scraped by this worker: {carriers} Carriers")
    print(" -"*30)


if __name__ == '__main__':
    create_files_for_scraper()

    with open('./files/limit.txt', 'r') as limit_file:
        LIMIT = int(limit_file.readline())

    get_logs()
    start_mc_menu()
    print("\n\nAt the end of the road buddy.")

