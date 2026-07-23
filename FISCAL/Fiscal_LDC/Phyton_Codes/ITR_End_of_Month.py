# %% [1] SETUP & IMPORTS
import pandas as pd
import numpy as np
import os # Operationg System, used to map the path of the files (working directory)

# %% [2] Loading Raw Data

# Setting the Working Directory to the location of the raw data files
os.chdir('/Users/lorenzodelcol/Desktop/GIT/RA_4_Caggiano/FISCAL/Fiscal_Data/Initial_Cagg_Material')

OUTPUT_FILE = '../ITR_dataframe.xlsx'

# Loading raw data
MunisData2            = pd.read_excel('MunisData2.xlsx'    , sheet_name='SubData')   # Municipal Bond Yields for 1,2,3,5,10,15,20 and 30 year maturities. END OF MONTH data from December 1949 to October 2008
# need to extract the folder "SubData" and update it
Muni_Benchmark        = pd.read_excel('Muni_Benchmark.xlsx', sheet_name='Worksheet') # Municipal Bond Yields for 1,5, 10 and 20 year maturities. END OF MONTH data from July 2024 to January 2009 (NEED TO REVERSE THE ORDER)
# (MISSING NOVEMEBR AND DECEMBER 2008) the two datasets are combined to create a continuous time series of Municipal Bond Yields from December 1949 to July 2024 (with this two month gap in 2008)

# In MunisData2 we have data for gov bonds yields that are not available from the FRED site.
# After having done the end of month extration from the daily data, I want to check the correlation between the data gov bonds data from the fren and the one from Leeper

Gov_Bond_1_daily      = pd.read_excel('DGS1.xlsx', sheet_name='Daily')
Gov_Bond_5_daily      = pd.read_excel('DGS5.xlsx', sheet_name='Daily')
# need to extract the gov bonds end of months from the daily data and mearge it in the MunisData2"SubData"

# When we are going to have daily data for the Municipal Bond Yield from Bloomberg
# Muni_Bond_1_daily   = pd.read_excel('../Muni_Bond_1_daily.xlsx')
# Muni_Bond_5_daily   = pd.read_excel('../Muni_Bond_5_daily.xlsx')

print("loaded all the raw data files")
# %% [3] Data Cleaning and Preprocessing

ITR_df = MunisData2.iloc[:, [0, 1, 4]].copy() #copying the columns of interest (Date, Municipal 1YR and 5YR yields) from the MunisData2 dataset
# for Gov bonds I should copy the early period observations that I don't have in the FRED datasets. But Before I want to check the correlation between the two datasets for the overlapping period, to see if they are consistent with each other.

# Now I need to revert the order of the rows in the Muni_Benchmark
Muni_Benchmark_cleaned = Muni_Benchmark.iloc[6:, ] # Adjust the slice as needed
Muni_Benchmark_reversed = Muni_Benchmark_cleaned.iloc[::-1].reset_index(drop=True) #reversing the order of the rows in the Muni_Benchmark dataset
Muni_Benchmark_reversed_renamed = Muni_Benchmark_reversed.iloc[:, [0, 1, 2]].set_axis(ITR_df.columns, axis=1)

# Now I am going to merge the two datasets. ATTENTION gap of two end of months observations in 2008 (November and December) that are missing in both the original datasets.
ITR_df = pd.concat([ITR_df, Muni_Benchmark_reversed_renamed], axis=0, ignore_index=True)



# %% Now I need to estract end of month observations from the daily data for the Gov Bonds yields.

Gov_Bond_daily_df = pd.concat([Gov_Bond_1_daily.iloc[:, [0, 1]], Gov_Bond_5_daily.iloc[:, 1]], axis=1)
Gov_Bond_daily_df = Gov_Bond_daily_df.dropna()
# %%
