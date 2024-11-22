import pandas as pd

start_date = '2023-01-01'
end_date = '2023-01-02'
freq = 5

anzahl_ladesaeulen = {
    'NCS': 12, # LKW Charging
    'MCS': 5
}

max_leistung_ladesaeulen = {
    'NCS': 100, # LKW Charging
    'MCS': 900
}

'''
df_ladesaeulen = pd.DataFrame()
df_ladesaeulen['ladetyp'] = ['LPC', 'HPC', 'NCS', 'MWC']
df_ladesaeulen['anzahl'] = [2, 3, 4, 6]
df_ladesaeulen['max_leistung'] = [50, 150, 350, 500]
'''

anzahl_lkws = 20
anteil_mcs = 0.5


df_lkws_standard = pd.DataFrame()
df_lkws_standard['id'] = range(4)
df_lkws_standard['kapazitaet'] = [600, 720, 840, 960]

if __name__ == '__main__':
    print(None)
