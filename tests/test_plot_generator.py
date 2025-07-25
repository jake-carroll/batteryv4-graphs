import pandas as pd
from backend.plot_generator import scale_columns

def test_scale_columns():
    # Sample data with small and normal values
    data = {
        'Current(A)': [0.000005, 0.000007, 0.000004],
        'Voltage(V)': [3.7, 3.8, 3.75],
        'Capacity(Ah)': [0.02, 0.015, 0.025]
    }
    df = pd.DataFrame(data)

    # Columns to scale
    columns = ['Current(A)', 'Voltage(V)', 'Capacity(Ah)']

    # Apply scaling function
    updated_columns = scale_columns(df, columns)

    # Check that only 'Current(A)' was scaled and renamed
    assert 'Current(A) (µ)' in updated_columns
    assert 'Voltage(V)' in updated_columns
    assert 'Capacity(Ah)' in updated_columns

    # Check that data was scaled correctly
    assert (df['Current(A) (µ)'] > 1).all()  # micro-amperes should be large numbers now
    assert (df['Voltage(V)'] < 10).all()        # voltage remains the same

    print("test_scale_columns passed!")

if __name__ == "__main__":
    test_scale_columns()
