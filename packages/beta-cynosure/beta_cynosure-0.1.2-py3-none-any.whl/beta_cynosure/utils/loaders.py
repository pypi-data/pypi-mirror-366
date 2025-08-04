import pandas as pd
from typing import List
from beta_cynosure.utils.downloader import download_zip

def load_csvs_from_zip(z, prefix: str = '', consolidated_only: bool = True) -> List[pd.DataFrame]:
    dataframes = []
    for filename in z.namelist():
        if not filename.lower().endswith('.csv'):
            continue
        if prefix and prefix.lower() not in filename.lower():
            continue
        if consolidated_only and '_con_' not in filename.lower():
            continue
        with z.open(filename) as fp:
            df = pd.read_csv(fp, sep=';', encoding='latin1', dtype=str)
            df.columns = [col.strip().upper() for col in df.columns]
            df['SOURCE_FILE'] = filename
            dataframes.append(df)
    return dataframes

def load_dfp_year(year: int) -> pd.DataFrame:
    url = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_{year}.zip"
    zip_file = download_zip(url)
    dfs = load_csvs_from_zip(zip_file, consolidated_only=True)
    for df in dfs:
        df['YEAR'] = year
    return pd.concat(dfs, ignore_index=True)

def load_itr_year(year: int) -> pd.DataFrame:
    url = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/itr_cia_aberta_{year}.zip"
    zip_file = download_zip(url)
    dfs = load_csvs_from_zip(zip_file, consolidated_only=True)
    for df in dfs:
        df['YEAR'] = year
    return pd.concat(dfs, ignore_index=True)

def load_fre_year(year: int) -> pd.DataFrame:
    url = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/fre_cia_aberta_{year}.zip"
    zip_file = download_zip(url)
    dfs = load_csvs_from_zip(zip_file, consolidated_only=True)
    for df in dfs:
        df['YEAR'] = year
    return pd.concat(dfs, ignore_index=True)