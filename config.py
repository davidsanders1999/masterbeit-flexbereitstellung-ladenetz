import pandas as pd

start_date = '2023-01-01'
end_date = '2023-01-02'
freq = 5

anzahl_ladesaeulen = {
    'LPC': 2, # PKW Charging
    'HPC': 3,
    'NCS': 4, # LKW Charging
    'MWC': 6
}

max_leistung_ladesaeulen = {
    'LPC': 50, # PKW Charging
    'HPC': 150,
    'NCS': 350, # LKW Charging
    'MWC': 500
}

df_lkws_standard = pd.DataFrame()
df_lkws_standard['id'] = range(4)
df_lkws_standard['kapazitaet'] = [600, 720, 840, 960]

print(df_lkws_standard)
