import pandas as pd
import plotly.graph_objs as go
import webbrowser
import os
import shutil
import subprocess

# ==== USER SETTINGS ====
excel_files = [
    (r"C:\Users\jakeg\OneDrive\Desktop\Battery Graphs\Na_MCMB_Test_6.xls", "Na_MCMB_Test_6")
    #   (r"C:\Users\jakeg\OneDrive\Desktop\Battery Graphs\30Q_Anode_half_cell.xls", "30Q Anode HC")
    # Add more (path, label) pairs here
]

color_pairs = [
    ('blue', 'red'),
    ('green', 'orange'),
    ('purple', 'brown'),
    ('teal', 'magenta'),
    ('darkcyan', 'goldenrod'),
    ('navy', 'crimson'),
    # Add more as needed
]

x_column = 'Test_Time(s)'  # Options: 'Test_Time(s)', 'Cycle_Index'
left_y_columns = ['Current(A)']     # Options: 'Current(A)', 'Normalized_Capacity(mAh/g)'
right_y_columns = ['Voltage(V)']    # 'Voltage(V)'

plot_modes = {
    "Voltage(V)": "lines",
    "Current(A)": "lines",
    "Charge_Capacity(Ah)": "markers",
    "Discharge_Capacity(Ah)": "markers",
    "Cycle_Index": "markers"
}
# ========================

fig = go.Figure()

for idx, (file_path, custom_label) in enumerate(excel_files):
    if not file_path.strip():
        continue  # Skip empty lines

    try:
        sheet_prefix = "Statistics_1-" if x_column == "Cycle_Index" else "Channel_1-"
        sheet_names = pd.ExcelFile(file_path).sheet_names
        target_sheets = [s for s in sheet_names if s.startswith(sheet_prefix)]

        if not target_sheets:
            print(f"[ERROR] No matching sheet in {file_path}. Sheets: {sheet_names}")
            continue

        sheet_to_use = target_sheets[0]
        df = pd.read_excel(file_path, sheet_name=sheet_to_use)

        # Check for required columns
        required = [x_column] + left_y_columns + right_y_columns
        missing = [col for col in required if col not in df.columns]
        if missing:
            print(f"[ERROR] Missing columns in {file_path}: {missing}")
            print(f"[INFO] Available columns: {list(df.columns)}")
            continue

        label_prefix = custom_label if custom_label else f"Battery {idx + 1}"

        # === Auto-scale micro-units if needed ===
        def scale_columns(df, columns):
            new_cols = []
            for col in columns:
                max_val = df[col].abs().max()
                if max_val < 0.01:
                    df[col] = df[col] * 1e6
                    new_col = f"{col} (µ)"
                    df.rename(columns={col: new_col}, inplace=True)
                    new_cols.append(new_col)
                else:
                    new_cols.append(col)
            return new_cols

        scaled_left_y = scale_columns(df, left_y_columns)
        scaled_right_y = scale_columns(df, right_y_columns)

        current_color, voltage_color = color_pairs[idx % len(color_pairs)]

        # === Add traces ===
        for col in scaled_left_y:
            fig.add_trace(go.Scatter(
                x=df[x_column],
                y=df[col],
                mode=plot_modes.get(col, "lines" if x_column != "Cycle_Index" else "markers"),
                name=f"{label_prefix}: {col}",
                line=dict(color=current_color),
                yaxis='y1',
                marker=dict(size=10) if x_column == 'Cycle_Index' else None
            ))

        for col in scaled_right_y:
            fig.add_trace(go.Scatter(
                x=df[x_column],
                y=df[col],
                mode=plot_modes.get(col, "lines" if x_column != "Cycle_Index" else "markers"),
                name=f"{label_prefix}: {col}",
                line=dict(color=voltage_color),
                yaxis='y2',
                marker=dict(size=10) if x_column == 'Cycle_Index' else None
            ))

    except Exception as e:
        print(f"[ERROR] Could not process {file_path}: {e}")
        continue

left_y_title = ' / '.join(scaled_left_y)
right_y_title = ' / '.join(scaled_right_y)
# === Configure Layout ===
fig.update_layout(
    title="Na NFM Half Cell",
    xaxis=dict(title=x_column, rangeslider=dict(visible=True)),
    yaxis=dict(
        title=dict(
            text=' / '.join(scaled_left_y),
            font=dict(color='blue')
        ),
        tickfont=dict(color='blue')
    ),
    yaxis2=dict(
        title=dict(
            text=' / '.join(scaled_right_y),
            font=dict(color='red')
        ),
        tickfont=dict(color='red'),
        overlaying='y',
        side='right'
    ),
    legend=dict(x=0.01, y=0.99),
    hovermode='x unified'
)

# === Preview Plot in Local Browser ===
preview_file = "battery_preview.html"
fig.write_html(preview_file)
webbrowser.open(preview_file)

# === Ask User if the Graph is Good ===
response = input("Is the graph good to proceed and push to GitHub? (yes/no): ").strip().lower()

if response == "yes":
    graph_name = input("Enter a name for the graph file (without .html): ").strip()
    final_file = f"{graph_name}.html"
    fig.update_layout(title=graph_name)

    # Path to your GitHub repo folder
    repo_folder = r"C:\Users\jakeg\OneDrive\Desktop\Battery-graphs"
    destination_path = os.path.join(repo_folder, final_file)

    # Move the approved graph into the GitHub folder
    shutil.move(preview_file, destination_path)

    # Commit and push to GitHub
    try:
        subprocess.run(["git", "add", final_file], cwd=repo_folder, check=True)
        subprocess.run(["git", "commit", "-m", f"Add {final_file}"], cwd=repo_folder, check=True)
        subprocess.run(["git", "push"], cwd=repo_folder, check=True)
        print(f"[SUCCESS] {final_file} pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Git operation failed: {e}")

else:
    os.remove(preview_file)
    print("[INFO] Graph discarded. Nothing was pushed.")

# Generate and display HTML preview link
repo_raw_base = "https://raw.githubusercontent.com/jake-carroll/Battery-graphs/main"
preview_url = f"https://htmlpreview.github.io/?{repo_raw_base}/{final_file.replace(' ', '%20')}"
print(f"[SHAREABLE LINK] {preview_url}")

