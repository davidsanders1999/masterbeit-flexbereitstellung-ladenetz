import pandas as pd
import numpy as np
import os
from datetime import datetime

import config

# Erstellen Sie ein DataFrame mit den Spalten 'Zeitspanne', 'Ladesäule', 'energie' und 'leistung'
start_date = pd.to_datetime(config.start_date)
end_date = pd.to_datetime(config.end_date)

date_range = pd.date_range(start=start_date, end=end_date, freq=f"{config.freq}T")
dict_lastgang = []
for date in date_range:
    for typ_ladesaule, anzahl_ladesaeule in config.anzahl_ladesaeulen.items():
        for i in range(anzahl_ladesaeule):
            max_leistung = config.max_leistung_ladesaeulen[typ_ladesaule]
            max_energie = max_leistung * config.freq / 60
            leistung = 0
            energie = 0
            dict_lastgang.append({'Zeitspanne': date, 'Ladesäule': f'{typ_ladesaule}_{i}', 'max_energie':max_energie, 'max_leistung':max_leistung, 'energie': energie, 'leistung': leistung})

df_lastgang = pd.DataFrame(dict_lastgang)

# Erstellen Sie ein DataFrame mit den Spalten 'Zeitspanne' und 'Kapazität'
df_lkws_ankommen = pd.DataFrame(columns=['Zeitspanne', 'Kapazität','Ladezustand'])
dict_lkws = {
    'Zeitspanne': ['2023-01-01 11:00:00','2023-01-01 11:00:00', '2023-01-01 16:00:00', '2023-01-01 19:00:00'],
    'Kapazität': [1000,1000, 300, 50],
    'Ladezustand': [0.1,0.1, 0.1, 0.1],
    'typ_ladesaeule': ['MWC','MWC', 'NCS', 'NCS']
}

dict_lkws['Zeitspanne'] = [datetime.strptime(zeit, '%Y-%m-%d %H:%M:%S') for zeit in dict_lkws['Zeitspanne']] # Konvertieren Sie die Zeitwerte in datetime-Objekte
df_lkws_ankommen = pd.DataFrame(dict_lkws)

for index_lkw, row_lkw in df_lkws_ankommen.iterrows(): # Iterieren Sie über die ankommenden LKWs des DataFrames df_lkws
    startzeit = row_lkw['Zeitspanne']
    lkw_ladezustand = row_lkw['Ladezustand']
    lkw_kapazität = row_lkw['Kapazität']
    lkw_ladetyp = row_lkw['typ_ladesaeule']

    for index_lastgang, row_lastgang in df_lastgang.iterrows(): # Finden einer freien Ladesäule
        if row_lastgang['Ladesäule'].split('_')[0] == lkw_ladetyp and row_lastgang['leistung'] == 0 and row_lastgang['Zeitspanne'] == startzeit:
            # Hier können Sie den gefundenen Eintrag weiter verarbeiten
            ladesaeule = row_lastgang['Ladesäule']
            ladesauele_max_energie = row_lastgang['max_energie']
            ladesauele_max_leistung = row_lastgang['max_leistung']
            break
    
    while lkw_ladezustand < 0.8:
        if lkw_kapazität < ladesauele_max_energie:
            df_lastgang.loc[(df_lastgang['Zeitspanne'] == startzeit) & (df_lastgang['Ladesäule'] == ladesaeule), 'energie'] = lkw_kapazität
            df_lastgang.loc[(df_lastgang['Zeitspanne'] == startzeit) & (df_lastgang['Ladesäule'] == ladesaeule), 'leistung'] = lkw_kapazität * 60 / config.freq
            lkw_ladezustand = 1
        else:
            df_lastgang.loc[(df_lastgang['Zeitspanne'] == startzeit) & (df_lastgang['Ladesäule'] == ladesaeule), 'energie'] = ladesauele_max_energie
            df_lastgang.loc[(df_lastgang['Zeitspanne'] == startzeit) & (df_lastgang['Ladesäule'] == ladesaeule), 'leistung'] = ladesauele_max_leistung
            lkw_ladezustand = lkw_ladezustand + ladesauele_max_energie / lkw_kapazität
            startzeit = startzeit + pd.Timedelta(minutes=config.freq)
        


print(df_lastgang.loc[df_lastgang['energie'].notnull()])

# Speichern Sie das DataFrame in eine CSV-Datei
if not os.path.exists('./Output'):
    os.makedirs('./Output')

df_lastgang.to_csv('./Output/Lastprofil.csv')
df_lkws_ankommen.to_csv('./Output/LKWs.csv')