import os
import re

def load_language_prompts():
    """Load language prompts from markdown file."""
    prompts = {}
    with open(os.path.join(os.path.dirname(__file__), 'language_prompts.md'), 'r') as f:
        content = f.read()
        
    # Parse language sections using regex
    sections = re.findall(r'## (\w+) \((.*?)\)\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    for language_name, code, prompt in sections:
        prompts[code.strip()] = prompt.strip()
    
    return prompts

def load_prompt(filename):
    """Load a prompt from a markdown file."""
    with open(os.path.join(os.path.dirname(__file__), filename), 'r') as f:
        content = f.read()
        # Remove the title (first line) and any extra whitespace
        prompt = '\n'.join(line for line in content.split('\n')[2:] if line.strip())
    return prompt

# Load all prompts at module level
LANGUAGE_PROMPTS = load_language_prompts()
EPISODE_LINEUP_PROMPT = load_prompt('episode_lineup_prompt.md')
FIRST_EPISODE_PROMPT = load_prompt('first_episode_prompt.md')
EPISODE_PROMPT = load_prompt('episode_prompt.md') 