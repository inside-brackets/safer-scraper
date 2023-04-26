import csv

# with open('./files/carriers.csv', 'r') as infile, open('carriers.csv', 'a', newline='') as outfile:
#     # output dict needs a list for new column ordering
#     fieldnames = ['MC', 'Entity Type', 'Operating Status', 'Legal Name', 'DBA Name', 'Physical Address', 'Phone', 'Email',
#                   'Mailing Address', 'USDOT Number', 'MC/MX/FF Number(s)', 'Power Units', 'MCS-150 Form Date',
#                   'Drivers', 'Operation_class', 'Carrier_operations', 'Cargo_carried']
#     writer = csv.DictWriter(outfile, fieldnames=fieldnames)
#     # reorder the header first
#     writer.writeheader()
#     for row in csv.DictReader(infile):
#         # writes the reordered rows to the new file
#         writer.writerow(row)
