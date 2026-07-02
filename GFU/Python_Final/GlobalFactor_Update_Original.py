### Lorenzo Del Col 2026: Auto Update code for the Global Factor dataset of Global Financial Uncertainty (Caggiano & Castelnuovo 2023)

# %% 0; Packages
import os
import pandas as pd
import numpy as np
import openpyxl

# %% 
percorso_cartella = '/Users/lorenzodelcol/Desktop/GIT/RA_4_Caggiano/GFU/REPLICATION DROPBOX (NEW)/Raw data UPDATE/Updated 2026 Series'
os.chdir(percorso_cartella)

print("Adding the path")

# %% 1; Phase A and B:
# Phase A for the daily returns * 100 for Market returns and Exchange rates, and just copying the raw levels for the 10YR Bond Yields
# Phase B for the monthly SD and SK of the daily returns/levels, to be used in the final GFU dataset

# 1. Create a list of the 3 raw files, along with the names we want for the output files
datasets = [
    {
        "input": "No_DS_S-MKT_RETURNS_DEL_COL_Updated_2026.xlsx",
        "out_daily": "PHASE_A_MKT_daily_df.xlsx",
        "out_monthly": "PHASE_B_MKT_monthly_df.xlsx"
    },
    {
        "input": "No_DS_10YR_RETURNS_DEL_COL_update2026.xlsx",
        "out_daily": "PHASE_A_10YR_daily_df.xlsx",
        "out_monthly": "PHASE_B_10YR_monthly_df.xlsx"
    },
    {
        "input": "No_DS_EX_RETURNS_DEL_COL_Updated 2026.xlsx",
        "out_daily": "PHASE_A_EX_daily_df.xlsx",
        "out_monthly": "PHASE_B_EX_monthly_df.xlsx"
    }
]

# 2. Start the Master Loop
for data in datasets:
    file_path = data["input"]
    print(f"\n{'='*50}\n Starting to process: {file_path}")
    
    # Load the workbook
    all_sheets = pd.read_excel(file_path, sheet_name=None)
    daily_df = pd.DataFrame()

    # ==========================================
    # PHASE A: Calculate Daily Returns / Extract Raw Yields
    # ==========================================
    print("   -> Extracting raw data and computing daily returns/levels...")
    for country_name, df in all_sheets.items():
        try:
            # Grab Raw Data from Columns A and B, starting at Excel Row 8
            df_raw = df.iloc[7:, [0, 1]].copy()
            df_raw.columns = ["Date", "Raw_Value"]
            
            df_raw["Date"] = pd.to_datetime(df_raw["Date"], errors="coerce")
            df_raw["Raw_Value"] = pd.to_numeric(df_raw["Raw_Value"], errors="coerce")
            df_raw = df_raw.dropna()
            
            # =========================================================
            # LOGIC SPLIT: Returns vs Raw Levels
            # =========================================================
            if "10YR_RETURNS" in file_path:
                # For Bond Yields: keep the raw values without calculating daily returns
                df_raw[country_name] = df_raw["Raw_Value"]
            else:
                # For Market and Exchange Rates: compute daily percentage return
                df_raw[country_name] = df_raw["Raw_Value"].pct_change() * 100
                
            df_raw.set_index('Date', inplace=True)
            df_clean = df_raw[[country_name]].dropna()

            # =========================================================
            # INJECT HISTORICAL GREEK EX_RETURNS DATA 
            # =========================================================
            if "EX_RETURNS" in file_path and country_name == "Greece":
                old_gr = df.iloc[7:, [5, 6]].copy()
                old_gr.columns = ["Date", country_name]
                old_gr["Date"] = pd.to_datetime(old_gr["Date"], errors="coerce")
                old_gr[country_name] = pd.to_numeric(old_gr[country_name], errors="coerce")
                old_gr = old_gr.dropna().set_index("Date")
                
                df_clean = pd.concat([old_gr, df_clean])
                df_clean = df_clean.sort_index()
                df_clean = df_clean[~df_clean.index.duplicated(keep='last')]

            # =========================================================
            # INJECT HISTORICAL COLOMBIA MKT_RETURNS DATA
            # =========================================================
            if "MKT_RETURNS" in file_path and country_name == "Colombia":
                old_col = df.iloc[7:, [5, 6]].copy()
                old_col.columns = ["Date", country_name]
                old_col["Date"] = pd.to_datetime(old_col["Date"], errors="coerce")
                old_col[country_name] = pd.to_numeric(old_col[country_name], errors="coerce")                
                df_clean = old_col.dropna().set_index("Date")

            if daily_df.empty:
                daily_df = df_clean
            else:
                daily_df = daily_df.join(df_clean, how='outer')
                
        except Exception as e:
            print(f"  Could not process {country_name}. Error: {e}")

    daily_df = daily_df.sort_index()

    print("   -> Cleaning infinite values caused by Zero Lower Bound...")
    daily_df.replace([np.inf, -np.inf], np.nan, inplace=True)

    # ==========================================
    # PHASE B: Calculate Monthly SD and SK
    # ==========================================
    print("   -> Grouping into months and computing SD & SK...")
    monthly_df = daily_df.resample('MS').agg(['std', 'skew'])

    # Flatten the columns
    new_columns = []
    for country, stat in monthly_df.columns:
        if stat == 'std':
            new_columns.append(f'SD {country}')
        elif stat == 'skew':
            new_columns.append(f'SK {country}')
            
    monthly_df.columns = new_columns

    # ==========================================
    # SAVE TO EXCEL
    # ==========================================
    daily_df.index = daily_df.index.strftime('%Y-%m-%d')
    monthly_df.index = monthly_df.index.strftime('%Y-%m-%d')
    
    daily_df.to_excel(data["out_daily"])
    monthly_df.to_excel(data["out_monthly"])
    
    print(f" Complete! Saved daily and monthly files for this dataset.")

print(f"\n{'='*50}\n ALL 3 DATASETS HAVE BEEN SUCCESSFULLY PROCESSED!")


# %% Phase C:
# aggregate the three Phase B datasets into the GFU original dataset.

print("Building Phase C: Auto-filling the GFU Dataset with Smart Mapping...")

# 1. Load the original GF dataset file
gfu_skeleton = pd.read_excel('cc_globalfactor_1992M72020M5.xlsx', sheet_name='raw data')
target_columns = gfu_skeleton.columns.tolist()

# 2. Load the three Phase B dataframes
mkt_df  = pd.read_excel('PHASE_B_MKT_monthly_df.xlsx', index_col='Date', parse_dates=True)
ex_df   = pd.read_excel('PHASE_B_EX_monthly_df.xlsx', index_col='Date', parse_dates=True)
bond_df = pd.read_excel('PHASE_B_10YR_monthly_df.xlsx', index_col='Date', parse_dates=True)

# This removes any invisible spaces at the beginning or end of the column names
mkt_df.columns = [str(c).strip() for c in mkt_df.columns]
ex_df.columns = [str(c).strip() for c in ex_df.columns]
bond_df.columns = [str(c).strip() for c in bond_df.columns]

# 3. Create the New Timeline
start_date = '1992-07-01'
max_date = max(mkt_df.index.max(), ex_df.index.max(), bond_df.index.max())
new_dates = pd.date_range(start=start_date, end=max_date, freq='MS')

new_gfu = pd.DataFrame(index=new_dates, columns=target_columns)
new_gfu = new_gfu.drop(columns=['Date'], errors='ignore')

# ==========================================
# Mapping Dictionary
# ==========================================
aliases = {
    'Great Britain': ['UK', 'GB', 'Great Britain', 'United Kingdom'],
    'Czech Republic': ['Czech Rep', 'Czech', 'CZ'],
    'New Zeland': ['NZ', 'New Zealand'],
    'New Zealand': ['NZ'],
    'HK': ['Hong Kong', 'HK'],
    'Philippines': ['Philippine', 'Philippines', 'Phillipines']
}

def get_phase_b_column(df, country):
    """Cerca la colonna usando il nome originale, poi gli alias, poi le varianti US/USA"""
    if f"SD {country}" in df.columns:
        return f"SD {country}"
    
    if country in aliases:
        if isinstance(aliases[country], list):
            for possible_name in aliases[country]:
                if f"SD {possible_name}" in df.columns:
                    return f"SD {possible_name}"
        else:
            if f"SD {aliases[country]}" in df.columns:
                return f"SD {aliases[country]}"
        
    if country == 'US' and 'SD USA' in df.columns:
        return 'SD USA'
    if country == 'USA' and 'SD US' in df.columns:
        return 'SD US'
        
    return None

# ==========================================
# Inserting new data
# ==========================================
for col in new_gfu.columns:
    parts = col.rsplit('_', 1)
    
    if len(parts) == 2:
        # Clean up the parsed names to ensure accurate matching
        country = parts[0].replace('_', ' ').strip()
        var_type = parts[1].lower().strip()
        
        # Forziamo l'esclusione solo per i Bond Yields di Hong Kong
        if country in ['Hong Kong', 'HK'] and var_type.startswith('b'):
            continue
        
        target_df = None
        if var_type.startswith('st') or var_type == 's': 
            target_df = mkt_df
        elif var_type.startswith('ex') or var_type == 'e': 
            target_df = ex_df
        elif var_type.startswith('by') or var_type == 'b': 
            target_df = bond_df
            
        if target_df is not None:
            sd_col_name = get_phase_b_column(target_df, country)
            
            if sd_col_name:
                # Estraiamo la serie da mappare
                series = target_df[sd_col_name].copy()
                
                # Regola specifica per il Brasile: limitiamo i dati partendo dal 2006
                if country == 'Brazil':
                    series.loc[:'2005-12-31'] = float('nan')
                
                new_gfu[col] = series
            else:
                print(f" Attention: Haven't found data for '{country}' ({var_type})")

# ==========================================
# 6. Final Polish of name of the columns and dates
# ==========================================
new_gfu.index.name = 'Date'
new_gfu.reset_index(inplace=True)
new_gfu['Date'] = pd.to_datetime(new_gfu['Date']).dt.strftime('%d/%m/%Y')

# 7. Save the final output
output_name = 'cc_globalfactor_1992M72026M6_original_updated.xlsx'
new_gfu.to_excel(output_name, index=False)

print(f"\n Success! The dataset is mapped and saved as '{output_name}'")
# %%
