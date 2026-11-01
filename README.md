# Student Record Validator

A beginner-friendly Python command-line project using Pydantic v2 to validate student JSON records, compute results, and export structured data. No API key, database, web server, or paid service is required.

## Setup (Python 3.11 or newer)

Extract the ZIP, open a terminal in this folder, then run:

Windows:
```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py examples/valid_student.json
```

macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py examples/valid_student.json
```

Expected output:
```text
Student: Junaed Ahmed
Courses validated: 2
Average marks: 81.5
Result: PASS
Saved to validated_student.json
```

Use a different output name for subsequent runs:
```bash
python main.py examples/valid_student.json --output another_result.json
python main.py examples/invalid_student.json
python -m unittest discover -s tests -v
```

Validation failures return exit code 1 and explain the field errors. Successful exports return 0. Existing output files and the original input are protected from overwrite. Output parent directories must already exist.

## Workflow

The CLI reads one student record, validates it with Pydantic, and exports a report when all checks pass.

```mermaid
flowchart TD
    A["Run CLI with input and output paths"] --> B{"Paths differ?"}
    B -->|No| E["Print error and exit with code 1"]
    B -->|Yes| C["Read input JSON"]
    C -->|Read or encoding error| E
    C --> D["Validate Student and nested Course models"]
    D -->|Invalid JSON or validation failure| E
    D -->|Valid record| F["Compute average marks and pass or fail"]
    F --> G["Serialize and create output JSON"]
    G -->|Output exists or write fails| E
    G -->|Saved| H["Print summary and exit with code 0"]
```

Validation checks field types, required values, marks, unique course names, and credit limits. The original input and any existing output file are protected from overwrite.

## Rules

- Name and course names must contain non-whitespace text; surrounding whitespace is trimmed.
- Student IDs use S followed by digits, e.g. S101.
- At least one course is required; course names must be unique ignoring case.
- Marks must be finite numbers between 0 and 100 inclusive. Numeric strings such as "78" are converted.
- Credits are strict integers; required credits must be positive; completed credits cannot exceed required credits.
- Unknown fields are rejected to catch misspelled keys.
- The average is an unweighted arithmetic mean, rounded to two decimal places.
- PASS requires at least 40 in every course. This is a demonstration rule, not BRAC University's grading policy.

The exported JSON includes computed fields (`average_marks` and `result`). It is a report, not a raw input record. Remove those two fields if you want to validate an exported report as new input.

## What you learn

| Feature | Implementation |
| --- | --- |
| BaseModel and Field | Student/Course schemas, ranges and ID pattern |
| Field validators | Trim text and reject duplicate courses |
| Model validator | Compare completed and required credits |
| Computed fields | Average marks and overall result |
| Nested models | A student's list of Course objects |
| Serialization | model_dump_json() exports |
| Error handling | ValidationError and readable CLI errors |
| Tests and CI | unittest suite and GitHub Actions |

## Files

- `models.py`: data models and business validation.
- `main.py`: CLI input, output, and error handling.
- `examples/`: valid and invalid inputs.
- `tests/`: validation and CLI tests.
- `.github/workflows/tests.yml`: runs tests on pushes and pull requests.

## Push to GitHub

Create an empty repository named `student-record-validator` under [junayedtiy4378](https://github.com/junayedtiy4378) on GitHub. Leave README, license, and .gitignore unchecked, then run these commands from this project folder.

```bash
git config --global user.name "Junaed Ahmed"
git config --global user.email "junayedtiy437@gmail.com"
git init
git add .
git commit -m "Build student record validator with Pydantic"
git branch -M main
git remote add origin https://github.com/junayedtiy4378/student-record-validator.git
git push -u origin main
```

If `origin` already exists, update it instead:

```bash
git remote set-url origin https://github.com/junayedtiy4378/student-record-validator.git
git push -u origin main
```

## Possible extensions

Add batch processing, CSV export, or a FastAPI endpoint after understanding the current validation flow.
