import pandas as pd
from pathlib import Path


DATA_DIR = Path("data/cleaned")


# ---------------------------------------------------------
# Load cleaned data
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
# Master registry
# ---------------------------------------------------------

people = []


def find_person(email="", phone="", name="", city=""):
    """
    Find an existing master person.

    Priority:
    1. Exact normalized email
    2. Exact normalized phone
    3. Name + city
    """

    for person in people:

        # Strong match: email
        if email and person["email"] == email:
            return person

        # Strong match: phone
        if phone and person["phone"] == phone:
            return person

    # We deliberately do NOT automatically merge
    # based only on name + city yet.

    return None


def create_person(name, email="", phone="", city=""):

    person = {
        "person_id": f"P{len(people) + 1:05d}",
        "name": name,
        "email": email,
        "phone": phone,
        "city": city,
        "sources": set(),
    }

    people.append(person)

    return person


# ---------------------------------------------------------
# Process Naukri
# ---------------------------------------------------------

for _, row in naukri.iterrows():

    person = find_person(
        email=row["email_normalized"],
        phone=row["phone_normalized"],
    )

    if person is None:

        person = create_person(
            name=row["Full Name"],
            email=row["email_normalized"],
            phone=row["phone_normalized"],
            city=row["city_normalized"],
        )

    person["sources"].add("naukri")


# ---------------------------------------------------------
# Process Gig Workers
# ---------------------------------------------------------

for _, row in gig.iterrows():

    person = find_person(
        email=row["email_normalized"],
        name=row["name_normalized"],
        city=row["city_normalized"],
    )

    if person is None:

        person = create_person(
            name=row["worker_name"],
            email=row["email_normalized"],
            city=row["city_normalized"],
        )

    person["sources"].add("gig")


# ---------------------------------------------------------
# Process CBNexus
# ---------------------------------------------------------

for _, row in cbnexus.iterrows():

    person = find_person(
        phone=row["phone_normalized"],
    )

    if person is None:

        person = create_person(
            name=row["Name"],
            phone=row["phone_normalized"],
            city=row["city_normalized"],
        )

    person["sources"].add("cbnexus")


# ---------------------------------------------------------
# Convert to DataFrame
# ---------------------------------------------------------

master = pd.DataFrame(people)

master["sources"] = master["sources"].apply(
    lambda x: ", ".join(sorted(x))
)


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

output_path = DATA_DIR / "master_people.csv"

master.to_csv(
    output_path,
    index=False
)


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

print("=" * 70)
print("MASTER PERSON REGISTRY")
print("=" * 70)

print(f"Total master people: {len(master)}")

print("\nPeople by source combination:")

print(
    master["sources"]
    .value_counts()
    .to_string()
)

print("\nSample master records:")

print(
    master.head(20).to_string(index=False)
)

print(
    f"\nSaved to: {output_path}"
)