from flask import Flask, render_template, request, jsonify
from title_analyzer import TitleAnalyzer
import os
from dotenv import load_dotenv

# Load environment variables
print("\nLoading environment variables...")
load_dotenv()

app = Flask(__name__)

# Get API keys from environment variables
openai_key = os.getenv('OPENAI_API_KEY')
anthropic_key = os.getenv('ANTHROPIC_API_KEY')

print("\n=== Environment Variables ===")
print(f"OPENAI_API_KEY: {'Present (length: ' + str(len(openai_key)) + ')' if openai_key else 'Not found'}")
print(f"ANTHROPIC_API_KEY: {'Present (length: ' + str(len(anthropic_key)) + ')' if anthropic_key else 'Not found'}")

print("\n=== API Key Status ===")
print(f"OpenAI API Key present: {'Yes' if openai_key else 'No'}")
print(f"Anthropic API Key present: {'Yes' if anthropic_key else 'No'}")

if not openai_key and not anthropic_key:
    print("Error: Neither OPENAI_KEY nor ANTHROPIC_API_KEY found. Please set at least one API key in your .env file")
    exit(1)

# Initialize analyzer with available keys
analyzer = TitleAnalyzer(openai_key, anthropic_key)

# Print available services
print("\nAvailable AI Services:")
if openai_key:
    print("✓ GPT-4")
if anthropic_key:
    print("✓ Claude")
print()

def load_instructions():
    try:
        with open('current_instructions.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        try:
            with open('default_instructions.txt', 'r') as f:
                return f.read()
        except FileNotFoundError:
            return """Create a unique and engaging title tag (max 75 characters) that:
1. Incorporates 2-3 of the most relevant common terms
2. Adds a unique angle or perspective
3. Maintains search intent
4. Includes the main keyword naturally
5. Avoid using dates and/or years"""

def save_instructions(instructions):
    with open('current_instructions.txt', 'w') as f:
        f.write(instructions)

@app.route('/')
def index():
    instructions = load_instructions()
    return render_template('index.html', instructions=instructions)

@app.route('/analyze', methods=['POST'])
def analyze():
    print("\n=== New Analysis Request ===")
    keyword = request.form.get('keyword', '')
    temperature = float(request.form.get('temperature', 0.4))
    instructions = request.form.get('instructions', '')
    
    print(f"Keyword: {keyword}")
    print(f"Temperature: {temperature}")
    
    # Save instructions if they differ from default
    try:
        with open('default_instructions.txt', 'r') as f:
            default_instructions = f.read()
            if instructions != default_instructions:
                save_instructions(instructions)
    except FileNotFoundError:
        save_instructions(instructions)
    
    results = analyzer.run_analysis(keyword, temperature, instructions)
    
    # Debug print results
    print("\nResults received:")
    print(f"GPT-4 Title: {'Available' if 'gpt4_title' in results else 'Not available'}")
    print(f"Claude Title: {'Available' if 'claude_title' in results else 'Not available'}")
    
    # Only include available AI results
    response = {
        "keyword": results["keyword"],
        "num_titles_analyzed": results["num_titles_analyzed"],
        "top_terms": results["top_terms"],
        "term_frequency": results["term_frequency"],
        "analyzed_titles": results["analyzed_titles"]
    }
    
    if results["gpt4_title"] != "OpenAI API key not provided":
        response["gpt4_title"] = results["gpt4_title"]
    
    if results["claude_title"] != "Anthropic API key not provided":
        response["claude_title"] = results["claude_title"]
    
    return jsonify(response)

@app.route('/reset-instructions', methods=['POST'])
def reset_instructions():
    try:
        with open('default_instructions.txt', 'r') as f:
            default_instructions = f.read()
            return jsonify({"instructions": default_instructions})
    except FileNotFoundError:
        return jsonify({"error": "Default instructions file not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001) 