import os
import io
import json
import zipfile
import requests
from pathlib import Path
from typing import List
import shutil

import pandas as pd

from beta_cynosure.utils.companies_data import companies
from beta_cynosure.utils.loaders import load_dfp_year, load_itr_year
from beta_cynosure.utils.cleaner import clean_financial_data
from beta_cynosure.utils.processor import prepare_quarterly_data
from beta_cynosure.config.config import DFP_FILE, ITR_FILE, FRE_FILE


def ensure_output_dir():
    os.makedirs(os.path.dirname(DFP_FILE), exist_ok=True)


def run(years: List[int], prefix: str = None):
    ensure_output_dir()

    filtered_names = set()

    if prefix:
        for name, tickers in companies.items():
            for p in prefix:
                if any(t.upper().startswith(p.upper()) for t in tickers):
                    filtered_names.add(name)

        if not filtered_names:
            print(f"No company found for tickers: {', '.join(prefix)}")
            return

    # === DFP ===
    dfp_frames = []
    for year in years:
        try:
            dfp = load_dfp_year(year)
            dfp_frames.append(dfp)
        except Exception as exc:
            print(f"Error loading DFP {year}: {exc}")
    dfp_all = clean_financial_data(pd.concat(dfp_frames, ignore_index=True))

    if filtered_names:
        dfp_all = dfp_all[
            dfp_all["DENOM_CIA"]
            .str.upper()
            .apply(lambda x: any(name.upper() in x for name in filtered_names))
        ]

    for col in ["DENOM_CIA", "DS_CONTA", "GRUPO_DFP"]:
        if col not in dfp_all.columns:
            dfp_all[col] = pd.NA

    dfp_all[["CNPJ_CIA", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "GRUPO_DFP", "VL_CONTA", "YEAR"]].to_csv(DFP_FILE, index=False)

    # === ITR ===
    itr_frames = []
    for year in years:
        try:
            itr = load_itr_year(year)
            itr_frames.append(itr)
        except Exception as exc:
            print(f"Error loading ITR {year}: {exc}")
    quarter_data = prepare_quarterly_data(itr_frames)

    if filtered_names:
        quarter_data = quarter_data[
            quarter_data["DENOM_CIA"]
            .str.upper()
            .apply(lambda x: any(name.upper() in x for name in filtered_names))
        ]

    quarter_data.to_csv(ITR_FILE, index=False)

    # === Get CNPJs ===
    if not dfp_all.empty:
        cnpjs = set(dfp_all["CNPJ_CIA"].dropna().unique())
    elif not quarter_data.empty:
        cnpjs = set(quarter_data["CNPJ_CIA"].dropna().unique())
    else:
        cnpjs = set()

    if not cnpjs:
        print("No CNPJ found to filter FRE data.")
        return

    # === Map CNPJ → DENOM_CIA from ITR
    cnpj_to_name = {}
    if not quarter_data.empty:
        subset = quarter_data[["CNPJ_CIA", "DENOM_CIA"]].drop_duplicates()
        cnpj_to_name = dict(zip(subset["CNPJ_CIA"], subset["DENOM_CIA"]))

    # === Process FRE manually ===
    os.makedirs("fre_temp", exist_ok=True)
    fre_rows = []

    for year in years:
        print(f"Processing FRE {year}...")

        url = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/fre/DADOS/fre_cia_aberta_{year}.zip"
        try:
            response = requests.get(url)
            response.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(f"fre_temp/{year}")
        except Exception as e:
            print(f"Failed to download/extract FRE {year}: {e}")
            continue

        try:
            base = f"fre_temp/{year}"
            capital_path = os.path.join(base, f"fre_cia_aberta_capital_social_{year}.csv")
            dist_path = os.path.join(base, f"fre_cia_aberta_distribuicao_capital_{year}.csv")

            df_cap = pd.read_csv(capital_path, sep=';', encoding='latin1', dtype=str)
            df_dist = pd.read_csv(dist_path, sep=';', encoding='latin1', dtype=str)

            df_cap = df_cap[df_cap["CNPJ_Companhia"].isin(cnpjs)].drop_duplicates("CNPJ_Companhia")
            df_dist = df_dist[df_dist["CNPJ_Companhia"].isin(cnpjs)].drop_duplicates("CNPJ_Companhia")

            df_cap["Quantidade_Total_Acoes"] = pd.to_numeric(df_cap["Quantidade_Total_Acoes"], errors="coerce")
            df_dist["Quantidade_Total_Acoes_Circulacao"] = pd.to_numeric(df_dist["Quantidade_Total_Acoes_Circulacao"], errors="coerce")

            df_cap = df_cap[["CNPJ_Companhia", "Quantidade_Total_Acoes"]]
            df_dist = df_dist[["CNPJ_Companhia", "Quantidade_Total_Acoes_Circulacao"]]

            merged = pd.merge(df_cap, df_dist, on="CNPJ_Companhia", how="inner")
            merged.insert(0, "YEAR", year)
            merged = merged.rename(columns={"CNPJ_Companhia": "CNPJ"})

            # Add DENOM_CIA from ITR
            merged["DENOM_CIA"] = merged["CNPJ"].map(cnpj_to_name).fillna(pd.NA)

            fre_rows.append(merged)
            shutil.rmtree("fre_temp", ignore_errors=True)

        except Exception as e:
            print(f"Error processing FRE CSVs {year}: {e}")
            continue
        except Exception as e:
            print(f"Error processing FRE CSVs {year}: {e}")
            continue

    if fre_rows:
        final_fre = pd.concat(fre_rows, ignore_index=True)
        final_fre.to_csv(FRE_FILE, index=False)
        print(f"Process finished")
    else:
        print("No data returned.")
