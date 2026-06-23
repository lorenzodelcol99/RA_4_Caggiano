import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define the file name and column names
FILE_NAME = 'Disentanglying_Fiscal_Event_Daily_Series.xlsx'
DATE_COLUMN = 'Date'
VALUE_COLUMN = 'pv_change_fiscal_events'

# Load the Excel file
df = pd.read_excel(FILE_NAME)
df.head()