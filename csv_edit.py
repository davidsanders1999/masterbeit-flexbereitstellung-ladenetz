import csv
from datetime import datetime
import pandas as pd

verteilungsfunktion = pd.read_csv('./Input/verteilungsfunktion_mcs-ncs_5-min.csv', index_col=0, parse_dates=True)

for index, row in verteilungsfunktion.iterrows():            
    zeit = row['Zeit']
    zeit = zeit.split(' ', 1)[1]
    verteilungsfunktion.loc[index, 'Zeit'] = zeit
    print(zeit)


verteilungsfunktion.to_csv('./Input/verteilungsfunktion_mcs-ncs_5-min_conv.csv')