import pandas as pd

import config

def lastgang_leer_erstellen():

    start_date = pd.to_datetime(config.start_date)
    end_date = pd.to_datetime(config.end_date) + pd.Timedelta(days=1) # Stelle sicher, dass der letzte Tag auch berücksichtigt wird

    time_range = pd.date_range(start=start_date, end=end_date, freq=f"{config.freq}min")
    time_range = time_range[:-1] # Der letzte Zeitschritt wird entfernt, da dieser nicht mehr zum betrachteten Zeitraum gehört bsp. 2023-01-02 00:00:00

    lastgang = []
    
    for date in time_range:
        for ladetyp, ladesaeule_anzahl in config.anzahl_ladesaeulen.items():
            for i in range(ladesaeule_anzahl):
                max_leistung = config.max_leistung_ladesaeulen[ladetyp]
                max_energie = max_leistung * config.freq / 60
                leistung = 0
                energie = 0
                lkw_id = None
                ladedauer = None
                ladezustand = None
                lastgang.append({'zeit': date, 'ladetyp': f'{ladetyp}_{i}', 'max_energie':max_energie, 'max_leistung':max_leistung, 'energie': energie, 'leistung': leistung, 'lkw_id': lkw_id, 'ladedauer': ladedauer, 'ladezustand': ladezustand})    

    df_lastgang = pd.DataFrame(lastgang)
    return df_lastgang

def lastgang_simuieren(df_lkws_eingang, df_lastgang):

    df_lkws_geladen = pd.DataFrame(columns=['index', 'zeit', 'kapazitaet', 'ladezustand', 'ladetyp', 'zeit_ende', 'ladedauer','verzoegerung'])
    df_lkws_nicht_geladen = pd.DataFrame(columns=['index', 'zeit', 'kapazitaet', 'ladezustand', 'ladetyp'])

    for index, row_lkw in df_lkws_eingang.iterrows():
        startzeit = row_lkw['zeit']
        lkw_index = index
        lkw_ladezustand = row_lkw['ladezustand']
        lkw_kapazitaet = row_lkw['kapazitaet']
        lkw_ladetyp = row_lkw['ladetyp']
        verzoegerung = 0

        # Festlegen der Ladezeit
        if lkw_ladetyp == 'NCS':
            lkw_ladedauer = config.ladezeit_ncs
        elif lkw_ladetyp == 'MCS':
            lkw_ladedauer = config.ladezeit_mcs
        else:
            raise ValueError('Ladetyp nicht bekannt')

        # Suchen der passenden Ladesäule
        freie_ladesaeule = df_lastgang.loc[(df_lastgang['leistung'] == 0) & (df_lastgang['zeit'] == startzeit + pd.Timedelta(minutes=config.freq)) & (df_lastgang['ladetyp'].str.contains(lkw_ladetyp))]
        
        # Falls die Ladesäule nicht frei ist, dann suche nach einer freien Ladesäule
        if freie_ladesaeule.empty:
            # startzeit = pd.to_datetime(startzeit) + pd.Timedelta(minutes=config.freq)
            # Prüfen, ob innerhalb von 30 min eine Ladesäule frei wird
            for i in range(0, config.wartezeit, config.freq):
                time_delta = i + config.freq
                neue_startzeit = pd.to_datetime(startzeit) + pd.Timedelta(minutes=time_delta)
                freie_ladesaeule = df_lastgang.loc[(df_lastgang['leistung'] == 0) & (df_lastgang['zeit'] == neue_startzeit + pd.Timedelta(minutes=config.freq)) & (df_lastgang['ladetyp'].str.contains(lkw_ladetyp))]
                
                if not freie_ladesaeule.empty:
                    startzeit = neue_startzeit
                    verzoegerung = i + config.freq
                    break
        
        # Wenn keine freie Ladesäule innerhalb von 15 min gefunden wurde, dann speichere den LKW in einem separaten DataFrame
        if freie_ladesaeule.empty:            
            row_lkw['index'] = lkw_index
            df_lkws_nicht_geladen = pd.concat([df_lkws_nicht_geladen, row_lkw.to_frame().T], ignore_index=True)
            continue

        ladesaeule = freie_ladesaeule['ladetyp'].values[0]
        ladesauele_max_leistung = float(freie_ladesaeule['max_leistung'].values[0])
        ladesauele_max_energie = float(freie_ladesaeule['max_energie'].values[0])
        
        # Laden des LKWs entsprechend der Ladezeit
        ladedauer = 0
        while ladedauer < lkw_ladedauer:
            if lkw_ladezustand == 1: # LKW ist bereits voll geladen aber Ladezeit ist noch nicht erreicht
                ladedauer = ladedauer + config.freq
                startzeit = pd.to_datetime(startzeit) + pd.Timedelta(minutes=config.freq)
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'lkw_id'] = lkw_index
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'ladezustand'] = lkw_ladezustand
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'ladedauer'] = ladedauer
                continue

            if lkw_kapazitaet*(1-lkw_ladezustand) <= ladesauele_max_energie: # LKW kann in der verbleibenden Zeit vollständig geladen werden
                red_ladeleistung = lkw_kapazitaet*(1-lkw_ladezustand) * 60 / config.freq
                red_ladeenergie = lkw_kapazitaet*(1-lkw_ladezustand)
                lkw_ladezustand = lkw_ladezustand + red_ladeenergie / lkw_kapazitaet
                ladedauer = ladedauer + config.freq
                startzeit = pd.to_datetime(startzeit) + pd.Timedelta(minutes=config.freq)
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'energie'] = red_ladeenergie
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'leistung'] = red_ladeleistung
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'lkw_id'] = lkw_index
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'ladezustand'] = lkw_ladezustand
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'ladedauer'] = ladedauer
                
            else: # LKW kann nicht in der verbleibenden Zeit vollständig geladen werden
                lkw_ladezustand = lkw_ladezustand + ladesauele_max_energie / lkw_kapazitaet
                ladedauer = ladedauer + config.freq
                startzeit = pd.to_datetime(startzeit) + pd.Timedelta(minutes=config.freq)                
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'energie'] = ladesauele_max_energie
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'leistung'] = ladesauele_max_leistung
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'lkw_id'] = lkw_index
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'ladezustand'] = lkw_ladezustand
                df_lastgang.loc[(df_lastgang['zeit'] == startzeit) & (df_lastgang['ladetyp'] == ladesaeule), 'ladedauer'] = ladedauer

                
        
        row_lkw['zeit_ende'] = startzeit
        row_lkw['index'] = lkw_index
        row_lkw['ladedauer'] = ladedauer
        row_lkw['verzoegerung'] = verzoegerung
        df_lkws_geladen = pd.concat([df_lkws_geladen, row_lkw.to_frame().T], ignore_index=True)


    return df_lastgang, df_lkws_geladen, df_lkws_nicht_geladen