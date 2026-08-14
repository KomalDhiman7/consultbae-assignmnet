# import pandas as pd
# import re
# from pathlib import Path


# DATA_DIR = Path("data")
# OUTPUT_DIR = Path("data/cleaned")

# OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# # ---------------------------------------------------------
# # Normalization functions
# # ---------------------------------------------------------

# def normalize_name(value):
#     if pd.isna(value):
#         return ""

#     value = str(value).strip().lower()
#     value = re.sub(r"\s+", " ", value)

#     return value


# def normalize_email(value):
#     if pd.isna(value):
#         return ""

#     return str(value).strip().lower()


# def normalize_phone(value):
#     if pd.isna(value):
#         return ""

#     digits = re.sub(r"\D", "", str(value))

#     if len(digits) == 12 and digits.startswith("91"):
#         digits = digits[2:]

#     return digits


# def normalize_city(value):
#     if pd.isna(value):
#         return ""

#     city = str(value).strip().lower()

#     city_aliases = {
#         "bangalore": "bengaluru",
#         "gurugram": "gurgaon",
#         "new delhi": "delhi",
#     }

#     return city_aliases.get(city, city)


# def normalize_status(value):
#     if pd.isna(value):
#         return ""

#     return str(value).strip().lower()


# def parse_rate(value):
#     """
#     Convert rates such as:
#         1415/hr
#         15k/month

#     into:
#         numeric value
#         unit
#     """

#     if pd.isna(value):
#         return None, None

#     text = str(value).strip().lower()

#     if "/hr" in text:
#         number = text.replace("/hr", "").strip()

#         return float(number), "hourly"

#     if "/month" in text:
#         number = text.replace("/month", "").strip()

#         if number.endswith("k"):
#             number = float(number[:-1]) * 1000
#         else:
#             number = float(number)

#         return number, "monthly"

#     return None, None


# # ---------------------------------------------------------
# # Load raw data
# # ---------------------------------------------------------

# naukri = pd.read_csv(
#     DATA_DIR / "source1_naukri_applicants.csv"
# )

# gig = pd.read_csv(
#     DATA_DIR / "source2_gig_workers.csv"
# )

# cbnexus = pd.read_csv(
#     DATA_DIR / "source3_cbnexus_contacts.csv"
# )


# # ---------------------------------------------------------
# # Clean Gig Workers
# # ---------------------------------------------------------

# # Remove completely empty rows
# gig = gig.dropna(how="all").copy()


# # Remove the malformed Isha Chopra row.
# #
# # This row can be identified because the worker_name
# # column contains an email address instead of a name.

# malformed_mask = (
#     gig["worker_name"]
#     .astype(str)
#     .str.contains("@", na=False)
# )

# gig = gig[~malformed_mask].copy()


# # Normalize Gig Worker fields

# gig["name_normalized"] = gig["worker_name"].apply(
#     normalize_name
# )

# gig["email_normalized"] = gig["email_id"].apply(
#     normalize_email
# )

# gig["city_normalized"] = gig["location"].apply(
#     normalize_city
# )

# gig["status_normalized"] = gig["status"].apply(
#     normalize_status
# )


# # Parse rate

# gig[["rate_value", "rate_unit"]] = gig["rate"].apply(
#     lambda x: pd.Series(parse_rate(x))
# )


# # ---------------------------------------------------------
# # Clean Naukri
# # ---------------------------------------------------------

# naukri["name_normalized"] = naukri["Full Name"].apply(
#     normalize_name
# )

# naukri["email_normalized"] = naukri["Email"].apply(
#     normalize_email
# )

# naukri["phone_normalized"] = naukri["Phone"].apply(
#     normalize_phone
# )

# naukri["city_normalized"] = naukri["City"].apply(
#     normalize_city
# )


# # Remove exact duplicate person records.

# naukri = naukri.drop_duplicates(
#     subset=[
#         "name_normalized",
#         "phone_normalized"
#     ]
# ).copy()


# # ---------------------------------------------------------
# # Clean CBNexus
# # ---------------------------------------------------------

# cbnexus["name_normalized"] = cbnexus["Name"].apply(
#     normalize_name
# )

# cbnexus["phone_normalized"] = cbnexus["Phone Number"].apply(
#     normalize_phone
# )

# cbnexus["city_normalized"] = cbnexus["City"].apply(
#     normalize_city
# )

# cbnexus["verified_normalized"] = (
#     cbnexus["Verified"]
#     .astype(str)
#     .str.strip()
#     .str.lower()
#     .map({
#         "yes": True,
#         "y": True,
#         "no": False,
#         "n": False,
#     })
# )


# # ---------------------------------------------------------
# # Save cleaned files
# # ---------------------------------------------------------

# naukri.to_csv(
#     OUTPUT_DIR / "naukri_cleaned.csv",
#     index=False
# )

# gig.to_csv(
#     OUTPUT_DIR / "gig_workers_cleaned.csv",
#     index=False
# )

# cbnexus.to_csv(
#     OUTPUT_DIR / "cbnexus_cleaned.csv",
#     index=False
# )


# # ---------------------------------------------------------
# # Summary
# # ---------------------------------------------------------

# print("=" * 60)
# print("CLEANING COMPLETE")
# print("=" * 60)

# print(f"Naukri records: {len(naukri)}")
# print(f"Gig Worker records: {len(gig)}")
# print(f"CBNexus records: {len(cbnexus)}")

# print("\nCleaned files saved to:")
# print(OUTPUT_DIR)

import pandas as pd
import re
from pathlib import Path


DATA_DIR = Path("data")
OUTPUT_DIR = Path("data/cleaned")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# NORMALIZATION FUNCTIONS
# =========================================================

def normalize_name(value):
    if pd.isna(value):
        return ""

    value = str(value).strip().lower()
    value = re.sub(r"\s+", " ", value)

    return value


def normalize_email(value):
    if pd.isna(value):
        return ""

    return str(value).strip().lower()


def normalize_phone(value):
    if pd.isna(value):
        return ""

    digits = re.sub(r"\D", "", str(value))

    # Convert Indian numbers such as 919000000254
    # to the standard 10-digit format.
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]

    return digits


def normalize_city(value):
    if pd.isna(value):
        return ""

    city = str(value).strip().lower()

    city_aliases = {
        "bangalore": "bengaluru",
        "gurugram": "gurgaon",
        "new delhi": "delhi",
    }

    return city_aliases.get(city, city)


def normalize_status(value):
    if pd.isna(value):
        return ""

    return str(value).strip().lower()


def parse_rate(value):
    """
    Convert:
        1415/hr
        15k/month

    into:
        numeric value
        unit
    """

    if pd.isna(value):
        return None, None

    text = str(value).strip().lower()

    if "/hr" in text:
        number = text.replace("/hr", "").strip()

        try:
            return float(number), "hourly"
        except ValueError:
            return None, None

    if "/month" in text:
        number = text.replace("/month", "").strip()

        try:
            if number.endswith("k"):
                number = float(number[:-1]) * 1000
            else:
                number = float(number)

            return number, "monthly"

        except ValueError:
            return None, None

    return None, None


# =========================================================
# LOAD RAW DATA
# =========================================================

naukri = pd.read_csv(
    DATA_DIR / "source1_naukri_applicants.csv"
)

gig = pd.read_csv(
    DATA_DIR / "source2_gig_workers.csv"
)

cbnexus = pd.read_csv(
    DATA_DIR / "source3_cbnexus_contacts.csv"
)


# =========================================================
# CLEAN GIG WORKERS
# =========================================================

# Remove completely empty rows
gig = gig.dropna(how="all").copy()


# Remove malformed Isha Chopra row.
# The corrupted row has an email address inside worker_name.

malformed_mask = (
    gig["worker_name"]
    .astype(str)
    .str.contains("@", na=False)
)

gig = gig[~malformed_mask].copy()


# Normalize fields

gig["name_normalized"] = gig["worker_name"].apply(
    normalize_name
)

gig["email_normalized"] = gig["email_id"].apply(
    normalize_email
)

gig["city_normalized"] = gig["location"].apply(
    normalize_city
)

gig["status_normalized"] = gig["status"].apply(
    normalize_status
)


# Parse rates

gig[["rate_value", "rate_unit"]] = gig["rate"].apply(
    lambda x: pd.Series(parse_rate(x))
)


# =========================================================
# CLEAN NAUKRI
# =========================================================

naukri["name_normalized"] = naukri["Full Name"].apply(
    normalize_name
)

naukri["email_normalized"] = naukri["Email"].apply(
    normalize_email
)

naukri["phone_normalized"] = naukri["Phone"].apply(
    normalize_phone
)

naukri["city_normalized"] = naukri["City"].apply(
    normalize_city
)


# Remove exact duplicate Naukri records

naukri = naukri.drop_duplicates(
    subset=[
        "name_normalized",
        "phone_normalized"
    ]
).copy()


# =========================================================
# CLEAN CBNEXUS
# =========================================================

# IMPORTANT:
# Remove accidental duplicate header rows that appear
# inside the actual CBNexus data.

cbnexus = cbnexus[
    cbnexus["Projects Completed"]
    .astype(str)
    .str.strip()
    != "Projects Completed"
].copy()


cbnexus["name_normalized"] = cbnexus["Name"].apply(
    normalize_name
)

cbnexus["phone_normalized"] = cbnexus["Phone Number"].apply(
    normalize_phone
)

cbnexus["city_normalized"] = cbnexus["City"].apply(
    normalize_city
)


cbnexus["verified_normalized"] = (
    cbnexus["Verified"]
    .astype(str)
    .str.strip()
    .str.lower()
    .map({
        "yes": True,
        "y": True,
        "no": False,
        "n": False,
    })
)


# =========================================================
# SAVE CLEANED DATA
# =========================================================

naukri.to_csv(
    OUTPUT_DIR / "naukri_cleaned.csv",
    index=False
)

gig.to_csv(
    OUTPUT_DIR / "gig_workers_cleaned.csv",
    index=False
)

cbnexus.to_csv(
    OUTPUT_DIR / "cbnexus_cleaned.csv",
    index=False
)


# =========================================================
# SUMMARY
# =========================================================

print("=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)

print(f"Naukri records: {len(naukri)}")
print(f"Gig Worker records: {len(gig)}")
print(f"CBNexus records: {len(cbnexus)}")

print("\nCleaned files saved to:")
print(OUTPUT_DIR)