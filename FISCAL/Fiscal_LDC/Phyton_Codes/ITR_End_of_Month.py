# %% [1] SETUP & IMPORTS
import pandas as pd
import numpy as np
import os # Operationg System, used to map the path of the files (working directory)

# %% [2] Loading Raw Data

# Setting the Working Directory to the location of the raw data files
os.chdir('/Users/lorenzodelcol/Desktop/GIT/RA_4_Caggiano/FISCAL/Fiscal_Data/Initial_Cagg_Material/')

OUTPUT_FILE = '../ITR_dataframe.xlsx'
OUTPUT_Gov_FILE = '../Fred_Gov_Bond_End_of_Month_df.xlsx'

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
Muni_Benchmark_cleaned = Muni_Benchmark.iloc[6:, ] # removing the first rows that contain information about data sources
Muni_Benchmark_reversed = Muni_Benchmark_cleaned.iloc[::-1].reset_index(drop=True) #reversing the order of the rows in the Muni_Benchmark dataset
Muni_Benchmark_reversed_renamed = Muni_Benchmark_reversed.iloc[:, [0, 1, 2]].set_axis(ITR_df.columns, axis=1)

# Now I am going to merge the two datasets. ATTENTION gap of two end of months observations in 2008 (November and December) that are missing in both the original datasets.
ITR_df = pd.concat([ITR_df, Muni_Benchmark_reversed_renamed], axis=0, ignore_index=True)



# %% Now I need to estract end of month observations from the daily data for the Gov Bonds yields.

# Mearging the two daily datasets for the Gov Bonds yields (1YR and 5YR) into a single dataframe
Gov_Bond_daily_df = pd.concat([Gov_Bond_1_daily.iloc[:, [0, 1]], Gov_Bond_5_daily.iloc[:, 1]], axis=1)
Gov_Bond_daily_df = Gov_Bond_daily_df.dropna()

# Creating the end of month dataframe for the Gov Bonds yields by grouping the daily data by month and taking the last observation of each month
Gov_Bond_End_of_Month_df = Gov_Bond_daily_df.groupby(Gov_Bond_daily_df['observation_date'].dt.to_period('M')).last().reset_index(drop=True)

# Gov_Bond_End_of_Month_df.to_excel(OUTPUT_Gov_FILE, index=False)
# %% Now I want to check the correlation between the two datasets for the overlapping period, to see if they are consistent with each other.
# Easier and faster to do in excel. Done, correlation is almost perfect, both 0.996 
# Now I can use the Leeper's gov data that is not present in the FRED datasets: from April 1953 to Jan 1962
# [0:105] From April 1953 to December 1961 included

Leeper_Gov_Bond_End_of_Month_df = MunisData2.iloc[0: 105, [0, 2, 5 ]].set_axis(Gov_Bond_End_of_Month_df.columns, axis=1)

Gov_Bond_End_of_Month_df = pd.concat([Leeper_Gov_Bond_End_of_Month_df, Gov_Bond_End_of_Month_df], axis=0, ignore_index=True)

# %% Mearging the Gov Bonds yields end of month dataframe with the Municipal Bonds yields end of month dataframe into a single dataframe

# Uniforming the name of the date columns
ITR_df.rename(columns={ITR_df.columns[0]: 'Date'}, inplace=True)
Gov_Bond_End_of_Month_df.columns = ['Date', 'Gov_1YR', 'Gov_5YR']

# make sure the date columns are in the same format (datetime) for the merge
ITR_df['Date'] = pd.to_datetime(ITR_df['Date'])
Gov_Bond_End_of_Month_df['Date'] = pd.to_datetime(Gov_Bond_End_of_Month_df['Date'])

# mearging the two dataframes safety using the 'Date' column as the key and using a left join to keep all the rows from ITR_df
ITR_df = pd.merge(ITR_df, Gov_Bond_End_of_Month_df, on='Date', how='left')

#ITR_df['Gov_1YR'] = Gov_Bond_End_of_Month_df.iloc[:, 1] # this line dis-aligns the series because in Municipal Bond Yiels we are missing november and december 2008

# %% [4] Update of Implied Tax Rate (ITR) for the 1YR and 5YR maturities

ITR_df['ITR_1YR'] = 1 - (ITR_df['Muni1'] / ITR_df['Gov_1YR'])
ITR_df['ITR_5YR'] = 1 - (ITR_df['Muni5'] / ITR_df['Gov_5YR'])


# %% SAVE ITR_df to Excel
ITR_df.to_excel(OUTPUT_FILE, index=False)
Gov_Bond_End_of_Month_df.to_excel(OUTPUT_Gov_FILE, index=False)
# %%
