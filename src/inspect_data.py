import pandas as pd
from pathlib import Path


DATA_DIR = Path("data")

files = {
    "naukri": DATA_DIR / "source1_naukri_applicants.csv",
    "gig_workers": DATA_DIR / "source2_gig_workers.csv",
    "cbnexus": DATA_DIR / "source3_cbnexus_contacts.csv",
}


for source, file_path in files.items():
    print("\n" + "=" * 60)
    print(f"{source.upper()}")
    print("=" * 60)

    df = pd.read_csv(file_path)

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumns:")
    print(list(df.columns))

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nFirst 5 rows:")
    print(df.head())