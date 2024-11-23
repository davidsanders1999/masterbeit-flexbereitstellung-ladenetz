import pandas as pd

# Infos über den betrachteten Zeitraum
start_date = '2023-01-01'
end_date = '2023-01-02'
freq = 5 # 10 oder 15 oder 30 oder 60

typen_ladesaeulen = ['NCS', 'MCS']

# Infos über die Ladesäulen
anzahl_ladesaeulen = {
    typen_ladesaeulen[0]: 35, # LKW Charging
    typen_ladesaeulen[1]: 14
}
max_leistung_ladesaeulen = {
    typen_ladesaeulen[0]: 100, # LKW Charging
    typen_ladesaeulen[1]: 900
}

# Infos über die eingehenden LKWs
szenarios_eingang_optionen = ['zufall', 'verteilungsfunktion']
szenario_eingang_lkws = szenarios_eingang_optionen[1] # 'zufall' oder 'verteilungsfunktion'

anzahl_lkws_mcs = 76 # Anzahl eingehende MCS LKWs pro Tag
anzahl_lkws_ncs = 50 # Anzahl eingehende NCS LKWs pro Tag

ladezeit_mcs = 45 # Ladezeit in min
ladezeit_ncs = 600 # Ladezeit in min

# Infos über die standard LKWs
nummer_lkws = [1, 2, 3, 4]

kapazitaet_lkws = {
    nummer_lkws[0]: 600,
    nummer_lkws[1]: 720,
    nummer_lkws[2]: 840,
    nummer_lkws[3]: 960
}

# Ladeverhalten
wartezeit = 15 # Wartezeit in min

if __name__ == '__main__':
    print(list(kapazitaet_lkws.keys()))
    print(nummer_lkws)

    print(typen_ladesaeulen)
    print(list(anzahl_ladesaeulen.keys()))
