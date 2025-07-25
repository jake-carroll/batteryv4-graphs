# Run this syntax to open the browser app: .\.venv\Scripts\python.exe -m streamlit run ui/app.py

import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.plot_generator import generate_plot
from backend.data_loader import load_multiple_excel_files
from backend.plot_generator import COLOR_PAIRS

st.set_page_config(page_title="BatteryV4 Local", layout="wide")
st.title("🔋 Battery Graph Preview")

# Upload Excel file
uploaded_files = st.file_uploader("Upload one or more Excel files:", type=["xls", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    try:
        # Let user select data source type
        sheet_type = st.radio("Choose data source:", ["Channel", "Statistics"], horizontal=True)
        sheet_prefix = "Channel_1-" if sheet_type == "Channel" else "Statistics_1-"

        # Load and combine all uploaded files
        loaded_files = load_multiple_excel_files(uploaded_files, sheet_prefix)
        datasets = [(label, df) for label, df, _ in loaded_files]
        all_columns = set()
        for _, df, cols in loaded_files:
            all_columns.update(cols)
        available_columns = sorted(list(all_columns))

        default_x = "Test_Time(s)" if "Test_Time(s)" in available_columns else available_columns[0]
        x_column = st.selectbox("Select X-axis column:", options=available_columns, index=available_columns.index(default_x))

        # 1. Derived Column UI Section
        st.subheader("📐 Derived Columns")
        with st.expander("Configure Derived Columns"):

            add_norm_capacity = st.checkbox("Add Normalized Capacity (mAh/g)")
            if add_norm_capacity:
                weight = st.number_input("Enter Active Material Mass (g):", min_value=0.0001, format="%.4f")
                cap_type = st.radio("Use which capacity column?", ["Discharge_Capacity(Ah)", "Charge_Capacity(Ah)"], index=0)

            add_coulombic_efficiency = st.checkbox("Add Coulombic Efficiency")

        # 2. Apply Derived Columns to All Datasets
        derived_datasets = []
        for label, df in datasets:
            df = df.copy()

            # Normalized Capacity
            if add_norm_capacity and cap_type in df.columns and weight:
                df["Normalized Capacity"] = df[cap_type].diff() * 1000 / weight
                available_columns.append("Normalized Capacity")

            # Coulombic Efficiency
            if add_coulombic_efficiency:
                if "Discharge_Capacity(Ah)" in df.columns and "Charge_Capacity(Ah)" in df.columns:
                    charge_cap = df["Charge_Capacity(Ah)"].replace(0, pd.NA)
                    df["Coulombic Efficiency"] = df["Discharge_Capacity(Ah)"] / charge_cap
                    available_columns.append("Coulombic Efficiency")

            derived_datasets.append((label, df))

        # Set defaults using columns from the already-loaded df
        default_left_y = "Current(A)" if "Current(A)" in available_columns else available_columns[0]
        default_right_y = "Voltage(V)" if "Voltage(V)" in available_columns else available_columns[0]

        left_y_columns = st.multiselect("Select Left Y-axis column(s):", options=available_columns, default=[default_left_y])
        right_y_columns = st.multiselect("Select Right Y-axis column(s):", options=available_columns, default=[default_right_y])

        left_y_columns = [col for col in left_y_columns if col in df.columns]
        right_y_columns = [col for col in right_y_columns if col in df.columns]

        default_y1_label = "Current (µA)" if "Current(A)" in left_y_columns else "Current (A)"
        default_y2_label = "Current (µA)" if "Current(A)" in right_y_columns else "Voltage (V)"

        # Set colors
        for i, (label, df) in enumerate(datasets):
            color_pair = COLOR_PAIRS[i % len(COLOR_PAIRS)]

        # 🟡 Step 1: Add the label UI inputs *after* x_column is set
        st.subheader("Customize Graph Labels")
        graph_title = st.text_input("Graph Title", value="Battery Data")
        x_axis_label = st.text_input("X-axis Label", value=x_column)
        y1_label = st.text_input("Left Y-axis Label", value=default_y1_label)
        y2_label = st.text_input("Right Y-axis Label", value=default_y2_label)


        # ✏️ Extra Notes Section
        st.subheader("Optional Graph Notes")
        graph_notes = st.text_area("Add notes or comments to display on the graph:")

        # 🎚️ Toggle between line and dot plots
        plot_style = st.radio("Select Plot Style:", options=["Lines", "Dots"], horizontal=True)
        plot_mode_type = "markers" if plot_style == "Dots" else "lines"
        plot_modes = {col: plot_mode_type for col in left_y_columns + right_y_columns}

        # 📏 X-axis Interactivity Control
        x_interaction = st.radio("X-axis Interaction:", options=["Range Slider", "Drag Zoom"], horizontal=True)

        # 🟢 Now pass those into the plot function
        fig = generate_plot(
            datasets=derived_datasets,
            x_column=x_column,
            left_y_columns=left_y_columns,
            right_y_columns=right_y_columns,
            plot_modes=plot_modes,
            color_pair=color_pair,
            graph_title=graph_title,
            x_label=x_axis_label,
            y1_label=y1_label,
            y2_label=y2_label,
            notes=graph_notes,
            x_interaction=x_interaction
        )

        # 🟢 Finalize + Save Section
        st.subheader("Finalize Graph")
        finalize = st.button("Finalize & Save as HTML")

        if finalize:
            # Generate clean filename from graph title
            safe_title = graph_title.strip().replace(" ", "_").replace("/", "-")
            save_path = f"saved_graphs/{safe_title}.html"

            # Make sure the directory exists
            os.makedirs("saved_graphs", exist_ok=True)

            # Save interactive Plotly figure as HTML
            fig.write_html(save_path, full_html=True, include_plotlyjs='embed')

            # Show success message and access path
            st.success(f"Graph saved to: {save_path}")
            st.markdown(f"[Click to open graph](file://{os.path.abspath(save_path)})")

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading or plotting file: {e}")
