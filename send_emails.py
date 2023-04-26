import smtplib
from email.message import EmailMessage
import os
from datetime import date
import csv


def sent(mc):
    with open('./files/sales_work_logs.txt', 'r') as log_file:
        sent = [mc for line in log_file if f'"{mc}"' in line]
    if sent:
        return True
    else:
        return False


def get_n_carriers_from_file(employee_name, employee_email, no_of_carriers):
    file_name = f'{employee_name} {date.today().strftime("%d-%m-%Y")}.csv'
    with open('./files/carriers.csv', 'r') as infile, open(f'./files/{file_name}', 'a', newline='') as outfile:
        line_count = 0
        fieldnames = ['MC', 'Entity Type', 'Operating Status', 'Legal Name', 'DBA Name', 'Physical Address', 'Phone',
                      'Email',
                      'Mailing Address', 'USDOT Number', 'MC/MX/FF Number(s)', 'Power Units', 'MCS-150 Form Date',
                      'Drivers', 'Operation_class', 'Carrier_operations', 'Cargo_carried']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in csv.DictReader(infile):
            if line_count >= no_of_carriers:
                break

            if not sent(row['MC']):
                # log which mc is sent
                with open('./files/sales_work_logs.txt', 'a') as log_file:
                    log_file.write(f'"{row["MC"]}",{employee_email}\n')
                # make new file to be sent to the employee
                writer.writerow(row)
                line_count += 1
    return file_name


def send_employee_daily_work():
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        while True:
            email_add = input(" Email: ")
            password = input(" Password: ")
            try:
                smtp.login(email_add, password)
            except:
                print("Invalid email or password.")
                continue
            with open('./files/sales_agents.txt', 'r') as agents_file:
                for line in agents_file.readlines():
                    line_split = line.replace("\n", "").split(",")
                    msg = EmailMessage()
                    msg['Subject'] = 'Daily Carrier list'
                    msg['From'] = "ahmedkhalid9199@gmail.com"
                    msg['To'] = line_split[-1]
                    msg.set_content('')
                    no_of_leads = int(input(f'\nEnter Number of leads to send to {line_split[0]}: '))
                    if no_of_leads != 0:
                        file_name = get_n_carriers_from_file(line_split[0], msg['To'], no_of_leads)
                        with open(f'./files/{file_name}', 'rb') as file:
                            file_content = file.read()
                            file_path = file.name

                        msg.add_attachment(file_content, maintype='text', subtype='csv', filename=file_name)
                        smtp.send_message(msg)
                        print(f"Email sent to {line_split[0]}")
                    os.remove(file_path)
            break


def add_employee():
    name = input('Enter Name: ')
    email = input('Enter email: ')
    with open('./files/sales_agents.txt', 'a') as agents_file:
        agents_file.write(f'{name},{email}\n')


def delete_agent(name):
    agent_found = False
    with open('./files/sales_agents.txt') as agents_file:
        with open('./files/temp.txt', 'w') as temp_file:
            for line in agents_file.readlines():
                if name.lower() not in line.lower():
                    temp_file.write(line)
                else:
                    agent_found = True

    with open('./files/temp.txt') as temp_file:
        with open('./files/sales_agents.txt', 'w') as agents_file:
            for line in temp_file.readlines():
                agents_file.write(line)

    return agent_found


def delete_last_3mc():
    with open('./files/start_mc.csv') as agents_file:
        with open('./files/temp.txt', 'w') as temp_file:
            for line in agents_file.readlines()[:-3]:
                    temp_file.write(line)

    with open('./files/temp.txt') as temp_file:
        with open('./files/start_mc.csv', 'w') as agents_file:
            for line in temp_file.readlines():
                agents_file.write(line)


# send_employee_daily_work()
# name = input("Enter agent's full name: ")

# print(delete_agent(name))