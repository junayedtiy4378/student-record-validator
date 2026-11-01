import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from pydantic import ValidationError
from models import Student
from main import main


def record():
    return {
        "name": " Junaed ", "student_id": "S101",
        "credits_completed": 90, "credits_required": 120,
        "courses": [{"name": " Networks ", "marks": "78"}, {"name": "SWE", "marks": 85}],
    }


class RecordTests(unittest.TestCase):
    def test_normalization_conversion_and_export(self):
        student = Student.model_validate(record())
        self.assertEqual(student.name, "Junaed")
        self.assertEqual(student.courses[0].name, "Networks")
        self.assertEqual(student.courses[0].marks, 78.0)
        self.assertEqual(student.average_marks, 81.5)
        self.assertEqual(json.loads(student.model_dump_json())["result"], "PASS")

    def test_invalid_marks(self):
        for marks in [-1, 101, "invalid", float("nan"), float("inf")]:
            with self.subTest(marks=marks):
                data = record()
                data["courses"][0]["marks"] = marks
                with self.assertRaises(ValidationError):
                    Student.model_validate(data)

    def test_duplicates(self):
        data = record()
        data["courses"].append({"name": "networks", "marks": 50})
        with self.assertRaises(ValidationError):
            Student.model_validate(data)

    def test_credits(self):
        data = record()
        data["credits_completed"] = 121
        with self.assertRaises(ValidationError):
            Student.model_validate(data)

    def test_required_and_unknown_fields(self):
        for change in ["blank", "empty_courses", "unknown", "bad_id"]:
            data = record()
            if change == "blank":
                data["name"] = " "
            elif change == "empty_courses":
                data["courses"] = []
            elif change == "unknown":
                data["typo"] = 1
            else:
                data["student_id"] = "101"
            with self.subTest(change=change), self.assertRaises(ValidationError):
                Student.model_validate(data)

    def test_pass_boundary(self):
        data = record()
        data["courses"] = [{"name": "SWE", "marks": 40}]
        self.assertEqual(Student.model_validate(data).result, "PASS")
        data["courses"][0]["marks"] = 39.9
        self.assertEqual(Student.model_validate(data).result, "FAIL")

    def test_cli_success_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            output = Path(directory) / "output.json"
            source.write_text(json.dumps(record()), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main([str(source), "-o", str(output)]), 0)
                original = output.read_bytes()
                self.assertEqual(main([str(source), "-o", str(output)]), 1)
                self.assertEqual(main([str(source), "-o", str(source)]), 1)
            self.assertEqual(output.read_bytes(), original)

    def test_cli_invalid_and_missing_input(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "bad.json"
            output = Path(directory) / "output.json"
            for content in ["{", "{}"]:
                source.write_text(content, encoding="utf-8")
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(main([str(source), "-o", str(output)]), 1)
                self.assertFalse(output.exists())
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main([str(source.with_name("missing.json"))]), 1)


if __name__ == "__main__":
    unittest.main()
