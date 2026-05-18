"""CAD Test Configuration"""

import sys
from pathlib import Path

# Add cad-model-pool path for editable install
pool_path = Path(__file__).parent / "cad-model-pool"
if str(pool_path) not in sys.path:
    sys.path.insert(0, str(pool_path))
