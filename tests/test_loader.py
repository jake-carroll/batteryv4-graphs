# test_loader.py

from backend.data_loader import load_excel_data

# Replace with a real file you want to test
file_path = r"C:\Users\jakeg\OneDrive\Desktop\Battery Graphs\Na_MCMB_Test_6.xls"
x_column = "Test_Time(s)"  # or "Cycle_Index"

try:
    df = load_excel_data(file_path, x_column)
    print("[SUCCESS] Data loaded!")
    print(f"Shape: {df.shape}")
    print("Columns:", df.columns.tolist())
except Exception as e:
    print(f"[ERROR] {e}")
