# %% 0; Packages
import os
import pandas as pd
import numpy as np
import openpyxl

# %% 
percorso_cartella = '/Users/lorenzodelcol/Desktop/GIT/RA_4_Caggiano/GFU/REPLICATION DROPBOX (NEW)/Raw data UPDATE/Updated 2026 Series'
os.chdir(percorso_cartella)

print("Adding the path")

# %% to check the pair correlations between the original and the newly updated dataset:
# Few variable seems to be not perfectly correlated, like US EX rate, buut just some few complitely ifferent observations drive the correlation down.
# Probably this change is driven by the revision of the series
from IPython.display import display

# 1. Load the original and the newly updated datasets
old_df = pd.read_excel('cc_globalfactor_1992M72020M5.xlsx', sheet_name='raw data')
new_df = pd.read_excel('cc_globalfactor_1992M72026M6.xlsx')

# 2. Date formatting and indexing
# Make sure to handle the string formats correctly
old_df['Date'] = pd.to_datetime(old_df['Date'])
# In Phase C, the new dataset dates were formatted as '%d/%m/%Y'
new_df['Date'] = pd.to_datetime(new_df['Date'], format='%d/%m/%Y')

old_df.set_index('Date', inplace=True)
new_df.set_index('Date', inplace=True)

# 3. Isolate the exact overlapping period
start_date = '1992-07-01'
end_date = '2020-05-01'

old_df_sub = old_df.loc[start_date:end_date]
new_df_sub = new_df.loc[start_date:end_date]

# 4. Identify variables that exist in both datasets
common_cols = [col for col in old_df_sub.columns if col in new_df_sub.columns]

# 5. Compute pairwise Pearson correlations
correlations = []

for col in common_cols:
    series_old = old_df_sub[col]
    series_new = new_df_sub[col]
    
    # Calculate correlation (pandas automatically drops NaNs pairwise)
    corr = series_old.corr(series_new)
    correlations.append({'Variable': col, 'Correlation': corr})

# 6. Format and display the results
corr_df = pd.DataFrame(correlations)

# Sort ascending so any problematic correlations (less than 1.0) appear at the top
corr_df = corr_df.sort_values(by='Correlation', ascending=True).reset_index(drop=True)

print("Correlation Table (Original vs. Updated Dataset | 1992M7 - 2020M5):")
# In standard Python/VS Code, print(corr_df.to_string()) is safer than display() if not using interactive windows, 
# but if you are running this in a VS Code interactive python window (# %%), display() works perfectly.
display(corr_df)
# %%
