import csv
from datetime import datetime
import pandas as pd

verteilungsfunktion = pd.read_csv('./Input/verteilungsfunktion_mcs-ncs.csv', index_col=0, parse_dates=True)

for index, row in verteilungsfunktion.iterrows():
    verteilungsfunktion.at[index, 'Zeit'] = pd.to_datetime(row['Zeit'])

    for i in range(2):
        ausgangszeit = pd.to_datetime(row['Zeit'])
        zeit_addieren = pd.Timedelta(minutes=5)
        print(type(ausgangszeit))
        print(type(zeit_addieren))
        row['Zeit'] = ausgangszeit + zeit_addieren
        print(row['Zeit'])

        verteilungsfunktion = pd.concat([verteilungsfunktion, row.to_frame().T], ignore_index=True)

verteilungsfunktion.sort_values(by='Zeit', inplace=True)
verteilungsfunktion.reset_index(drop=True, inplace=True)

summe_NCS = verteilungsfunktion['NCS'].sum()
summe_MCS = verteilungsfunktion['MCS'].sum()

for index, row in verteilungsfunktion.iterrows():
    verteilungsfunktion.at[index, 'NCS'] = row['NCS'] / summe_NCS
    verteilungsfunktion.at[index, 'MCS'] = row['MCS'] / summe_MCS 


summe_NCS = verteilungsfunktion['NCS'].sum()
summe_MCS = verteilungsfunktion['MCS'].sum()

print(summe_NCS)
print(summe_MCS)

print(verteilungsfunktion)

verteilungsfunktion.to_csv('./Input/verteilungsfunktion_mcs-ncs_5-min.csv')