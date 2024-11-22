import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

def lkws_eingang_zufall(anzahl):

    start_date = pd.to_datetime(config.start_date)
    end_date = pd.to_datetime(config.end_date)
    time_range = pd.date_range(start=start_date, end=end_date, freq=f"{config.freq}min")
    
    lkws = []
    for i in range(anzahl):
        nummer_lkw = np.random.choice(config.nummer_lkws)
        lkw = {
            'nr': nummer_lkw,
            'zeit': np.random.choice(time_range),
            'kapazitaet': config.kapazitaet_lkws[nummer_lkw],
            'ladezustand': np.random.uniform(0.05, 0.4),
            'ladetyp': np.random.choice(list(config.typen_ladesaeulen))
        }
        lkws.append(lkw)
    
    df_lkws = pd.DataFrame(lkws)
    df_lkws = df_lkws.sort_values(by='zeit')
    df_lkws = df_lkws.reset_index(drop=True)
    df_lkws.index = df_lkws.index + 1
    df_lkws.to_csv('./Output/LKWs_eingehend.csv')
    return df_lkws

def lkws_eingang_verteilungsfunktion(anzahl):
    verteilungsfunktion = pd.read_csv('./Input/verteilungsfunktion_mcs-ncs_5-min.csv', index_col=0, parse_dates=True)

    if config.freq > 5:
        
        # Eliminieren von allen Zeiten, die nicht in den 5-minütigen Intervallen liegen
        df_time_neu = pd.DataFrame(columns=['Zeit'])
        zeit = pd.to_datetime('2023-01-01 00:00:00')

        for i in range(int(1440/config.freq)):
            df_time_neu.loc[i,'Zeit'] = zeit
            zeit = zeit + pd.Timedelta(minutes=config.freq)
        zeiten = df_time_neu['Zeit'].to_list()

        for index, row in verteilungsfunktion.iterrows():            
            zeit = pd.to_datetime(row['Zeit'])
            if zeit not in zeiten:
                verteilungsfunktion.drop(index, inplace=True)

        # Normieren der Verteilungsfunktion
        summe_NCS = verteilungsfunktion['NCS'].sum()
        summe_MCS = verteilungsfunktion['MCS'].sum()

        for index, row in verteilungsfunktion.iterrows():
            verteilungsfunktion.at[index, 'NCS'] = row['NCS'] / summe_NCS
            verteilungsfunktion.at[index, 'MCS'] = row['MCS'] / summe_MCS

    lkws = []
    for i in range(anzahl):
        nummer_lkw = np.random.choice(config.nummer_lkws)
        ladetyp = np.random.choice(list(config.typen_ladesaeulen))

        if ladetyp == 'NCS':
            zeiten = verteilungsfunktion['Zeit']
            wahrscheinlichkeiten = verteilungsfunktion['NCS']
        elif ladetyp == 'MCS':
            zeiten = verteilungsfunktion['Zeit']
            wahrscheinlichkeiten = verteilungsfunktion['MCS']
            
        zeit = np.random.choice(zeiten, p=wahrscheinlichkeiten)

        lkws.append({
            'nr': nummer_lkw,
            'zeit': zeit,
            'kapazitaet': config.kapazitaet_lkws[nummer_lkw],
            'ladezustand': np.random.uniform(0.05, 0.4),
            'ladetyp': ladetyp
        })
    
    df_lkws = pd.DataFrame(lkws)
    df_lkws = df_lkws.sort_values(by='zeit')
    df_lkws = df_lkws.reset_index(drop=True)
    df_lkws.index = df_lkws.index + 1
    df_lkws.to_csv('./Output/LKWs_eingehend.csv')
    return pd.DataFrame(lkws)

if __name__ == '__main__':

    df_lkws = lkws_eingang_verteilungsfunktion(1000)
    print(df_lkws)