# %% [0] INSTALLATION OF REQUIRED PACKAGES
# Run this in your terminal if needed:
# !pip install pandas openpyxl google-generativeai python-dotenv

# %% [1] SETUP & IMPORTS
import pandas as pd
import json
import os
import time
import google.generativeai as genai
from   dotenv import load_dotenv

# Load API Key from .env file (for security and professional standard)
# Never hardcode keys directly in the script, git hub will block the licence if you do that, and it is a security risk.
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("API Key not found in .env file. Please ensure GEMINI_API_KEY is set.")

# Initialize the Gemini client
# Ensure your API key is set in your environment variables
# API = Application Programming Interface.
# API connects two softwares, the Python code and a LLM, allowing the code to send requests and receive responses from the LLM.
# We Should use the Chat GPT API for consistency, because the Oxford PhD studends have used it to analyze historical fiscal events
# But these API are pay as you go, at the moment we can try with the API free version from Google, if it works and this is the way we need to procede,
# maybe we can think about paying the OpenAI API

# At the moment given that I won't pay, I will use the Google free version of the API, which is free for a limited number of requests per month.
# If our number of request overcomes the free limit, we can think about LLM API which runs locally, they use the local GPU to run the model, but they are not as powerful as the OpenAI API.
# Now, I want that the LLM give me a reproducible output, So I need to set


# 1) The temperature to 0.0, which means that the model will always give the same output for the same input, making it deterministic and reproducible.
# 2) Rigid Model Versioning, not a generic LLM, but a constant model version, so that the model's behavior does not change over time.
# 3) Set a Seed forcing the server to use the same random number generator state for each request.

genai.configure(api_key=api_key)

# We use Gemini 1.5 Flash. 
# Why Gemini instead of OpenAI? 
# 1. Cost Efficiency: It offers a robust free tier, ideal for proof-of-concept and academic research.
# 2. Performance: It is highly capable for historical information retrieval tasks.
# 3. Research Independence: Using an alternative model allows for a robustness check against the original authors' GPT-4o-mini results.
# Note: If high-precision methodology replication is required by the PI later, we can pivot to OpenAI's API.
model = genai.GenerativeModel('gemini-2.5-flash')

print("Gemini API Client initialized successfully.")

# %% [2] DATA INITIALIZATION
# Define file path. Adjust the path if the file is in a different directory.
FILE_NAME = '../Disentangling_Fiscal_Event_Daily_Series.xlsx'

# Load dataset
df_raw = pd.read_excel(FILE_NAME)
print(f"Dataset loaded. Total rows: {len(df_raw)}")

# %% Preprocessing: Standardize column names
df_raw.columns = df_raw.columns.str.strip().str.lower()

# Identify the shock column
target_col_name = 'pv_change_fiscal_event' 
if target_col_name not in df_raw.columns and 'pv_change_fiscal_events' in df_raw.columns:
    target_col_name = 'pv_change_fiscal_events'

# Create the working DataFrame
df = df_raw[['date', target_col_name]].copy()

# Initialize result columns
for col in [ 'G', 'T', 'Positive_G', 'Negative_G', 'Positive_T', 'Negative_T']:
    df[col] = 0.0

# Add columns for LLM metadata
df['LLM_Driver'] = "N"
df['LLM_Explanation'] = ""

print(f"Working DataFrame ready. Column used for shock: '{target_col_name}'")
print(df.head())
# %% [3] LLM API FUNCTION
def get_fiscal_driver(date):
    """
    Sends the date to the LLM to retrieve the fiscal news driver.
    Uses temperature=0.0 to ensure deterministic, reproducible results.
    """
    prompt = f"""
    You are an expert US macroeconomic historian.
    
    Analyze historical US fiscal policy and financial news around the date: {date}.
    A non-zero fiscal shock occurred on this day, moving deficit expectations.
    
    Determine if the primary driver of this news was:
    - Government Spending (G)
    - Taxes (T)
    - None (N) if unidentifiable or ambiguous.
    
    Respond strictly with a JSON object containing exactly two keys:
    1. "driver": "G", "T", or "N"
    2. "explanation": A concise 1-2 sentence summary of the historical event with the reference.
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.0, # Ensures reproducibility
                response_mime_type="application/json", # Forces output format
            )
        )
        
        result = json.loads(response.text)
        return result.get("driver", "N"), result.get("explanation", "")
        
    except Exception as e:
        print(f"Error on date {date}: {e}")
        return "N", "API Error"

print("Function 'get_fiscal_driver' defined successfully.")

# %% [4] SINGLE ROW TEST
# Test the API with the first available shock
test_row = df[df[target_col_name] != 0].iloc[0]
test_date = test_row['date']
test_shock = test_row[target_col_name]

print(f"Testing API for Date: {test_date} | Shock Value: {test_shock}")

driver, explanation = get_fiscal_driver(test_date)

print(f"--- TEST RESULT ---")
print(f"Driver: {driver}")
print(f"Explanation: {explanation}")

# %% [5] ROW EVALUATION & SIGN MAPPING
# Note: Respecting the rate limit of 15 requests per minute for the free tier.
non_zero_indices = df[df[target_col_name] != 0].index.tolist()
test_indices = non_zero_indices[:5] # Process first 5 as a test
print(f"Processing {len(test_indices)} events...")

for idx in test_indices:
    i = df.at[idx, target_col_name]
    date_val = df.at[idx, 'date']
    
    driver, explanation = get_fiscal_driver(date_val)
    
    df.at[idx, 'LLM_Driver'] = driver
    df.at[idx, 'LLM_Explanation'] = explanation
    
    # Mapping logic for fiscal signs
    if driver == "G":
        df.at[idx, 'G'] = i
        if i > 0: df.at[idx, 'Positive_G'] = i
        elif i < 0: df.at[idx, 'Negative_G'] = i
            
    elif driver == "T":
        df.at[idx, 'T'] = i
        if i > 0: df.at[idx, 'Negative_T'] = i  # Deficit expansion -> Tax cut
        elif i < 0: df.at[idx, 'Positive_T'] = i  # Deficit contraction -> Tax hike
            
    time.sleep(4.5) # Rate limiting pause

print("Mapping complete.")

# %% [6] VERIFY RESULTS
processed_view = df.loc[test_indices, [
    'date', target_col_name, 'LLM_Driver', 'Positive_G', 'Negative_G', 'Positive_T', 'Negative_T'
]]
print(processed_view)
# %%
