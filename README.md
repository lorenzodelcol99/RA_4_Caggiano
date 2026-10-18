# Research assistance, Prof. Giovanni Caggiano, University of Padova

Work carried out since April 2026 as a Research Assistant. Two strands, both of which are mainly about producing and maintaining data.

## GFU, the global financial uncertainty index

The index of Caggiano and Castelnuovo (2023, Journal of Applied Econometrics) is built from a daily panel of 42 countries covering equity indices, ten year government bond yields and bilateral exchange rates against the dollar, aggregated to monthly volatility and skewness and then fed into a dynamic hierarchical factor model that separates a global factor from regional and country components.

My task was to update the dataset. Rather than update it once by hand, I wrote a pipeline that reproduces the whole construction from the raw exports.

`GFU/Python_Final/` holds the final scripts:

- `GlobalFactor.py` builds the panel from the three raw Datastream workbooks, equity indices, ten year yields and exchange rates, reading them sheet by sheet, cleaning the series, computing daily returns for equities and exchange rates, keeping yields in levels, joining them into a daily panel and aggregating to monthly moments.
- `GlobalFactor_Update_Original.py` writes the result back on the column structure of the original dataset, mapping each series by country and variable, so that hierarchy and ordering are preserved and the output can be dropped into the existing estimation code without further edits.
- `Pair_Correlation.py` compares a new vintage against the previous one, which is how breaks, gaps and discontinued series are caught.

`GFU/Analisi_Serie_Problematiche/` documents the series that needed a decision, for example the Brazilian exchange rate and the UK and New Zealand long term yields, where the original source changed or stopped.

`GFU/Python_latest/` and `GFU/Python_old/` are the working notebooks that led there, kept for the record.

The estimation is in MATLAB, in the replication package under `GFU/REPLICATION DROPBOX (NEW)/GlobalCodes_June2026/`. I ran the dynamic hierarchical factor model on the extended sample, from 1992M7 to 2026M6, after restoring functions that were missing from the package. The resulting factors and output are in `Output_Lorenzo/`.

## FISCAL, identifying fiscal shocks from text

`FISCAL/Fiscal_LDC/Phyton_Codes/` holds the scripts for the fiscal side of the project:

- `Disentangling_FiscalEvent_Series.py` and `Disentangling_FiscalEvent_top5%.py` take a list of fiscal event dates and, for each one, send a question to a large language model with web search, which reads US newspaper coverage around that date and returns structured JSON saying whether the event was driven by spending or by taxes. The output is in the classified event workbooks in the folder above.
- `LEEPER_ITR_End_of_Month.py` and `ITR_End_of_Month.py` rebuild an implied tax rate series at monthly frequency, splicing sources that overlap imperfectly.

## Work in progress

A third strand has just started and is not in this repository yet: a high frequency defence shock. We collect the dates of defence related news, align them with daily prices, and define narrow windows around each date in which we measure the excess returns of defence stocks over the market, so that the move inside the window can be read as the news itself. The aim is a high frequency counterpart to the defence news series used in the fiscal literature. The code will be added here once it is stable.

## Notes

The MATLAB code under `REPLICATION DROPBOX` is the authors' replication package and is not mine. The Python pipeline and the fiscal text classification are my own work.
