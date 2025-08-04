import pandas as pd
from typing import List
from beta_cynosure.utils.cleaner import clean_financial_data, extract_quarter_number

def prepare_quarterly_data(df_itr_list: List[pd.DataFrame]) -> pd.DataFrame:
    itr_all = pd.concat(df_itr_list, ignore_index=True)
    itr_all = clean_financial_data(itr_all)
    itr_all = extract_quarter_number(itr_all)
    for col in ['DENOM_CIA', 'DS_CONTA', 'GRUPO_DFP']:
        if col not in itr_all.columns:
            itr_all[col] = pd.NA
    quarter_data = itr_all[['CNPJ_CIA', 'DENOM_CIA', 'CD_CONTA', 'DS_CONTA', 'GRUPO_DFP',
                            'VL_CONTA', 'TRIMESTRE', 'YEAR']].copy()
    quarter_data['TRIMESTRE'] = quarter_data['TRIMESTRE'].astype(int)
    quarter_data['VL_CONTA'] = pd.to_numeric(quarter_data['VL_CONTA'], errors='coerce').fillna(0.0)
    return quarter_data
