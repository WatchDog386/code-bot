"""Print a valid example doctor payload as JSON."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clinic_service.services import sample_doctor


if __name__ == "__main__":
    print(json.dumps(sample_doctor(1), indent=2))
