import pandas as pd
import numpy as np
import os
from datetime import datetime

import config

def lkws_eingehend(anzahl):
    """
    Generiert eine Liste von LKWs, die zu bestimmten Zeitpunkten ankommen und eine bestimmte Kapazität haben.
    
    Args:
    anzahl (int): Die Anzahl der LKWs, die generiert werden sollen.
    
    Returns:
    list: Ein DataFrame mit LKWs mit zufälligen Ankunftszeiten und zufälligen Kapazitäten.
    """
    start_date = pd.to_datetime(config.start_date)
    end_date = pd.to_datetime(config.end_date)
    time_range = pd.date_range(start=start_date, end=end_date, freq=f"{config.freq}min")
    lkws = []
    for index in range(anzahl):
        standard_lkw = np.random.choice(config.df_standard_lkw)
        lkw = {
            'id': np.random.randint(0, anzahl),
            'zeit': np.random.choice(time_range),
            'kapazitaet': standard_lkw['kapazitaet'],
            'ladezustand': np.random.uniform(0, 1),
            'ladetyp': np.random.choice(list(config.anzahl_ladesaeulen.keys()))
        }
        lkws.append(lkw)
    df_lkws = pd.DataFrame(lkws)
    print(df_lkws)
    return df_lkws

def lastgang_ladehub_leer_erstellen():
    '''
    
    Dokumentation
    
    '''
    start_date = pd.to_datetime(config.start_date)
    end_date = pd.to_datetime(config.end_date)
    time_range = pd.date_range(start=start_date, end=end_date, freq=f"{config.freq}min")
    lastgang = []
    for date in time_range:
        for ladetyp, ladesaeule_anzahl in config.anzahl_ladesaeulen.items():
            for i in range(ladesaeule_anzahl):
                max_leistung = config.max_leistung_ladesaeulen[ladetyp]
                max_energie = max_leistung * config.freq / 60
                leistung = 0
                energie = 0
                lastgang.append({'zeit': date, 'ladetyp': f'{ladetyp}_{i}', 'max_energie':max_energie, 'max_leistung':max_leistung, 'energie': energie, 'leistung': leistung})

    df_lastgang = pd.DataFrame(lastgang)
    return df_lastgang

def lastgang_ladehub_simulieren(df_lkws_ankommen, df_lastgang):
    
    df_lkws_warten = pd.DataFrame()

    for index_lkw, row_lkw in df_lkws_ankommen.iterrows(): 
        startzeit = row_lkw['zeit']
        lkw_id = row_lkw['id']
        lkw_ladezustand = row_lkw['ladezustand']
        lkw_kapazitaet = row_lkw['kapazitaet']
        lkw_ladetyp = row_lkw['ladetyp']

        # Suchen der passenden Ladesäule
        freie_ladesaeule = df_lastgang.loc[(df_lastgang['leistung'] == 0) & (df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'].str.contains(lkw_ladetyp))]
        
        # Prüfen, ob die ladetyp frei ist, falls nicht LKW in Warteschlange einreihen
        if freie_ladesaeule.empty:
            df_lkws_warten = pd.concat([df_lkws_warten, row_lkw.to_frame().T], ignore_index=True)
            continue
        
        # Laden bis auf 100 %
        else:
            ladesaeule = freie_ladesaeule['ladetyp'].values[0]
            ladesauele_max_leistung = int(freie_ladesaeule['max_leistung'].values[0])
            ladesauele_max_energie = int(freie_ladesaeule['max_energie'].values[0])

            # Wenn freie ladetyp gefunden wurde, dann lade den LKW
            while lkw_ladezustand < 0.8:
                if lkw_kapazitaet*(1-lkw_ladezustand) <= ladesauele_max_energie:
                    red_ladeleistung = lkw_kapazitaet*(1-lkw_ladezustand) * 60 / config.freq
                    red_ladeenergie = lkw_kapazitaet*(1-lkw_ladezustand)
                    df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'energie'] = red_ladeenergie
                    df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'leistung'] = red_ladeleistung
                    lkw_ladezustand = lkw_ladezustand + red_ladeenergie / lkw_kapazitaet

                else:
                    df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'energie'] = ladesauele_max_energie
                    df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'leistung'] = ladesauele_max_leistung
                    lkw_ladezustand = lkw_ladezustand + ladesauele_max_energie / lkw_kapazitaet
                    startzeit = startzeit + pd.Timedelta(minutes=config.freq)
        # Abschließenden Ladezustand in das DataFrame eintragen
        df_lkws_ankommen.loc[index_lkw, 'ladezustand'] = lkw_ladezustand

    return df_lastgang, df_lkws_ankommen, df_lkws_warten


  
df_lkws_ankommen = lkws_eingehend(5)
df_lastgang = lastgang_ladehub_leer_erstellen()
df_lastgang, df_lkws_ankommen, df_lkws_warten = lastgang_ladehub_simulieren(df_lkws_ankommen, df_lastgang)

df_lastgang.to_csv('./Output/Lastprofil.csv')
df_lkws_ankommen.to_csv('./Output/LKWs_eingehend.csv')
df_lkws_warten.to_csv('./Output/LKWs_warten.csv')