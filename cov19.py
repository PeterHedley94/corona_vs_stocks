import pandas as pd
import os

def get_csvs():
    folder = os.path.join("COVID-19", "csse_covid_19_data",
                        "csse_covid_19_daily_reports")
    file_list = [os.path.join(folder,i) for i in os.listdir(folder) if i.endswith('.csv')]
    cov_per_day = [pd.read_csv(i) for i in file_list]
    return file_list, cov_per_day

def replace_data(col_name):
    if col_name=='Mainland China':
        return 'China'
    elif col_name== 'Korea, South':
        return 'South Korea'
    elif col_name == 'United Kingdom':
        return 'UK'
    return col_name

def get_population_data(cov_19):
    pop = pd.read_csv('pop_data.csv',sep='\t',header=None)
    pop = pop.iloc[:,[1,2]]
    pop.columns = ['Country','Population']
    cov_19['Country'] = cov_19.index
    combined = pd.merge(cov_19, pop, on='Country', how='left')
    combined.index= combined['Country']
    return combined.loc[:,combined.columns!='Country']

def get_cov_data():
    file_list, cov_per_day = get_csvs()
    for i in cov_per_day:
        i.loc[:,'Country/Region'] = i.loc[:,'Country/Region'].apply(replace_data)
    cumulative = [i.groupby('Country/Region').sum() for i in cov_per_day]

    df = pd.concat([i['Confirmed'] for i in cumulative], axis=1)
    df.columns = [os.path.basename(i).replace(".csv","") for i in file_list]
    df.columns =  pd.to_datetime(df.columns)
    df = get_population_data(df)
    return df