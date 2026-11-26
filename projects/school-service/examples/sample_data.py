"""Print a valid example teacher payload as JSON."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from school_service.services import sample_teacher


if __name__ == "__main__":
    print(json.dumps(sample_teacher(1), indent=2))
