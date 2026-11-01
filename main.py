"""Run: python main.py examples/valid_student.json"""
import argparse
import json
import sys
from pathlib import Path
from pydantic import ValidationError
from models import Student


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a student JSON record.")
    parser.add_argument("input", type=Path, help="Path to the input JSON file")
    parser.add_argument("-o", "--output", type=Path, default=Path("validated_student.json"))
    args = parser.parse_args(argv)

    if args.input.resolve() == args.output.resolve():
        print("Error: input and output paths must differ.", file=sys.stderr)
        return 1
    try:
        student = Student.model_validate_json(args.input.read_text(encoding="utf-8"))
    except ValidationError as exc:
        print("Validation failed:", file=sys.stderr)
        for error in exc.errors():
            location = ".".join(str(part) for part in error["loc"]) or "record"
            print(f"  {location}: {error['msg']}", file=sys.stderr)
        return 1
    except (OSError, UnicodeError) as exc:
        print(f"Cannot read input: {exc}", file=sys.stderr)
        return 1

    # Computed fields are included in exports; input files contain raw fields only.
    try:
        with args.output.open("x", encoding="utf-8") as output:
            output.write(student.model_dump_json(indent=2) + "\n")
    except FileExistsError:
        print("Output already exists. Choose a new path with --output.", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Cannot save output: {exc}", file=sys.stderr)
        return 1

    print(f"Student: {student.name}\nCourses validated: {len(student.courses)}")
    print(f"Average marks: {student.average_marks}\nResult: {student.result}")
    print(f"Saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
