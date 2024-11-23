import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

# Erstellen von zufälligen eingehenden LKWs innerhalb der definierten Betrachtungszeit
def lkws_eingang_zufall(anzahl_mcs, anzahl_ncs):
    date_range = pd.date_range(start=config.start_date, end=config.end_date, freq='D')
    time_range = pd.date_range(start='00:00:00', end='23:59:59', freq=f'{config.freq}T')
    
    # Timestamps in Liste mit Uhrzeiten als Strings umwandeln
    times = []
    for time in time_range:
        time = time.strftime('%H:%M:%S')
        times.append(time)

    # Zurällige Liste aus einfahrenden LKWs erstellen
    lkws = []
    for date in date_range:
        for i in range(anzahl_mcs + anzahl_ncs):
            nummer_lkw = np.random.choice(config.nummer_lkws)
            zeit_lkw = pd.to_datetime(f"{date.date()} {np.random.choice(times)}")

            lkw = {
                'nr': nummer_lkw,
                'zeit': zeit_lkw,
                'kapazitaet': config.kapazitaet_lkws[nummer_lkw],
                'ladezustand': np.random.uniform(0.05, 0.4),
                'ladetyp': np.random.choice(list(config.typen_ladesaeulen))
            }
            lkws.append(lkw)
    
    # Sortieren, Indexierung und Ausgeben der eingehenden LKWs
    df_lkws = pd.DataFrame(lkws)
    df_lkws = df_lkws.sort_values(by='zeit')
    df_lkws = df_lkws.reset_index(drop=True)
    df_lkws.index = df_lkws.index + 1
    df_lkws.to_csv('./Output/LKWs_eingehend.csv')
    return df_lkws

def lkws_eingang_verteilungsfunktion(anzahl_mcs, anzahl_ncs):
    verteilungsfunktion = pd.read_csv('./Input/verteilungsfunktion_mcs-ncs_5-min.csv', index_col=0, parse_dates=True)

    # Filtern der Verteilungsfunktion nach der gewünschten Frequenz
    if config.freq > 5:
        
        # Eliminieren von allen Zeiten, die nicht in den 5-minütigen Intervallen liegen
        df_time_neu = pd.DataFrame(columns=['Zeit'])
        zeit = pd.to_datetime('00:00:00')

        # Erstellen Liste mit den gewünschten Zeitelementen
        for i in range(int(1440/config.freq)):
            df_time_neu.loc[i,'Zeit'] = zeit
            zeit = zeit + pd.Timedelta(minutes=config.freq)
        zeiten = df_time_neu['Zeit'].to_list()

        # Filtern der Verteilungsfunktion nach der Liste mit den gewünschten Zeitelementen
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
            
    # Erstellen der LKWs entsprechend der neuen Verteilungsfunktion
    lkws = []
    date_range = pd.date_range(start=config.start_date, end=config.end_date, freq='D')

    # Betrachten von jedem Tag zwichen start_date und end_date
    for date in date_range: 
        for i in range(anzahl_ncs):
            nummer_lkw = np.random.choice(config.nummer_lkws)
            ladetyp = 'NCS'

            zeiten = verteilungsfunktion['Zeit']
            wahrscheinlichkeiten = verteilungsfunktion['NCS']
            zeit = np.random.choice(zeiten, p=wahrscheinlichkeiten)
            
            # Zusammensetzen von Datum und Zeit
            zeit = pd.to_datetime(f"{date.date()} {zeit}")

            # Anhängen von erstelltem LKW an die Liste
            lkws.append({
                'zeit': zeit,
                'kapazitaet': config.kapazitaet_lkws[nummer_lkw],
                'ladezustand': np.random.uniform(0.05, 0.4),
                'ladetyp': ladetyp
            })

        for i in range(anzahl_mcs): # Erstellen von anzahl LKWs pro Tag
            nummer_lkw = np.random.choice(config.nummer_lkws) # Zufällige Auswahl eines LKW-Typs
            ladetyp = 'MCS' # Zufällige Auswahl eines Ladetyps

            zeiten = verteilungsfunktion['Zeit']
            wahrscheinlichkeiten = verteilungsfunktion['MCS']
            zeit = np.random.choice(zeiten, p=wahrscheinlichkeiten)
            
            # Zusammensetzen von Datum und Zeit
            zeit = pd.to_datetime(f"{date.date()} {zeit}")

            # Anhängen von erstelltem LKW an die Liste
            lkws.append({
                'zeit': zeit,
                'kapazitaet': config.kapazitaet_lkws[nummer_lkw],
                'ladezustand': np.random.uniform(0.05, 0.4),
                'ladetyp': ladetyp
            })
    
    # Sortieren, Indexierung und Ausgeben der eingehenden LKWs
    df_lkws = pd.DataFrame(lkws) # Erstellen eines DataFrames aus der Liste 
    df_lkws = df_lkws.sort_values(by='zeit') # Sortieren der LKWs nach Ankunftszeit
    df_lkws = df_lkws.reset_index(drop=True) # Zurücksetzen des Index
    df_lkws.index = df_lkws.index + 1   # Indexierung von 1 bis n
    df_lkws.to_csv('./Output/LKWs_eingehend.csv') # Speichern der eingehenden LKWs in einer CSV-Datei
    return df_lkws

if __name__ == '__main__':

    df_lkws = lkws_eingang_verteilungsfunktion(150,30)
    print(df_lkws)