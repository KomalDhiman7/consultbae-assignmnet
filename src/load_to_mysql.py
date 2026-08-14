import os
import pandas as pd
import mysql.connector

from dotenv import load_dotenv
from pathlib import Path


load_dotenv()


DATA_DIR = Path("data/cleaned")


DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def find_person(cursor, email=None, phone=None):
    """
    Find an existing person using strong identifiers.

    Priority:
    1. Email
    2. Phone
    """

    if email:
        cursor.execute(
            """
            SELECT person_id
            FROM people
            WHERE email = %s
            LIMIT 1
            """,
            (email,)
        )

        result = cursor.fetchone()

        if result:
            return result[0]

    if phone:
        cursor.execute(
            """
            SELECT person_id
            FROM people
            WHERE phone = %s
            LIMIT 1
            """,
            (phone,)
        )

        result = cursor.fetchone()

        if result:
            return result[0]

    return None


def create_person(cursor, name, email=None, phone=None, city=None):
    """
    Create a new master person.
    """

    cursor.execute(
        """
        INSERT INTO people
        (name, email, phone, city)
        VALUES (%s, %s, %s, %s)
        """,
        (name, email, phone, city)
    )

    return cursor.lastrowid


def get_or_create_person(
    cursor,
    name,
    email=None,
    phone=None,
    city=None
):
    """
    Return an existing person_id or create a new person.
    """

    person_id = find_person(
        cursor,
        email=email,
        phone=phone
    )

    if person_id:
        return person_id

    return create_person(
        cursor,
        name=name,
        email=email,
        phone=phone,
        city=city
    )


def load_naukri(cursor, connection):
    """
    Load Naukri records.
    """

    df = pd.read_csv(
        DATA_DIR / "naukri_cleaned.csv"
    )

    count = 0

    for _, row in df.iterrows():

        person_id = get_or_create_person(
            cursor,
            name=row["Full Name"],
            email=row["email_normalized"],
            phone=row["phone_normalized"],
            city=row["city_normalized"]
        )

        cursor.execute(
            """
            INSERT INTO naukri_records
            (
                person_id,
                experience_years,
                current_ctc,
                applied_date,
                skills
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                person_id,
                row["Experience (Years)"],
                row["Current CTC"],
                row["Applied Date"],
                row["Skills"]
            )
        )

        cursor.execute(
            """
            INSERT INTO source_records
            (
                person_id,
                source,
                source_record_key
            )
            VALUES (%s, %s, %s)
            """,
            (
                person_id,
                "naukri",
                row["email_normalized"]
            )
        )

        count += 1

    connection.commit()

    print(f"Naukri records loaded: {count}")


def load_gig_workers(cursor, connection):
    """
    Load Gig Worker records.
    """

    df = pd.read_csv(
        DATA_DIR / "gig_workers_cleaned.csv"
    )

    count = 0

    for _, row in df.iterrows():

        person_id = get_or_create_person(
            cursor,
            name=row["worker_name"],
            email=row["email_normalized"],
            city=row["city_normalized"]
        )

        cursor.execute(
            """
            INSERT INTO gig_worker_records
            (
                person_id,
                rate_original,
                rate_value,
                rate_unit,
                status,
                skill_tags
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                person_id,
                row["rate"],
                row["rate_value"],
                row["rate_unit"],
                row["status_normalized"],
                row["skill_tags"]
            )
        )

        cursor.execute(
            """
            INSERT INTO source_records
            (
                person_id,
                source,
                source_record_key
            )
            VALUES (%s, %s, %s)
            """,
            (
                person_id,
                "gig_workers",
                row["email_normalized"]
            )
        )

        count += 1

    connection.commit()

    print(f"Gig Worker records loaded: {count}")


def load_cbnexus(cursor, connection):
    """
    Load CBNexus records.
    """

    df = pd.read_csv(
        DATA_DIR / "cbnexus_cleaned.csv"
    )

    count = 0

    for _, row in df.iterrows():

        person_id = get_or_create_person(
            cursor,
            name=row["Name"],
            phone=row["phone_normalized"],
            city=row["city_normalized"]
        )

        cursor.execute(
            """
            INSERT INTO cbnexus_records
            (
                person_id,
                verified,
                projects_completed
            )
            VALUES (%s, %s, %s)
            """,
            (
                person_id,
                row["verified_normalized"],
                row["Projects Completed"]
            )
        )

        cursor.execute(
            """
            INSERT INTO source_records
            (
                person_id,
                source,
                source_record_key
            )
            VALUES (%s, %s, %s)
            """,
            (
                person_id,
                "cbnexus",
                row["phone_normalized"]
            )
        )

        count += 1

    connection.commit()

    print(f"CBNexus records loaded: {count}")


def main():

    connection = get_connection()
    cursor = connection.cursor()

    try:

        load_naukri(cursor, connection)
        load_gig_workers(cursor, connection)
        load_cbnexus(cursor, connection)

        print("\nAll data loaded successfully.")

    except Exception as error:

        connection.rollback()

        print("\nERROR:")
        print(error)

        raise

    finally:

        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()