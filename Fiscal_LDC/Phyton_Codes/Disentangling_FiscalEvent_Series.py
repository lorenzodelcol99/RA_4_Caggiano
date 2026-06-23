# %% [0] Installation of required packages
# Uncomment the following lines if you need to install the packages in your environment
# !pip install openai

# %% [1] SETUP & IMPORTS
import pandas as pd
import json
import os
import time
from openai import OpenAI

# %% Initialize the OpenAI client
# Ensure your API key is set in your environment variables
# API connects two softwares, the Python code and the OpenAI API, allowing the code to send requests and receive responses from the LLM.
# We Should use the Chat GPT API for consistency, because the Oxford PhD studends have used it to analyze historical fiscal events
# But these API are pay as you go, at the moment we can try with the API free version from Google, if it works and this is the way we need to procede,
# maybe we can think about paying the OpenAI API

# At the moment given that I won't pay, I will use the Google free version of the API, which is free for a limited number of requests per month.

# Now, I want that the LLM give me a reproducible output, So I need to set 
# 1) The temperature to 0.0, which means that the model will always give the same output for the same input, making it deterministic and reproducible.
# 2) Rigid Model Versioning, not a generic LLM, but a constant model version, so that the model's behavior does not change over time.
# 3) Set a Seed forcing the server to use the same random number generator state for each request.

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# %% Define file paths based on the uploaded data
INPUT_FILE = "high_frequency_fiscal_shocks_data.xlsx - Data.csv"
OUTPUT_FILE = "classified_fiscal_events.csv"

print("Setup complete. Client initialized.")

# %% [2] DATA INITIALIZATION
# Load the raw dataset
df_raw = pd.read_csv(INPUT_FILE)

# Isolate the required columns to keep the dataframe clean
df = df_raw[['date', 'pv_change_fiscal_events']].copy()

# Initialize the 6 target columns with zeros
target_columns = ['Positive_G', 'Negative_G', 'Positive_T', 'Negative_T', 'G', 'T']
for col in target_columns:
    df[col] = 0.0

# Add columns for the LLM output to track explanations
df['LLM_Driver'] = "N"
df['LLM_Explanation'] = ""

print(f"Dataframe loaded. Shape: {df.shape}")
print(df.head())

# %% [3] LLM API FUNCTION
def query_llm_for_driver(date):
    """Invia la data all'LLM in modalità strettamente riproducibile."""
    system_prompt = (
        "You are an expert US macroeconomic historian. Your task is to identify the primary "
        "fiscal policy event or news that shifted economic expectations on a given date."
    )
    
    user_prompt = f"""
    Analyze historical US fiscal policy and financial news around the date: {date}.
    A non-zero fiscal shock occurred on this day, moving deficit expectations.
    
    Determine if the primary driver of this news was related to Government Spending (G) or Taxes (T).
    If it is impossible to identify or ambiguous, classify as None (N).
    
    Respond strictly with a JSON object containing exactly two keys:
    1. "driver": Must be exactly "G", "T", or "N"
    2. "explanation": A concise 1-2 sentence summary of the historical news event.
    """
    
    try:
        response = client.chat.completions.create(
            # 1. Usa un modello con una data fissa invece di quello generico
            model="gpt-4o-2024-05-13", 
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            # 2. Azzera la temperatura
            temperature=0.0, 
            # 3. Imposta un seed fisso per la riproducibilità
            seed=42 
        )
        
        content = json.loads(response.choices[0].message.content)
        return content.get("driver", "N"), content.get("explanation", "")
    except Exception as e:
        print(f"Errore API alla data {date}: {e}")
        return "N", f"Error: {str(e)}"

print("Function 'get_fiscal_driver' defined successfully.")

# %% [4] SINGLE ROW TEST
# Find the first date where a shock occurred to test the API
test_row = df[df['pv_change_fiscal_events'] != 0].iloc[0]
test_date = test_row['date']
test_shock = test_row['pv_change_fiscal_events']

print(f"Testing API for Date: {test_date} | Shock Value: {test_shock}")

# Run the function
test_driver, test_explanation = get_fiscal_driver(test_date)

print(f"Output Driver: {test_driver}")
print(f"Output Explanation: {test_explanation}")

# %% [5] ROW EVALUATION & SIGN MAPPING (PIPELINE)
# Filter indices where the event is not zero
non_zero_indices = df[df['pv_change_fiscal_events'] != 0].index.tolist()

# FOR TESTING: Limit to the first 10 events to check logic without high API costs
test_indices = non_zero_indices[:10] 
print(f"Processing {len(test_indices)} non-zero events...")

for idx in test_indices:
    i = df.at[idx, 'pv_change_fiscal_events']
    date_val = df.at[idx, 'date']
    
    # 1. API Call
    driver, explanation = get_fiscal_driver(date_val)
    
    # 2. Store raw text
    df.at[idx, 'LLM_Driver'] = driver
    df.at[idx, 'LLM_Explanation'] = explanation
    
    # 3. Sign Mapping and Assignment
    if driver == "G":
        df.at[idx, 'G'] = i
        if i > 0:
            df.at[idx, 'Positive_G'] = i
        elif i < 0:
            df.at[idx, 'Negative_G'] = i
            
    elif driver == "T":
        df.at[idx, 'T'] = i
        if i > 0:
            df.at[idx, 'Negative_T'] = i  # Deficit expands -> Tax cut
        elif i < 0:
            df.at[idx, 'Positive_T'] = i  # Deficit shrinks -> Tax hike
            
    # Rate limiting pause
    time.sleep(0.5)

print("Mapping complete for the test batch.")

# %% [6] VERIFY RESULTS & EXPORT
# View the rows we just processed to ensure the logic mapped variables to the right columns
processed_view = df.loc[test_indices, [
    'date', 'pv_change_fiscal_events', 'LLM_Driver', 
    'Positive_G', 'Negative_G', 'Positive_T', 'Negative_T'
]]
print(processed_view)

# Save to CSV
# df.to_csv(OUTPUT_FILE, index=False)
# print(f"File saved to {OUTPUT_FILE}")