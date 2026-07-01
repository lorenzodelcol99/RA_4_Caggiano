# %% [0] INSTALLATION OF REQUIRED PACKAGES
# !pip install pandas openpyxl ollama python-dotenv

# %% [1] SETUP & IMPORTS
import pandas as pd
import json
import os
import time
import ollama 
import openpyxl

# %% [2] DATA INITIALIZATION & PROGRESS LOADING
FILE_NAME = '../Disentangling_Fiscal_Event_Daily_Series.xlsx'
OUTPUT_FILE = '../Classified_Fiscal_Events_Local_LLM.csv'

# Carica i progressi se il file CSV esiste già
if os.path.exists(OUTPUT_FILE):
    print(f"Loading existing progress from {OUTPUT_FILE}...")
    df = pd.read_csv(OUTPUT_FILE)
    # Assicura che le colonne necessarie esistano (in caso di caricamento CSV)
    for col in ['G', 'T', 'Positive_G', 'Negative_G', 'Positive_T', 'Negative_T', 'LLM_Driver', 'LLM_Explanation']:
        if col not in df.columns: df[col] = 0.0 if 'LLM' not in col else ""
else:
    print(f"Starting fresh from {FILE_NAME}...")
    df_raw = pd.read_excel(FILE_NAME)
    df_raw.columns = df_raw.columns.str.strip().str.lower()
    target_col_name = 'pv_change_fiscal_event' if 'pv_change_fiscal_event' in df_raw.columns else 'pv_change_fiscal_events'
    df = df_raw[['date', target_col_name]].copy()
    for col in ['G', 'T', 'Positive_G', 'Negative_G', 'Positive_T', 'Negative_T']:
        df[col] = 0.0
    df['LLM_Driver'] = "N"
    df['LLM_Explanation'] = ""

print(f"Working DataFrame ready. Total rows: {len(df)}")

# %% [3] LLM API FUNCTION (LOCAL OLLAMA)
import time
import json
import ollama

def get_fiscal_driver(date, max_retries=2):
    prompt = f"""
    System: You are an expert US macroeconomic historian.
    Task: On the specific date {date}, a significant fiscal policy event occurred in the United States. 
    You MUST search your internal knowledge base of historical newspapers, press releases, and official US government documents to identify this exact event.
    
    Rules for classification:
    - You MUST classify the event as either "G" or "T". There is no neutral option.
    - Return "G" if the event relates to Government Spending (e.g., military, infrastructure, budget acts, social programs, bailouts).
    - Return "T" if the event relates to Taxes (e.g., tax cuts, tax hikes, rebates, tariffs).
    
    Output requirement:
    Respond STRICTLY with a valid JSON object. Do not include any conversational text outside the JSON.
    
    Format:
    {{"driver": "G" or "T", "explanation": "Name the specific historical event found in newspapers/official documents and briefly state why it is G or T."}}
    """
    
    for attempt in range(max_retries):
        try:
            response = ollama.chat(
                model='llama3',
                messages=[{'role': 'user', 'content': prompt}],
                format='json',
                options={'temperature': 0.0, 'seed': 42}
            )
            result = json.loads(response['message']['content'])
            
            # Estrazione del risultato
            driver = result.get("driver", "").upper()
            
            # Controllo di sicurezza: se il modello devia, forziamo un errore di parsing 
            # piuttosto che inserire un dato sporco
            if driver not in ["G", "T"]:
                raise ValueError(f"Model output invalid driver: {driver}")
                
            return driver, result.get("explanation", "")
            
        except Exception as e:
            print(f"Error on {date} (Attempt {attempt+1}): {e}")
            time.sleep(2)
            
    # Se fallisce tutti i tentativi, restituisce un errore rintracciabile nel dataframe
    return "Error", "Forced binary classification failed or Local Processing Error"

# %% [4] SINGLE ROW TEST
#test_row = df[df['pv_change_fiscal_event' if 'pv_change_fiscal_event' in df.columns else 'pv_change_fiscal_events'] != 0].iloc[0]
#driver, explanation = get_fiscal_driver(test_row['date'])
#print(f"Test Result: {driver} - {explanation}")

# %% [5] ROW EVALUATION & SIGN MAPPING (RESUMABLE PIPELINE)
target_col = 'pv_change_fiscal_event' if 'pv_change_fiscal_event' in df.columns else 'pv_change_fiscal_events'
non_zero_indices = df[df[target_col] != 0].index.tolist()

print(f"Starting pipeline for {len(non_zero_indices)} events...")

for idx in non_zero_indices:
    # FILTRO AGGIORNATO: processa solo se non è mai stato analizzato con successo
    # Se il driver è ancora "N" (default) e non c'è una spiegazione, allora lavora.
    current_driver = str(df.at[idx, 'LLM_Driver'])
    current_expl = str(df.at[idx, 'LLM_Explanation'])
    
    # Processa solo se il driver è 'N' e la spiegazione è vuota/nulla
    if current_driver != "N" and current_expl not in ["", "nan", "None"]:
        continue 
        
    val = df.at[idx, target_col]
    driver, explanation = get_fiscal_driver(df.at[idx, 'date'])
    
    df.at[idx, 'LLM_Driver'] = driver
    df.at[idx, 'LLM_Explanation'] = explanation
    
    # Map signs
    if driver == "G":
        df.at[idx, 'G'] = val
        df.at[idx, 'Positive_G' if val > 0 else 'Negative_G'] = val
    elif driver == "T":
        df.at[idx, 'T'] = val
        df.at[idx, 'Negative_T' if val > 0 else 'Positive_T'] = val
            
    # Salva su disco dopo OGNI riga
    df.to_csv(OUTPUT_FILE, index=False)
    
    # Print di controllo
    count = non_zero_indices.index(idx)
    if count % 10 == 0:
        print(f"Progress: {count} / {len(non_zero_indices)} - Processed: {df.at[idx, 'date']} -> {driver}")

print("=== FULL DATASET MAPPING COMPLETE ===")

# %% [6] EXPORT RESULTS
# Save the fully processed DataFrame to a CSV file so the data is permanently stored

df.to_csv(OUTPUT_FILE, index=False)
print(f"Success! The fully classified dataset has been saved to: {OUTPUT_FILE}")
# %%
