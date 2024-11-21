import pandas as pd
import numpy as np
import os
from datetime import datetime

import config

def lkws_eingehend(anzahl_lkws, start_date, end_date):
    """
    Generiert eine Liste von LKWs, die zu bestimmten Zeitpunkten ankommen und eine bestimmte Kapazität haben.
    
    Args:
    anzahl_lkws (int): Die Anzahl der LKWs, die generiert werden sollen.
    
    Returns:
    list: Ein DataFrame mit LKWs mit zufälligen Ankunftszeiten und zufälligen Kapazitäten.
    """
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    time_range = pd.date_range(start=start_date, end=end_date, freq=f"{config.freq}T")
    lkws = []
    for index in range(anzahl_lkws):
        lkw = {
            'id': index,
            'Zeitspanne': np.random.choice(time_range),
            'Kapazität': np.random.randint(50, 301),
            'Ladezustand': np.random.uniform(0, 1),
            'typ_ladesaeule': np.random.choice(list(config.anzahl_ladesaeulen.keys()))
        }
        lkws.append(lkw)
    df_lkws = pd.DataFrame(lkws)
    return df_lkws

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

'''
# Erstellen Sie ein DataFrame mit den Spalten 'Zeitspanne' und 'Kapazität'
df_lkws_ankommen = pd.DataFrame(columns=['Zeitspanne', 'Kapazität','Ladezustand'])
dict_lkws = {
    'id': [1,2,3,4],
    'Zeitspanne': ['2023-01-01 00:00:00','2023-01-01 00:00:00', '2023-01-01 00:00:00', '2023-01-01 19:00:00'],
    'Kapazität': [50,50, 300, 50],
    'Ladezustand': [0,0.5, 0.1, 0.1],
    'typ_ladesaeule': ['LPC','LPC', 'LPC', 'NCS']
}

dict_lkws['Zeitspanne'] = [datetime.strptime(zeit, '%Y-%m-%d %H:%M:%S') for zeit in dict_lkws['Zeitspanne']] # Konvertieren Sie die Zeitwerte in datetime-Objekte
'''
df_lkws_ankommen = lkws_eingehend(100, config.start_date, config.end_date)
df_lkws_warten = pd.DataFrame()

# Iterieren Sie über die ankommenden LKWs des DataFrames df_lkws
for index_lkw, row_lkw in df_lkws_ankommen.iterrows(): 
    startzeit = row_lkw['Zeitspanne']
    lkw_id = row_lkw['id']
    lkw_ladezustand = row_lkw['Ladezustand']
    lkw_kapazität = row_lkw['Kapazität']
    lkw_ladetyp = row_lkw['typ_ladesaeule']

    # Suchen der passenden Ladesäule
    freie_ladesaeule = df_lastgang.loc[(df_lastgang['leistung'] == 0) & (df_lastgang['Zeitspanne'] == startzeit) & (df_lastgang['Ladesäule'].str.contains(lkw_ladetyp))]
    
    # Prüfen, ob die Ladesäule frei ist, falls nicht LKW in Warteschlange einreihen
    if freie_ladesaeule.empty:
        df_lkws_warten = pd.concat([df_lkws_warten, row_lkw.to_frame().T], ignore_index=True)
        continue
    
    # Laden bis auf 100 %
    else:
        ladesaeule = freie_ladesaeule['Ladesäule'].values[0]
        ladesauele_max_leistung = int(freie_ladesaeule['max_leistung'].values[0])
        ladesauele_max_energie = int(freie_ladesaeule['max_energie'].values[0])

        # Wenn freie Ladesäule gefunden wurde, dann lade den LKW
        while lkw_ladezustand < 1:
            if lkw_kapazität*(1-lkw_ladezustand) <= ladesauele_max_energie:
                red_ladeleistung = lkw_kapazität*(1-lkw_ladezustand) * 60 / config.freq
                red_ladeenergie = lkw_kapazität*(1-lkw_ladezustand)
                df_lastgang.loc[(df_lastgang['Zeitspanne'] == startzeit) & (df_lastgang['Ladesäule'] == ladesaeule), 'energie'] = red_ladeenergie
                df_lastgang.loc[(df_lastgang['Zeitspanne'] == startzeit) & (df_lastgang['Ladesäule'] == ladesaeule), 'leistung'] = red_ladeleistung
                lkw_ladezustand = lkw_ladezustand + red_ladeenergie / lkw_kapazität

            else:
                df_lastgang.loc[(df_lastgang['Zeitspanne'] == startzeit) & (df_lastgang['Ladesäule'] == ladesaeule), 'energie'] = ladesauele_max_energie
                df_lastgang.loc[(df_lastgang['Zeitspanne'] == startzeit) & (df_lastgang['Ladesäule'] == ladesaeule), 'leistung'] = ladesauele_max_leistung
                lkw_ladezustand = lkw_ladezustand + ladesauele_max_energie / lkw_kapazität
                startzeit = startzeit + pd.Timedelta(minutes=config.freq)
    # Abschließenden Ladezustand in das DataFrame eintragen
    df_lkws_ankommen.loc[index_lkw, 'Ladezustand'] = lkw_ladezustand
        

df_lastgang.to_csv('./Output/Lastprofil.csv')
df_lkws_ankommen.to_csv('./Output/LKWs_eingehend.csv')
df_lkws_warten.to_csv('./Output/LKWs_warten.csv')