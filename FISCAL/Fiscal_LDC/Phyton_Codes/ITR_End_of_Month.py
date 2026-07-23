# %% [1] SETUP & IMPORTS
import pandas as pd
import numpy as np

# %% [2] Loading Raw Data

OUTPUT_FILE = '../ITR_dataframe.xlsx'

# Loading raw data
Muni_Benchmark        = pd.read_excel('../Muni_Benchmark.xlsx', sheet_name='Worksheet') # Municipal Bond Yields for 1,2,3,5,10,15,20 and 30 year maturities. END OF MONTH data from December 1949 to October 2008
MunisData2            = pd.read_excel('../MunisData2.xlsx', sheet_name='SubData')     # Municipal Bond Yields for 1,5, 10 and 20 year maturities. END OF MONTH data from July 2024 to January 2009 (NEED TO REVERSE THE ORDER)
# need to extract the folder "SubData" and update it
# (MISSING NOVEMEBR AND DECEMBER 2008) the two datasets are combined to create a continuous time series of Municipal Bond Yields from December 1949 to July 2024 (with this two month gap in 2008)

# In Muni_Benchmark we have data for gov bonds yields that are not available from the FRED site.
# After having done the end of month extration from the daily data, I want to check the correlation between the data gov bonds data from the fren and the one from Leeper

Gov_Bond_1_daily      = pd.read_excel('../DGS1.xlsx', sheet_name='Daily')
Gov_Bond_5_daily      = pd.read_excel('../DGS5.xlsx', sheet_name='Daily')
# need to extract the gov bonds end of months from the daily data and mearge it in the Muni_Benchmark"SubData"

# When we are going to have daily data for the Municipal Bond Yield from Bloomberg
# Muni_Bond_1_daily   = pd.read_excel('../Muni_Bond_1_daily.xlsx')
# Muni_Bond_5_daily   = pd.read_excel('../Muni_Bond_5_daily.xlsx')

# %% [3] Data Cleaning and Preprocessing





df_raw.columns = df_raw.columns.str.strip().str.lower()
target_col = 'pv_change_fiscal_event' if 'pv_change_fiscal_event' in df_raw.columns else 'pv_change_fiscal_events'

# Filtering out the non zero events and calculating the threshold (95th percentile)
non_zero_df = df_raw[df_raw[target_col] != 0]
threshold = non_zero_df[target_col].abs().quantile(0.95)

# Creating the df_top Creating the df_top by copying rows above the threshold (date and shock only)
df_top = non_zero_df[non_zero_df[target_col].abs() >= threshold][['date', target_col]].copy()

# Initialization of new columns for the LLM on df_top
for col in ['G', 'T', 'Positive_G', 'Negative_G', 'Positive_T', 'Negative_T']:
    df_top[col] = np.nan
df_top['LLM_Driver'] = "Pending"
df_top['LLM_Explanation'] = ""

print(f"Top 5% fiscal events extracted: {len(df_top)} rows.")
print(df_top.head())


# %% [6] ROW EVALUATION & SIGN MAPPING (RESUMABLE PIPELINE)
indices = df_top.index.tolist()
print(f"Starting pipeline for {len(indices)} events...")

for idx in indices:
    # Convert to string to safely handle Excel's NaN values for empty cells
    current_expl = str(df_top.at[idx, 'LLM_Explanation']).strip()
    
    if current_expl not in ["", "nan", "None", "API Error", "Max Retries Reached"]:
        continue 
        
    val = df_top.at[idx, target_col] 
    date_val = df_top.at[idx, 'date']
    
    if indices.index(idx) % 10 == 0:
        print(f"Processing row {indices.index(idx)} / {len(indices)}")
    
    driver, explanation = get_fiscal_driver(date_val)
    
    df_top.at[idx, 'LLM_Driver'] = driver
    df_top.at[idx, 'LLM_Explanation'] = explanation
    
    if explanation == "Max Retries Reached":
        print("Daily API limit reached. Stopping pipeline and saving progress.")
        break

    if driver == "G":
        df_top.at[idx, 'G'] = val
        df_top.at[idx, 'Positive_G' if val > 0 else 'Negative_G'] = val
    elif driver == "T":
        df_top.at[idx, 'T'] = val
        df_top.at[idx, 'Negative_T' if val > 0 else 'Positive_T'] = val
            
    df_top.to_excel(OUTPUT_FILE, index=False)
    time.sleep(20) 

print("=== FULL DATASET MAPPING COMPLETE ===")
