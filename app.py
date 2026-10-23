"""Default entry point for the account-enabled Health Focus application.

The previous standalone implementation is preserved in app_legacy.py.
"""

import importlib.util
import os
import sys
from pathlib import Path

APPLICATION_DIR = Path(__file__).resolve().parent / "CNNT-KLCN180"
APPLICATION_FILE = APPLICATION_DIR / "app.py"
sys.path.insert(0, str(APPLICATION_DIR))

spec = importlib.util.spec_from_file_location("health_focus_application", APPLICATION_FILE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load application from {APPLICATION_FILE}")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
app = module.app

if __name__ == "__main__":
    app.run(
        debug=os.environ.get("FLASK_DEBUG") == "1",
        use_reloader=False,
        host="127.0.0.1",
        port=5000,
    )
