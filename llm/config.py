# Set up logging
import logging
import os
import openai


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("🔌 Connected to OpenAI API", os.getenv('OPENAI_API_KEY'))

# Configure OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def test_openai_api():
    chat_completion = openai.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            }
        ],
        model="gpt-4o",
    )
    
    print(chat_completion.choices[0].message.content)

test_openai_api()