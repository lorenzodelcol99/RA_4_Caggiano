# %% [0] INSTALLATION OF REQUIRED PACKAGES
# Run this in your terminal if needed:
# !pip install pandas openpyxl google-generativeai python-dotenv

# %% [1] SETUP & IMPORTS
import pandas as pd
import numpy as np
import json
import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("API Key not found in .env file. Please ensure GEMINI_API_KEY is set.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')
print("Gemini API Client initialized successfully.")

# %% [2 & 3] DATA INITIALIZATION & TOP 5% EXTRACTION
FILE_NAME = '../Disentangling_Fiscal_Event_Daily_Series.xlsx'
OUTPUT_FILE = '../Classified_Fiscal_Events_Top5Percent.xlsx'

# Loading raw data and identifying target column
df_raw = pd.read_excel(FILE_NAME)
df_raw.columns = df_raw.columns.str.strip().str.lower()
target_col = 'pv_change_fiscal_event' if 'pv_change_fiscal_event' in df_raw.columns else 'pv_change_fiscal_events'

# Filtering out the non zero events and calculating the threshold (95th percentile)
non_zero_df = df_raw[df_raw[target_col] != 0]
threshold = non_zero_df[target_col].abs().quantile(0.95)

# Creating the df_top by copying rows above the threshold (date and shock only)
df_top = non_zero_df[non_zero_df[target_col].abs() >= threshold][['date', target_col]].copy()

# Initialization of new columns for the LLM on df_top
for col in ['G', 'T', 'Positive_G', 'Negative_G', 'Positive_T', 'Negative_T']:
    df_top[col] = np.nan
df_top['LLM_Driver'] = "N"
df_top['LLM_Explanation'] = ""

print(f"Top 5% fiscal events extracted: {len(df_top)} rows.")
print(df_top.head())

# %% [4] LLM API FUNCTION (NEWS CYCLE & CHERRY-PICKED PROMPT)
def get_fiscal_driver(date, max_retries=3):
    """Fetches fiscal drivers with strict reproducibility and auto-retry for 429s."""
    
    prompt = f"""
    <role>
    You are a US macroeconomic historian. 
    </role>
    <task>
    Analyze the historical news cycle surrounding this date: {date}.
    A massive, peak daily fiscal shock is recorded on this day. Your task is to identify what major fiscal policy news was breaking in the 48-to-72-hour window around this date (t-1 to t+1), and classify the primary driver as Government Spending (G), Tax changes (T), or Neutral/Mixed (N).
    </task>
    Analyze the following date: {date}.
    <data_context>
    CRITICAL METHODOLOGICAL CONSTRAINT: The dataset contains ONLY the top 5% largest fiscal shocks in magnitude. Remember that these are the 5% in magnitude largest daily shock of all the dataset, so probably we are omitting the surrounding smaller daily shocks.
    Furthermore, account for historical reporting lags: an event happening late on day t-1 is often printed in newspapers on day t or t+1. You must scan the tight window around {date} to find the specific breakthrough, major vote, or announcement that triggered this outsized macroeconomic reaction.
    </data_context>
    1. Determine if the fiscal policy news is primarily related to Government Spending (G) or Tax changes (T).
    2. YOU MUST CHOOSE EITHER 'G' OR 'T'. Determine the single most dominant factor in the macroeconomic news on this day.
    3. BE BALANCED: Do not assume every fiscal event is a Tax Act. Check if the event is related to military spending, infrastructure, or social programs (G) versus revenue changes (T).
    
    Respond strictly with JSON:
    {{"driver": "G" or "T", "explanation": "Provide a specific reason linking the shock to G or T."}}
    """
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0,
                    response_mime_type="application/json"
                )
            )
            result = json.loads(response.text)
            return result.get("driver", "Error"), result.get("explanation", "")
            
        except Exception as e:
            if "429" in str(e) or "Quota" in str(e):
                print(f"[Rate Limit] Pausing 60s for {date} (Attempt {attempt+1}/{max_retries})...")
                time.sleep(60)
            else:
                print(f"API Error on {date}: {e}")
                return "Error", "API Error"
                
    return "Error", "Max Retries Reached"

print("Function 'get_fiscal_driver' compiled successfully.")
# %% [6] ROW EVALUATION & SIGN MAPPING (RESUMABLE PIPELINE)
# need to think about the sign of the shocks: G positive when the shock is negative?..
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
# %% [7] EXPORT RESULTS
df_top.to_excel(OUTPUT_FILE, index=False)
print(f"Success! The current dataset has been saved to: {OUTPUT_FILE}")
# %%
