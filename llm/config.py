# Set up logging
import logging
import os
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get API key from environment
api_key = os.getenv('OPENAI_API_KEY')
print(f"🔌 Connected to OpenAI API {api_key[:20]}..." if api_key else "❌ No OpenAI API key found")

# Configure OpenAI client
openai = OpenAI(api_key=api_key)

def test_openai_api():
    try:
        chat_completion = openai.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-4o",
        )
        
        print("✅ OpenAI API test successful:", chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        raise

# Only test the API if this module is being imported (not in production)
if not os.getenv('RAILWAY_ENVIRONMENT'):
    test_openai_api()