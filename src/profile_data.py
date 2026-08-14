import pandas as pd
import re
from pathlib import Path


DATA_DIR = Path("data")


def normalize_name(value):
    """Normalize a name for comparison."""
    if pd.isna(value):
        return ""

    value = str(value).strip().lower()
    value = re.sub(r"\s+", " ", value)

    return value


def normalize_phone(value):
    """Convert phone numbers to a comparable 10-digit format."""
    if pd.isna(value):
        return ""

    digits = re.sub(r"\D", "", str(value))

    # Remove Indian country code if present
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]

    return digits


def inspect_file(name, filename):
    print("\n" + "=" * 70)
    print(f"{name.upper()}")
    print("=" * 70)

    df = pd.read_csv(DATA_DIR / filename)

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nMissing values:")
    print(df.isnull().sum())

    return df


# Load files
naukri = inspect_file(
    "Naukri",
    "source1_naukri_applicants.csv"
)

gig = inspect_file(
    "Gig Workers",
    "source2_gig_workers.csv"
)

cbnexus = inspect_file(
    "CBNexus",
    "source3_cbnexus_contacts.csv"
)


# ---------------------------------------------------------
# Normalize names
# ---------------------------------------------------------

naukri["name_normalized"] = naukri["Full Name"].apply(normalize_name)
gig["name_normalized"] = gig["worker_name"].apply(normalize_name)
cbnexus["name_normalized"] = cbnexus["Name"].apply(normalize_name)


# ---------------------------------------------------------
# Normalize phone numbers
# ---------------------------------------------------------

naukri["phone_normalized"] = naukri["Phone"].apply(normalize_phone)
cbnexus["phone_normalized"] = cbnexus["Phone Number"].apply(normalize_phone)


# ---------------------------------------------------------
# Find duplicate names inside each source
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("DUPLICATE NAMES")
print("=" * 70)

for name, df in [
    ("Naukri", naukri),
    ("Gig Workers", gig),
    ("CBNexus", cbnexus),
]:

    duplicates = df[df.duplicated("name_normalized", keep=False)]

    if len(duplicates) > 0:
        print(f"\n{name}:")
        print(duplicates.to_string(index=False))
    else:
        print(f"\n{name}: No duplicate names")


# ---------------------------------------------------------
# Find duplicate phones
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("DUPLICATE PHONES")
print("=" * 70)

for name, df in [
    ("Naukri", naukri),
    ("CBNexus", cbnexus),
]:

    valid = df[df["phone_normalized"] != ""]

    duplicates = valid[
        valid.duplicated("phone_normalized", keep=False)
    ]

    if len(duplicates) > 0:
        print(f"\n{name}:")
        print(
            duplicates[
                [col for col in df.columns if col != "name_normalized"]
            ].to_string(index=False)
        )
    else:
        print(f"\n{name}: No duplicate phones")


# ---------------------------------------------------------
# Find cross-source phone matches
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("CROSS-SOURCE PHONE MATCHES")
print("=" * 70)

phone_matches = naukri.merge(
    cbnexus,
    on="phone_normalized",
    how="inner",
    suffixes=("_naukri", "_cbnexus")
)

print(
    phone_matches[
        [
            "Full Name",
            "Phone",
            "Name",
            "Phone Number"
        ]
    ].to_string(index=False)
)


# ---------------------------------------------------------
# Find cross-source name matches
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("CROSS-SOURCE NAME MATCHES")
print("=" * 70)

name_matches = naukri.merge(
    cbnexus,
    on="name_normalized",
    how="inner",
    suffixes=("_naukri", "_cbnexus")
)

print(
    name_matches[
        [
            "Full Name",
            "Phone",
            "Name",
            "Phone Number"
        ]
    ].to_string(index=False)
)