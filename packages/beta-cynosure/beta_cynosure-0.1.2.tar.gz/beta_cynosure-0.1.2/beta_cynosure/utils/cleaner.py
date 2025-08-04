import pandas as pd

def clean_financial_data(df: pd.DataFrame) -> pd.DataFrame:
    df['VL_CONTA'] = pd.to_numeric(df['VL_CONTA'], errors='coerce')
    date_cols = [col for col in ['DT_REFER', 'DT_FIM_EXERC', 'DT_FIM_TRIM'] if col in df.columns]
    df['DATE'] = pd.to_datetime(df[date_cols[0]], errors='coerce') if date_cols else pd.NaT
    if 'ORDEM_EXERC' in df.columns:
        order_map = {'PENÚLTIMO': 0, 'ANTE-PENÚLTIMO': 1, 'ÚLTIMO': 2}
        df['ORDER_RANK'] = df['ORDEM_EXERC'].map(order_map).fillna(-1)
        df = df.sort_values(['CNPJ_CIA', 'CD_CONTA', 'DATE', 'ORDER_RANK'])
    else:
        df = df.sort_values(['CNPJ_CIA', 'CD_CONTA', 'DATE'])
    return df.drop_duplicates(subset=['CNPJ_CIA', 'CD_CONTA', 'DATE'], keep='last')

def extract_quarter_number(df: pd.DataFrame) -> pd.DataFrame:
    if 'TRIMESTRE' in df.columns:
        df['TRIMESTRE'] = pd.to_numeric(df['TRIMESTRE'], errors='coerce')
        return df
    if 'DT_FIM_EXERC' in df.columns:
        dates = pd.to_datetime(df['DT_FIM_EXERC'], errors='coerce')
    else:
        dates = df['DATE']
    df['TRIMESTRE'] = ((dates.dt.month - 1) // 3) + 1
    return df
