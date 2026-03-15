# backend\run.py

import os

from backend.app import create_app

app = create_app()

PORT = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run(port=PORT, debug=False, use_reloader=False)
