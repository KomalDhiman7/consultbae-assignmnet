# ConsultBae AI Automation Assignment

## Overview

This project implements the ConsultBae AI Automation take-home assignment.

The solution covers:

1. Data cleaning and normalization
2. Entity matching across Naukri, Gig Workers, and CBNexus data
3. MySQL database creation and loading
4. n8n duplicate candidate checking automation
5. Flask-based audio collection application
6. Audio metadata extraction and submission listing

---

# 1. Project Structure

```text
consultbae-assignment/
├── data/
│   ├── source1_naukri_applicants.csv
│   ├── source2_gig_workers.csv
│   ├── source3_cbnexus_contacts.csv
│   └── cleaned/
├── src/
│   ├── inspect_data.py
│   ├── clean_data.py
│   ├── match_people.py
│   ├── build_master.py
│   ├── load_to_mysql.py
│   └── profile_data.py
├── n8n/
│   └── Candidate Duplicate Checker.json
├── audio_app/
│   ├── app.py
│   ├── templates/
│   │   ├── index.html
│   │   └── submissions.html
│   └── uploads/
├── requirements.txt
└── README.md
