import pandas as pd

import config

def lastgang_leer_erstellen():
    '''
    Erstellt einen leeren Lastgang für die Ladesäulen, die in der config.py definiert sind.

    Args:
    None

    Returns:
    DataFrame: Ein DataFrame mit leeren Werten für die Ladesäulen
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
                lkw_id = None
                lastgang.append({'zeit': date, 'ladetyp': f'{ladetyp}_{i}', 'max_energie':max_energie, 'max_leistung':max_leistung, 'energie': energie, 'leistung': leistung, 'lkw_id': lkw_id})
    
    # Alternative mit einem DataFrame. Leider signifikant langsamer
    '''
    for date in time_range:
        for index, row in config.df_ladesaeulen.iterrows():
            for i in range(row['anzahl']):
                max_leistung = row['max_leistung']
                max_energie = max_leistung * config.freq / 60
                leistung = 0
                energie = 0
                lastgang.append({'zeit': date, 'ladetyp': f'{row["ladetyp"]}_{i}', 'max_energie':max_energie, 'max_leistung':max_leistung, 'energie': energie, 'leistung': leistung})
    '''         

    df_lastgang = pd.DataFrame(lastgang)
    return df_lastgang

def lastgang_simuieren(df_lkws_eingang, df_lastgang):
    '''
    Simuliert den Lastgang für die Ladesäulen und die LKWs, die ankommen.

    Args:
    df_lkws_eingang (DataFrame): Ein DataFrame mit den LKWs, die ankommen.

    Returns:
    DataFrame: Ein DataFrame mit den Ladesäulen und den Ladevorgängen
    '''
    df_lkws_geladen = pd.DataFrame(columns=['id', 'zeit', 'kapazitaet', 'ladezustand', 'ladetyp', 'zeit_ende'])
    df_lkws_nicht_geladen = pd.DataFrame(columns=['id', 'zeit', 'kapazitaet', 'ladezustand', 'ladetyp'])

    for index_lkw, row_lkw in df_lkws_eingang.iterrows():
    
        startzeit = row_lkw['zeit']
        lkw_id = row_lkw['id']
        lkw_ladezustand = row_lkw['ladezustand']
        lkw_kapazitaet = row_lkw['kapazitaet']
        lkw_ladetyp = row_lkw['ladetyp']

        # Suchen der passenden Ladesäule
        freie_ladesaeule = df_lastgang.loc[(df_lastgang['leistung'] == 0) & (df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'].str.contains(lkw_ladetyp))]
        
        # Falls die Ladesäule nicht frei ist, dann suche nach einer freien Ladesäule
        if freie_ladesaeule.empty:
            # Prüfen, ob innerhalb von 15 min eine Ladesäule frei wird
            for i in range(0, 15, config.freq):
                startzeit = startzeit + pd.Timedelta(minutes=config.freq)
                freie_ladesaeule = df_lastgang.loc[(df_lastgang['leistung'] == 0) & (df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'].str.contains(lkw_ladetyp))]
        
        # Wenn keine freie Ladesäule innerhalb von 15 min gefunden wurde, dann speichere den LKW in einem separaten DataFrame
        if freie_ladesaeule.empty:            
            print(f'LKW {lkw_id} konnte nicht geladen werden.')
            df_lkws_nicht_geladen = pd.concat([df_lkws_nicht_geladen, row_lkw.to_frame().T], ignore_index=True)
            continue
            
        
        # Laden bis auf 100 %
        ladesaeule = freie_ladesaeule['ladetyp'].values[0]
        ladesauele_max_leistung = float(freie_ladesaeule['max_leistung'].values[0])
        ladesauele_max_energie = float(freie_ladesaeule['max_energie'].values[0])

        # Wenn freie ladetyp gefunden wurde, dann lade den LKW
        while lkw_ladezustand <= 0.8:
            if lkw_kapazitaet*(1-lkw_ladezustand) <= ladesauele_max_energie:
                red_ladeleistung = lkw_kapazitaet*(1-lkw_ladezustand) * 60 / config.freq
                red_ladeenergie = lkw_kapazitaet*(1-lkw_ladezustand)
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'energie'] = red_ladeenergie
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'leistung'] = red_ladeleistung
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'lkw_id'] = lkw_id
                lkw_ladezustand = lkw_ladezustand + red_ladeenergie / lkw_kapazitaet

            else:
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'energie'] = ladesauele_max_energie
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'leistung'] = ladesauele_max_leistung
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'lkw_id'] = lkw_id
                lkw_ladezustand = lkw_ladezustand + ladesauele_max_energie / lkw_kapazitaet
                startzeit = startzeit + pd.Timedelta(minutes=config.freq)
        
        row_lkw['zeit_ende'] = startzeit
        df_lkws_geladen = pd.concat([df_lkws_geladen, row_lkw.to_frame().T], ignore_index=True)


    return df_lastgang, df_lkws_geladen, df_lkws_nicht_geladen