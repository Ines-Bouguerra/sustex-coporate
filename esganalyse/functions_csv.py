import numpy as np
import pandas as pd
from esganalyse.functions import classify_sentence_label

def read_from_csv(file_path):
    """function to read from a CSV file

    Args:
        file_path (_type_): file path to read from

    Returns:
        df _type_: dataframe from read_from_csv
    """
    df = pd.read_csv(file_path,delimiter=';')
    return df

def read_from_xlsx(file_path,sheet):
    """function to read from a xlsx file

    Args:
        file_path (_type_): file path to read from
        sheet (_type_): sheet name to read from

    Returns:
        df _type_: dataframe from read_from_xlsx
    """
    df = pd.read_excel(file_path, sheet_name=sheet)
    return df

def  read_sheet_names(file_path):
    """
    Function to read all sheet names from an Excel file.
    
    Parameters:
    file_path (str): The path to the Excel file.
    
    Returns:
    list: A list of sheet names in the Excel file.
    """
    excel_file = pd.ExcelFile(file_path)
    sheet_names = excel_file.sheet_names
    return sheet_names

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def calculate_based_columns(df,columns_list,pipe_env, pipe_soc, pipe_gov, pipe_esg):
    """ function to prepare columns to calculate esg score """
    column_env = []
    column_soc = []
    column_gov = []
    for i in range(len(columns_list)):
        label, score_class = classify_sentence_label(columns_list[i], pipe_env, pipe_soc, pipe_gov, pipe_esg)
        non_nan_values = df[columns_list[i]].dropna()
        if label is not None and score_class is not None and not non_nan_values.apply(lambda x: isinstance(x, str)).any():
                df[columns_list[i]] = df[columns_list[i]] / df[columns_list[i]].max()
                if label == "environmental":
                    column_env.append(columns_list[i])
                elif label == "social":
                    column_soc.append(columns_list[i])
                elif label == "governance":
                    column_gov.append(columns_list[i])
                    
    return column_env,column_soc,column_gov

def calculate_based_lignes(df,pipe_env, pipe_soc, pipe_gov, pipe_esg):
    """ function to prepare lignes to calculate esg score """
    list_esg=[]
    for i in range(len(df)):
        row = list(df.iloc[i])
        row_esg,x,column_env,column_soc,column_gov=get_row_esg(row,pipe_env, pipe_soc, pipe_gov, pipe_esg)
        print({"row_esg":row_esg,"column_env":column_env,"column_soc":column_soc,"column_gov":column_gov})
        print("hello", row_esg)
        if row_esg is not None:
            list_esg.append({x:row_esg})
    df_esg=create_dataframe(list_esg)        
    return column_env,column_soc,column_gov,df_esg

def get_row_esg(row,pipe_env, pipe_soc, pipe_gov, pipe_esg):
    """
    function to get the row contains faction e,s,g
    """
    column_env = []
    column_soc = []
    column_gov = []
    for x in row:
        if not pd.isna(x) and not is_number(x):
            label, _ = classify_sentence_label(x, pipe_env, pipe_soc, pipe_gov, pipe_esg)
            if label is not None :
                if label == "environmental":
                    column_env.append(x)
                elif label == "social":
                    column_soc.append(x)
                elif label == "governance":
                    column_gov.append(x)
                return row,x,column_env,column_soc,column_gov
    return None,None,column_env,column_soc,column_gov  

def create_dataframe(data):
    """
    Create a pandas DataFrame from a list of dictionaries where each dictionary represents a column.
    """
    df_dict = {}
    for item in data:
        for key, value in item.items():
            value = [v if v is not None else np.nan for v in value]
            df_dict[key] = value
    df = pd.DataFrame(df_dict)
    return df

def calculate_esg_number(df, column_gov, column_soc, column_env):
    """
    Function to calculate ESG scores for given column families and return a DataFrame with scores.
    
    Parameters:
    df (pd.DataFrame): The input DataFrame containing the factor scores.
    column_gov (list): List of columns representing Governance factors.
    column_soc (list): List of columns representing Social factors.
    column_env (list): List of columns representing Environmental factors.
    
    Returns:
    pd.DataFrame: DataFrame with ESG scores added.
    """
    # Initialize a list to collect the results
    results = []

    # Helper function to process each category
    def process_columns(columns, category, e_score_val=0, s_score_val=0, g_score_val=0):
        for col in columns:
            e_score = e_score_val if category != "environmental" else round(df[col].mean(), 2)
            s_score = s_score_val if category != "social" else round(df[col].mean(), 2)
            g_score = g_score_val if category != "governance" else round(df[col].mean(), 2)
            esg = round(df[col].mean(), 2)
            results.append({"factors": col, "category": category, "e_score": e_score, "s_score": s_score, "g_score": g_score, "esg_score": esg})

    # Process each category
    if column_gov:
        process_columns(column_gov, "governance", g_score_val=0)

    if column_soc:
        process_columns(column_soc, "social", s_score_val=0)

    if column_env:
        process_columns(column_env, "environmental", e_score_val=0)

    df_res = pd.DataFrame(results)

    return df_res


def read_all_sheets(file_path):
    excel_file = pd.ExcelFile(file_path)
    sheet_names = excel_file.sheet_names
    data_frames = {}

    for sheet in sheet_names:
        data_frames[sheet] = pd.read_excel(file_path, sheet_name=sheet)