# Podcast Generator Bot

A Telegram bot that generates podcasts using OpenAI's GPT and Text-to-Speech APIs.

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your credentials:
   ```
   TELEGRAM_BOT_TOKEN=your_token
   OPENAI_API_KEY=your_key
   GEMINI_API_KEY=your_key
   ```
5. Run the application:
   ```bash
   python app.py
   ```

## Features

- Generate podcasts from user topics
- Multiple language support (English, Spanish, Italian)
- User-specific podcast storage
- Episode tracking and management

## Deployment

The application is ready for deployment on platforms like Heroku:

1. Create a new Heroku app
2. Set environment variables in Heroku dashboard
3. Deploy using Git:
   ```bash
   git push heroku main
   ```

## Project Structure

- `/llm` - AI and audio generation logic
- `/telegram_api` - Telegram bot implementation
- `app.py` - Flask web application
- `config.py` - Configuration management 