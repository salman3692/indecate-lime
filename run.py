import os
import app  # imports your existing app.py

# Heroku gives the port in the environment variable PORT
port = int(os.environ.get("PORT", 8050))

# Dash app object is `app.app` in your script
app.app.run(host="0.0.0.0", port=port, debug=False)
