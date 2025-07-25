import pandas as pd
import plotly.graph_objs as go

COLOR_PAIRS = [
    ("#1f77b4", "#ff7f0e"),
    ("#2ca02c", "#d62728"),
    ("#9467bd", "#8c564b"),
    ("#e377c2", "#7f7f7f"),
    ("#bcbd22", "#17becf"),
    ("#393b79", "#637939"),
    ("#8c6d31", "#843c39"),
    ("#7b4173", "#3182bd"),
]

def scale_columns(df: pd.DataFrame, columns: list[str]) -> list[str]:
    """
    Scales columns with very small values (< 0.01) to micro-units and renames them.

    Parameters:
        df (pd.DataFrame): The DataFrame with raw data.
        columns (list of str): Column names to check and potentially scale.

    Returns:
        list of str: Updated list of column names (some may be renamed to include ' (µ)').
    """
    updated_columns = []

    for col in columns:
        max_val = df[col].abs().max()
        if max_val < 0.01:
            scaled_col = f"{col} (µ)"
            df[col] = df[col] * 1e6
            df.rename(columns={col: scaled_col}, inplace=True)
            updated_columns.append(scaled_col)
        else:
            updated_columns.append(col)

    return updated_columns

def generate_plot(
    datasets: list[tuple[str, pd.DataFrame]],
    x_column: str,
    left_y_columns: list[str],
    right_y_columns: list[str],
    plot_modes: dict[str, str],
    color_pair: tuple[str, str],
    x_interaction: str = "Range Slider",
    graph_title: str = "Graph",
    x_label: str = "",
    y1_label: str = "",
    y2_label: str = "",
    notes: str = ""
) -> go.Figure:

    fig = go.Figure()

    for i, (label, df) in enumerate(datasets):
        color_pair = COLOR_PAIRS[i % len(COLOR_PAIRS)]
        current_color, voltage_color = color_pair

        # Step 1: Scale the columns
        scaled_left_y = scale_columns(df, left_y_columns)
        scaled_right_y = scale_columns(df, right_y_columns)

        # Step 2: Add left Y-axis traces
        for col in scaled_left_y:
            fig.add_trace(go.Scatter(
                x=df[x_column],
                y=df[col],
                mode=plot_modes.get(col, "lines" if x_column != "Cycle_Index" else "markers"),
                name=f"{label}: {col}",
                line=dict(color=current_color),
                yaxis='y1',
                marker=dict(size=10) if x_column == 'Cycle_Index' else None
            ))

        # Step 3: Add right Y-axis traces
        if scaled_right_y:
            for col in scaled_right_y:
                fig.add_trace(go.Scatter(
                    x=df[x_column],
                    y=df[col],
                    mode=plot_modes.get(col, "lines" if x_column != "Cycle_Index" else "markers"),
                    name=f"{label}: {col}",
                    line=dict(color=voltage_color),
                    yaxis='y2',
                    marker=dict(size=10) if x_column == 'Cycle_Index' else None
                ))
        else:
            # Add invisible dummy trace so right y-axis exists, preventing label disappearance
            fig.add_trace(go.Scatter(
                x=[None],
                y=[None],
                mode='lines',
                line=dict(color='rgba(0,0,0,0)'),
                showlegend=False,
                yaxis='y2'
            ))

    # Step 4: Configure rangeslider visibility and dragmode
    if x_interaction == "Range Slider":
        rangeslider_visible = True
        drag_mode_setting = "pan"  # Use pan to avoid zoom conflicts with slider
    elif x_interaction == "Drag Zoom":
        rangeslider_visible = False
        drag_mode_setting = "zoom"  # Allow drag to zoom on x axis
    else:
        rangeslider_visible = False
        drag_mode_setting = "pan"

    # Safe axis titles (never empty)
    y1_title = y1_label if y1_label else (' / '.join(scaled_left_y) if scaled_left_y else " ")
    y2_title = y2_label if y2_label else (' / '.join(scaled_right_y) if scaled_right_y else " ")
    graph_title_safe = graph_title if graph_title else "Battery Data"
    x_axis_title = x_label if x_label else x_column

    fig.update_layout(
        title=graph_title_safe,
        xaxis=dict(
            title=x_axis_title,
            rangeslider=dict(visible=rangeslider_visible)
        ),
        yaxis=dict(
            title=dict(text=y1_title, font=dict(color=current_color)),
            tickfont=dict(color=current_color)
        ),
        yaxis2=dict(
            title=dict(text=y2_title, font=dict(color=voltage_color)),
            tickfont=dict(color=voltage_color),
            overlaying='y',
            side='right'
        ),
        dragmode=drag_mode_setting,
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99)
    )

    if notes.strip():
        fig.add_annotation(
            text=notes.replace("\n", "<br>"),
            showarrow=False,
            xref="paper",
            yref="paper",
            x=1,
            y=1,
            xanchor="right",
            yanchor="top",
            align="right",
            font=dict(size=12, color="black"),
            bgcolor="rgba(255, 255, 255, 0.7)",
            bordercolor="lightgray",
            borderwidth=1,
            borderpad=4,
            opacity=1,
        )

    return fig
