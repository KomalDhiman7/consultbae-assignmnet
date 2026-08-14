import pandas as pd
from pathlib import Path


DATA_DIR = Path("data/cleaned")


# ---------------------------------------------------------
# Load cleaned datasets
# ---------------------------------------------------------

naukri = pd.read_csv(
    DATA_DIR / "naukri_cleaned.csv"
)

gig = pd.read_csv(
    DATA_DIR / "gig_workers_cleaned.csv"
)

cbnexus = pd.read_csv(
    DATA_DIR / "cbnexus_cleaned.csv"
)


# ---------------------------------------------------------
# 1. Naukri ↔ CBNexus
# Strong match: normalized phone
# ---------------------------------------------------------

phone_matches = naukri.merge(
    cbnexus,
    on="phone_normalized",
    how="inner",
    suffixes=("_naukri", "_cbnexus")
)


print("=" * 70)
print("NAUKRI ↔ CBNEXUS PHONE MATCHES")
print("=" * 70)

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

print(
    f"\nTotal strong phone matches: {len(phone_matches)}"
)


# ---------------------------------------------------------
# 2. Same name but different phone
# ---------------------------------------------------------

name_matches = naukri.merge(
    cbnexus,
    on="name_normalized",
    how="inner",
    suffixes=("_naukri", "_cbnexus")
)


name_conflicts = name_matches[
    name_matches["phone_normalized_naukri"]
    != name_matches["phone_normalized_cbnexus"]
]


print("\n" + "=" * 70)
print("SAME NAME BUT DIFFERENT PHONE")
print("=" * 70)


if len(name_conflicts) > 0:

    print(
        name_conflicts[
            [
                "Full Name",
                "Phone",
                "Name",
                "Phone Number"
            ]
        ].to_string(index=False)
    )

else:

    print("No conflicts found.")


print(
    f"\nPotential name conflicts: {len(name_conflicts)}"
)


# ---------------------------------------------------------
# 3. Naukri ↔ Gig Workers
# Strong match: normalized email
# ---------------------------------------------------------

email_matches = naukri.merge(
    gig,
    on="email_normalized",
    how="inner",
    suffixes=("_naukri", "_gig")
)


print("\n" + "=" * 70)
print("NAUKRI ↔ GIG WORKERS EMAIL MATCHES")
print("=" * 70)


if len(email_matches) > 0:

    print(
        email_matches[
            [
                "Full Name",
                "Email",
                "worker_name",
                "email_id"
            ]
        ].to_string(index=False)
    )

else:

    print("No email matches found.")


print(
    f"\nTotal email matches: {len(email_matches)}"
)


# ---------------------------------------------------------
# 4. Naukri ↔ Gig Workers
# Same normalized name
# ---------------------------------------------------------

name_gig_matches = naukri.merge(
    gig,
    on="name_normalized",
    how="inner",
    suffixes=("_naukri", "_gig")
)


print("\n" + "=" * 70)
print("NAUKRI ↔ GIG WORKERS SAME NAME")
print("=" * 70)


if len(name_gig_matches) > 0:

    print(
        name_gig_matches[
            [
                "Full Name",
                "Email",
                "worker_name",
                "email_id",
                "city_normalized_naukri",
                "city_normalized_gig"
            ]
        ].to_string(index=False)
    )

else:

    print("No same-name matches found.")


print(
    f"\nTotal same-name matches: {len(name_gig_matches)}"
)