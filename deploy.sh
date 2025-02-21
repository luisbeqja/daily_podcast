#!/bin/bash

# Ensure all requirements are installed
pip install -r requirements.txt

# Run database migrations if any
python -c "from telegram_api.database import Database; db = Database(); db.init_db()"

# Start the application
gunicorn app:app 