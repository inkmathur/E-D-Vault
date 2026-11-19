
import sys
from pathlib import Path

# Add the main E/D Vault project directory to Python's search path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from encryption.encrypt import encrypt_file


def test_existing_output_is_not_overwritten():
    source = PROJECT_ROOT / "sample_files" / "sample.txt"
    output = PROJECT_ROOT / "sample_files" / "overwrite_test.edv"

    if not source.exists():
        print("ERROR: sample.txt does not exist.")
        return

    try:
        output.write_text("KEEP THIS FILE", encoding="utf-8")

        try:
            encrypt_file(
                source,
                "TestPassword123!",
                output
            )

            print("FAILED: Existing file was overwritten.")

        except FileExistsError:
            print("SUCCESS: Existing output was protected.")

        content = output.read_text(encoding="utf-8")

        if content == "KEEP THIS FILE":
            print("SUCCESS: Original contents are unchanged.")
        else:
            print("FAILED: Original contents changed.")

    finally:
        if output.exists():
            output.unlink()


if __name__ == "__main__":
    test_existing_output_is_not_overwritten()
