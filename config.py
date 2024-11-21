import pandas as pd

start_date = '2023-01-01'
end_date = '2023-01-02'
freq = 5

anzahl_ladesaeulen = {
    'LPC': 1, # PKW Charging
    'HPC': 1,
    'NCS': 1, # LKW Charging
    'MWC': 1
}

max_leistung_ladesaeulen = {
    'LPC': 50, # PKW Charging
    'HPC': 150,
    'NCS': 350, # LKW Charging
    'MWC': 500
}

'''
df_ladesaeulen = pd.DataFrame()
df_ladesaeulen['ladetyp'] = ['LPC', 'HPC', 'NCS', 'MWC']
df_ladesaeulen['anzahl'] = [2, 3, 4, 6]
df_ladesaeulen['max_leistung'] = [50, 150, 350, 500]
'''

anzahl_lkws = 10

df_lkws_standard = pd.DataFrame()
df_lkws_standard['id'] = range(4)
df_lkws_standard['kapazitaet'] = [600, 720, 840, 960]

if __name__ == '__main__':
    print(None)
