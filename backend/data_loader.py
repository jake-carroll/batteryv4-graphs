import pandas as pd

def load_excel_data(file_path: str, sheet_prefix: str) -> tuple[pd.DataFrame, list[str]]:
    """
    Loads and merges all relevant Excel sheets starting with the given prefix.

    Parameters:
        file_path (str): Path to the Excel file.
        sheet_prefix (str): Prefix to match sheet names (e.g., 'Channel_1-' or 'Statistics_1-').

    Returns:
        tuple: (Merged DataFrame, list of available column names)

    Raises:
        ValueError: If no matching sheets are found.
        RuntimeError: For any other data loading error.
    """
    try:
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names
        target_sheets = [s for s in sheet_names if s.startswith(sheet_prefix)]

        if not target_sheets:
            raise ValueError(f"No matching sheets in {file_path}. Available sheets: {sheet_names}")

        # Read and merge all matching sheets
        dataframes = [xls.parse(sheet_name=s) for s in target_sheets]
        merged_df = pd.concat(dataframes, ignore_index=True)
        available_columns = merged_df.columns.tolist()

        return merged_df, available_columns

    except Exception as e:
        raise RuntimeError(f"Failed to load Excel data from {file_path}: {e}")

def load_multiple_excel_files(files, sheet_prefix: str) -> list[tuple[str, pd.DataFrame, list[str]]]:
    results = []
    for file in files:
        try:
            label = file.name.rsplit('.', 1)[0]
            df, columns = load_excel_data(file, sheet_prefix)
            results.append((label, df, columns))
        except Exception as e:
            print(f"Skipping {file.name}: {e}")
            continue
    return results
