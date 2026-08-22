import pandas as pd
import os

data_folder = "../data/raw"  # adjust if your CSVs are elsewhere

files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]

for file in files:
    path = os.path.join(data_folder, file)
    df = pd.read_csv(path)
    print("=" * 60)
    print(f"FILE: {file}")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nNull counts:\n{df.isnull().sum()}")
    print(f"\nDtypes:\n{df.dtypes}")
    print(f"\nSample rows:\n{df.head(3)}")
    print("\n")