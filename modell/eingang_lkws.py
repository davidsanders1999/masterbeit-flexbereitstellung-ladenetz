import pandas as pd
import numpy as np

import config

def lkws_eingehend_test():
    lkws = []
    for index in range(5):
        standard_lkw = config.df_lkws_standard.sample(n=1).iloc[0]
        lkw = {
            'id': index,
            'zeit': pd.Timestamp('2023-01-01 00:00:00'),
            'kapazitaet': 40,
            'ladezustand': 0,
            'ladetyp': 'NCS'
        }
        lkws.append(lkw)
    df_lkws = pd.DataFrame(lkws)
    return df_lkws

def lkws_eingang(anzahl):
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
    
    '''
    # Load the distribution function from CSV
    verteilungsfunktion = pd.read_csv('./Input/verteilungsfunktion_mcs-ncs.csv', index_col=0, parse_dates=True)
    print(verteilungsfunktion)

    # Normalize the distribution function to ensure it sums to 1
    verteilungsfunktion = verteilungsfunktion.div(verteilungsfunktion.sum(axis=1), axis=0)

    # Generate LKWs based on the distribution function
    lkws = []
    for index in range(anzahl):
        standard_lkw = config.df_lkws_standard.sample(n=1).iloc[0]
        
        # Randomly choose the time and type based on the distribution function
        time_choice = np.random.choice(verteilungsfunktion.index, p=verteilungsfunktion.sum(axis=1))
        ladetyp_choice = np.random.choice(verteilungsfunktion.columns, p=verteilungsfunktion.loc[time_choice])
        
        lkw = {
            'id': index,
            'zeit': time_choice,
            'kapazitaet': standard_lkw['kapazitaet'],
            'ladezustand': np.random.uniform(0.05, 0.4),
            'ladetyp': ladetyp_choice
        }
        lkws.append(lkw)

    '''
    lkws = []
    for index in range(anzahl):
        standard_lkw = config.df_lkws_standard.sample(n=1).iloc[0]
        lkw = {
            'id': index,
            'zeit': np.random.choice(time_range),
            'kapazitaet': standard_lkw['kapazitaet'],
            'ladezustand': np.random.uniform(0.05, 0.4),
            'ladetyp': np.random.choice(list(config.anzahl_ladesaeulen.keys()))
        }
        lkws.append(lkw)

    
    df_lkws = pd.DataFrame(lkws)
    df_lkws = df_lkws.sort_values(by='zeit')

    df_lkws.to_csv('./Output/LKWs_eingehend.csv')
    return df_lkws