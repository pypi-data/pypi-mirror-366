from functools import partial
import numpy as np
import pandas as pd
from string_date_controller import get_today, get_date_n_days_ago
from shining_pebbles import scan_files_including_regex
from canonical_transformer.morphisms import map_df_to_csv, map_csv_to_df
from fund_insight_engine.fund_data_retriever.fund_codes import get_fund_codes_all
from fund_insight_engine.fund_data_retriever.fund_codes.historical import (
    get_historical_fund_codes_all,
    get_historical_fund_codes_main, 
    get_historical_fund_codes_division_01, 
    get_historical_fund_codes_division_02, 
    get_historical_fund_codes_equity, 
    get_historical_fund_codes_equity_mixed, 
    get_historical_fund_codes_bond_mixed, 
    get_historical_fund_codes_multi_asset, 
    get_historical_fund_codes_variable, 
    get_historical_fund_codes_mothers, 
    get_historical_fund_codes_class, 
    get_historical_fund_codes_generals, 
    get_historical_fund_codes_nonclassified,
)
from fund_insight_engine.path_director import FILE_FOLDER
from fund_insight_engine.fund_data_retriever.basis import get_df_fund_data

get_df_firm_aum = partial(get_df_fund_data, key='순자산')

def get_firm_aum_total(option_save: bool = True)->pd.DataFrame:
    df_firm_aum_total = get_df_firm_aum(fund_codes_kernel=get_historical_fund_codes_all)
    if option_save:
        map_df_to_csv(df_firm_aum_total, file_folder=FILE_FOLDER['firm_aum'], file_name=f'dataset-firm_aum_total-save{get_today().replace("-", "")}.csv')
    return df_firm_aum_total

def load_firm_aum_total(file_folder: str = FILE_FOLDER['firm_aum'], regex='dataset-firm_aum_total-')->pd.DataFrame:
    file_names = scan_files_including_regex(file_folder=file_folder, regex=regex)
    file_name = file_names[-1]
    df = map_csv_to_df(file_folder=file_folder, file_name=file_name)
    return df

def map_label_to_historical_fund_codes_kernel(label: str):
    return {
        'all': get_historical_fund_codes_all,
        'main': get_historical_fund_codes_main,
        'division_01': get_historical_fund_codes_division_01,
        'division_02': get_historical_fund_codes_division_02,
        'equity': get_historical_fund_codes_equity,
        'equity_mixed': get_historical_fund_codes_equity_mixed,
        'bond_mixed': get_historical_fund_codes_bond_mixed,
        'multi_asset': get_historical_fund_codes_multi_asset,
        'variable': get_historical_fund_codes_variable,
        'mothers': get_historical_fund_codes_mothers,
        'class': get_historical_fund_codes_class,
        'generals': get_historical_fund_codes_generals,
        'nonclassified': get_historical_fund_codes_nonclassified,
    }[label]

def get_firm_aum_by_label(label: str, option_save: bool = True)->pd.DataFrame:
    df_firm_aum_total = load_firm_aum_total()
    df_firm_aum_by_label = df_firm_aum_total[map_label_to_historical_fund_codes_kernel(label)]
    if option_save:
        map_df_to_csv(df_firm_aum_by_label, file_folder=FILE_FOLDER['firm_aum'], file_name=f'dataset-firm_aum_{label}-save{get_today().replace("-", "")}.csv')
    return df_firm_aum_by_label

get_firm_aum_all = partial(get_firm_aum_by_label, label='all')
get_firm_aum_main = partial(get_firm_aum_by_label, label='main')
get_firm_aum_division_01 = partial(get_firm_aum_by_label, label='division_01')
get_firm_aum_division_02 = partial(get_firm_aum_by_label, label='division_02')
get_firm_aum_equity = partial(get_firm_aum_by_label, label='equity')
get_firm_aum_equity_mixed = partial(get_firm_aum_by_label, label='equity_mixed')
get_firm_aum_bond_mixed = partial(get_firm_aum_by_label, label='bond_mixed')
get_firm_aum_multi_asset = partial(get_firm_aum_by_label, label='multi_asset')
get_firm_aum_variable = partial(get_firm_aum_by_label, label='variable')
get_firm_aum_mothers = partial(get_firm_aum_by_label, label='mothers')
get_firm_aum_class = partial(get_firm_aum_by_label, label='class')
get_firm_aum_generals = partial(get_firm_aum_by_label, label='generals')
get_firm_aum_nonclassified = partial(get_firm_aum_by_label, label='nonclassified')
