# %% Import the csv files
import pandas as pd
import numpy as np
import os
import re

# %% Import the raw query results data
directory = 'data/'
dfs = {}

for entry in os.scandir(directory):
    if entry.path.endswith(".csv") and entry.is_file():
        # print(entry.path)
        match = re.search('[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{2,4}', entry.path)
        # print(match.group())
        if match:
            dfs[match.group()] = pd.read_csv(entry.path, header=0, usecols=[0, 4, 6, 8])
            dfs[match.group()].set_index('ethnicity', inplace=True)

# %% 02-15-21 data seems to be cumulative, reindex all dfs and subtract from 02-15-21
for week in dfs:
    if week == '2.15.2021':
        continue
    else:
        dfs[week] = dfs[week].reindex_like(dfs['2.15.2021']).fillna(0).astype('int')

feb_8_cum = dfs['2.15.2021'].astype('str').replace(regex=r'.*', value=0)
for week in dfs:
    if week != '2.15.2021':
        continue
    else:
        feb_8_cum = feb_8_cum.add(dfs[week])

# %%
for week in dfs:
    dfs[week]['week of'] = week
    dfs[week].rename(columns={"ethnicity": "orig_ethnicity"}, inplace=True)
    dfs[week]['ethnicity'] = ["Hispanic" if x == 'Latino/a' else 'Non-Hispanic' for x in dfs[week]["orig_ethnicity"]]
    dfs[week]['race'] = dfs[week]['orig_ethnicity'].replace({'Middle Eastern': 'White',
                                                             'Filipino': 'Asian',
                                                             'Chinese': 'Asian',
                                                             'Japanese': 'Asian',
                                                             'Laotian': 'Asian',
                                                             'Korean': 'Asian',
                                                             'Cambodian': 'Asian',
                                                             'Vietnamese': 'Asian',
                                                             'Samoan': 'Native Hawaiian or Other Pacific Islander ('
                                                                       'NHOP)',
                                                             'Other': 'Unreported'
                                                             })
# %%
for week in dfs:
    clean_week = pd.pivot_table(dfs[week], values=['valid_tests', 'positive_tests', 'inconclusive_tests'],
                                columns=['ethnicity', 'race'], aggfunc=np.sum, fill_value=0)
    clean_week.to_csv('data/clean/'+week+'_clean.csv')
