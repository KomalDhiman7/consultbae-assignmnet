import os
import math
import uuid

import librosa
import mysql.connector

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = "audio_app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def find_person(phone):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT person_id, name, phone
        FROM people
        WHERE phone = %s
        LIMIT 1
        """,
        (phone,)
    )

    person = cursor.fetchone()

    cursor.close()
    connection.close()

    return person


def calculate_audio_metadata(filepath):

    audio, sample_rate = librosa.load(
        filepath,
        sr=None,
        mono=False
    )

    duration = librosa.get_duration(
        y=audio,
        sr=sample_rate
    )

    if audio.ndim > 1:
        channels = audio.shape[0]
    else:
        channels = 1

    bitrate_kbps = (
        sample_rate * channels * 16
    ) / 1000

    rms = librosa.feature.rms(y=audio)

    rms_value = rms.mean()

    if rms_value > 0:
        loudness_db = 20 * math.log10(rms_value)
    else:
        loudness_db = -100.0

    return (
        duration,
        sample_rate / 1000,
        bitrate_kbps,
        loudness_db
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():

    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    audio_file = request.files.get("audio")

    if not name or not phone or not audio_file:
        return "Name, phone and audio file are required.", 400

    original_filename = secure_filename(
        audio_file.filename
    )

    extension = os.path.splitext(
        original_filename
    )[1].lower()

    filename = uuid.uuid4().hex + extension

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    audio_file.save(filepath)

    try:

        (
            duration,
            sample_rate_khz,
            bitrate_kbps,
            loudness_db
        ) = calculate_audio_metadata(filepath)

    except Exception as error:

        if os.path.exists(filepath):
            os.remove(filepath)

        return f"Could not process audio: {error}", 400

    person = find_person(phone)

    person_id = person["person_id"] if person else None

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO audio_submissions
        (
            person_id,
            name,
            phone,
            audio_filename,
            duration_seconds,
            sample_rate_khz,
            bitrate_kbps,
            loudness_db
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            person_id,
            name,
            phone,
            filename,
            duration,
            sample_rate_khz,
            bitrate_kbps,
            loudness_db
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("submissions"))


@app.route("/audio/<filename>")
def audio(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


@app.route("/submissions")
def submissions():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            submission_id,
            name,
            phone,
            audio_filename,
            duration_seconds,
            sample_rate_khz,
            bitrate_kbps,
            loudness_db,
            created_at
        FROM audio_submissions
        ORDER BY created_at DESC
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "submissions.html",
        submissions=rows
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )