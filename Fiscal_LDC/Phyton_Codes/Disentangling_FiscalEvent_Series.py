#%%
import pandas as pd
import numpy as np

#%%
# Define the file name and column names
FILE_NAME = 'Disentangling_FiscalEvent_Series.xlsx'
DATE_COLUMN = 'Date'
VALUE_COLUMN = 'pv_change_fiscal_events'

#%%
# Load the Excel file
df = pd.read_excel(FILE_NAME)
print(df.head())
# %%
