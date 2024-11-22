import pandas as pd
import numpy as np
import os
from datetime import datetime

import config
import modell.eingang_lkws as eingang_lkws
import modell.lastgang_simulieren_lkws as lastgang_simulieren_lkws


if __name__ == '__main__':
    
    simulation_zeit_start = datetime.now()

    # Simulieren der eingehenden LKWs
    if config.szenario_eingang_lkws == 'zufall':
        df_lkws_eingang = eingang_lkws.lkws_eingang_zufall(config.anzahl_lkws)
    if config.szenario_eingang_lkws == 'verteilungsfunktion':
        df_lkws_eingang = eingang_lkws.lkws_eingang_verteilungsfunktion(config.anzahl_lkws)
    
    # df_lkws_eingang = lkws_eingehend_test()
    simulaiton_zeit_lkws_generieren = datetime.now()

    # Erstellen des leeren Lastgangs
    df_lastgang = lastgang_simulieren_lkws.lastgang_leer_erstellen()
    simulation_zeit_lastgang_erstellen = datetime.now()

    # Simulieren des Lastgangs
    df_lastgang, df_lkws_geladen, df_lkws_nicht_geladen = lastgang_simulieren_lkws.lastgang_simuieren(df_lkws_eingang, df_lastgang)

    # Speichern der Ergebnisse
    df_lastgang.to_csv('./Output/Lastprofil.csv')
    df_lkws_geladen.to_csv('./Output/LKWs_geladen.csv')
    df_lkws_nicht_geladen.to_csv('./Output/LKWs_nicht_geladen.csv')

    simulation_end = datetime.now()

    print(f"""##########
          
    Simulation erfolgreich beendet!
          
    Dauer LKWs erstellen:           {simulaiton_zeit_lkws_generieren - simulation_zeit_start}
    Dauer Lastgang erstellen:       {simulation_zeit_lastgang_erstellen - simulaiton_zeit_lkws_generieren}
    Dauer Lastgang simulieren:      {simulation_end - simulation_zeit_lastgang_erstellen}

    Gesamtzeit:                     {simulation_end - simulation_zeit_start}

    ##########""")