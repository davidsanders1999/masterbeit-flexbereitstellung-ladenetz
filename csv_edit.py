import csv
from datetime import datetime

input_file = './Input/verteilungsfunktion_mcs-ncs.csv'
output_file = './Input/verteilungsfunktion_mcs-ncs_conv.csv'
date_prefix = '2023-01-01'

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile, delimiter=';')
    writer = csv.writer(outfile, delimiter=',')
    
    for row in reader:
        # Add a comma at the beginning of each row
        row.insert(0, '')
        
        # Format the 'zeit' column with the date prefix
        if 'Zeit' in row:
            zeit_index = row.index('Zeit')
        else:
            row[zeit_index] = f'{date_prefix} {row[zeit_index]}'
        
        writer.writerow(row)