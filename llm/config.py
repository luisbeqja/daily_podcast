# Set up logging
import logging
import os

import openai


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')