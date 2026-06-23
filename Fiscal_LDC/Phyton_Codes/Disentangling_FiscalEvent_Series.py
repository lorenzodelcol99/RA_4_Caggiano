#%%
import pandas as pd
import numpy as np
import os

# Stampa la directory corrente per farti vedere dove Python crede di trovarsi
print("Directory di lavoro attuale:", os.getcwd())


#%%
# Define the file name and column names
FILE_NAME = '../Disentangling_Fiscal_Event_Daily_Series.xlsx'
DATE_COLUMN = 'Date'
VALUE_COLUMN = 'pv_change_fiscal_events'

#%%
# Load the Excel file
df = pd.read_excel(FILE_NAME)
print(df.head())
# %%
