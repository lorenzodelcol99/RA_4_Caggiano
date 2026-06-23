# %% [0] Installation of required packages
# Decommenta questa riga se non hai ancora installato il pacchetto di Google
# !pip install pandas openpyxl google-generativeai

# %% [1] SETUP E IMPORTS
import pandas as pd
import json
import os
import time
import google.generativeai as genai

# %% Inizializza il client API di Gemini
# Assicurati di aver fatto export GEMINI_API_KEY="tua-chiave" nel terminale
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("API Key non trovata. Imposta la variabile d'ambiente GEMINI_API_KEY.")

genai.configure(api_key=api_key)

# Utilizziamo Gemini 1.5 Flash (adatto al limite Free Tier di 15 req/min)
model = genai.GenerativeModel('gemini-1.5-flash')

# Percorsi dei file
FILE_NAME = '../Disentangling_Fiscal_Event_Daily_Series.xlsx'
OUTPUT_FILE = 'classified_fiscal_events_gemini.csv'

# %% [2] DATA INITIALIZATION
# Carica il file Excel (richiede openpyxl installato)
df_raw = pd.read_excel(FILE_NAME)

# Uniforma i nomi delle colonne in minuscolo per evitare KeyError
df_raw.columns = df_raw.columns.str.strip().str.lower()

# Adatta il nome della colonna se nel file è singolare o plurale
target_col_name = 'pv_change_fiscal_event' 
if target_col_name not in df_raw.columns and 'pv_change_fiscal_events' in df_raw.columns:
    target_col_name = 'pv_change_fiscal_events'

# Isola le colonne necessarie
df = df_raw[['date', target_col_name]].copy()

# Inizializza le 6 colonne target con zeri
target_columns = ['Positive_G', 'Negative_G', 'Positive_T', 'Negative_T', 'G', 'T']
for col in target_columns:
    df[col] = 0.0

# Aggiunge le colonne per tracciare l'output dell'LLM
df['LLM_Driver'] = "N"
df['LLM_Explanation'] = ""

print(f"Dataframe caricato. Dimensioni: {df.shape}")
print(df.head())

# %% [3] LLM API FUNCTION
def get_fiscal_driver(date):
    """Invia la data all'LLM in modalità strettamente riproducibile."""
    
    # prompt combinato (Gemini unisce system e user prompt in questa chiamata base)
    prompt = f"""
    You are an expert US macroeconomic historian.
    
    Analyze historical US fiscal policy and financial news around the date: {date}.
    A non-zero fiscal shock occurred on this day, moving deficit expectations.
    
    Determine if the primary driver of this news was related to Government Spending (G) or Taxes (T).
    If it is impossible to identify or highly ambiguous, classify as None (N).
    
    Respond strictly with a JSON object containing exactly two keys:
    1. "driver": Must be exactly "G", "T", or "N"
    2. "explanation": A concise 1-2 sentence summary of the historical news event.
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.0, # Modalità deterministica
                response_mime_type="application/json", # Forza output strutturato
            )
        )
        
        result = json.loads(response.text)
        return result.get("driver", "N"), result.get("explanation", "")
    except Exception as e:
        print(f"Errore API alla data {date}: {e}")
        return "N", "API Error"

print("Funzione 'get_fiscal_driver' definita con successo.")

# %% [4] SINGLE ROW TEST
# Trova la prima riga non nulla per testare la chiamata
test_row = df[df[target_col_name] != 0].iloc[0]
test_date = test_row['date']
test_shock = test_row[target_col_name]

print(f"Test API per Data: {test_date} | Shock Value: {test_shock}")

# Esegue la funzione
test_driver, test_explanation = get_fiscal_driver(test_date)

print(f"Output Driver: {test_driver}")
print(f"Output Explanation: {test_explanation}")

# %% [5] ROW EVALUATION & SIGN MAPPING (PIPELINE)
# Filtra gli indici in cui lo shock non è zero
non_zero_indices = df[df[target_col_name] != 0].index.tolist()

# PER IL TEST: limita le iterazioni a 5 per verificare la logica
test_indices = non_zero_indices[:5] 
print(f"Elaborazione di {len(test_indices)} eventi non nulli...")

for idx in test_indices:
    i = df.at[idx, target_col_name]
    date_val = df.at[idx, 'date']
    
    # 1. Chiamata API
    driver, explanation = get_fiscal_driver(date_val)
    
    # 2. Archiviazione stringhe grezze
    df.at[idx, 'LLM_Driver'] = driver
    df.at[idx, 'LLM_Explanation'] = explanation
    
    # 3. Assegnazione logica dei segni
    if driver == "G":
        df.at[idx, 'G'] = i
        if i > 0:
            df.at[idx, 'Positive_G'] = i
        elif i < 0:
            df.at[idx, 'Negative_G'] = i
            
    elif driver == "T":
        df.at[idx, 'T'] = i
        if i > 0:
            df.at[idx, 'Negative_T'] = i  # Deficit si espande -> Taglio tasse
        elif i < 0:
            df.at[idx, 'Positive_T'] = i  # Deficit si restringe -> Aumento tasse
            
    # Pausa per Rate Limiting API Google
    time.sleep(4.5)

print("Mappatura completata per il batch di test.")

# %% [6] VERIFY RESULTS & EXPORT
# Mostra le righe elaborate per controllo visivo
processed_view = df.loc[test_indices, [
    'date', target_col_name, 'LLM_Driver', 
    'Positive_G', 'Negative_G', 'Positive_T', 'Negative_T'
]]
print(processed_view)

# Esportazione
# df.to_csv(OUTPUT_FILE, index=False)
# print(f"File salvato in {OUTPUT_FILE}")