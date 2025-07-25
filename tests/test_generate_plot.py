import pandas as pd
import webbrowser
from backend.plot_generator import generate_plot

# Sample data (some small values to trigger scaling)
df = pd.DataFrame({
    'Test_Time(s)': [0, 1, 2, 3, 4],
    'Current(A)': [0.000004, 0.000005, 0.000006, 0.0000055, 0.0000045],
    'Voltage(V)': [3.7, 3.75, 3.8, 3.78, 3.76],
})

# Plot settings
x_column = 'Test_Time(s)'
left_y_columns = ['Current(A)']
right_y_columns = ['Voltage(V)']
label_prefix = 'Test Cell'
plot_modes = {
    "Current(A)": "lines",
    "Voltage(V)": "lines"
}
color_pair = ('blue', 'red')

# Generate the figure
fig = generate_plot(
    df=df,
    x_column=x_column,
    left_y_columns=left_y_columns,
    right_y_columns=right_y_columns,
    label_prefix=label_prefix,
    plot_modes=plot_modes,
    color_pair=color_pair
)

# Save and open preview
preview_file = "test_generate_plot_output.html"
fig.write_html(preview_file)
webbrowser.open(preview_file)

print("Plot generated and opened in browser.")
