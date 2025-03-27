from flask import Flask, render_template, request, jsonify
from title_analyzer import TitleAnalyzer
import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize the analyzer
openai_key = os.getenv('OPENAI_KEY')
anthropic_key = os.getenv('ANTHROPIC_API_KEY')

if not openai_key or not anthropic_key:
    raise ValueError("OPENAI_KEY or ANTHROPIC_API_KEY not found in environment variables")

analyzer = TitleAnalyzer(openai_key, anthropic_key)

def load_instructions():
    try:
        with open('default_instructions.txt', 'r') as f:
            return f.read()
    except:
        return ""

def save_instructions(instructions):
    with open('current_instructions.txt', 'w') as f:
        f.write(instructions)

def reset_instructions():
    if os.path.exists('current_instructions.txt'):
        os.remove('current_instructions.txt')

@app.route('/')
def index():
    # Try to load current instructions, fall back to default if not found
    try:
        with open('current_instructions.txt', 'r') as f:
            current_instructions = f.read()
    except:
        current_instructions = load_instructions()
    
    return render_template('index.html', instructions=current_instructions)

@app.route('/analyze', methods=['POST'])
def analyze():
    keyword = request.form['keyword']
    temperature = float(request.form['temperature'])
    instructions = request.form.get('instructions', load_instructions())
    
    try:
        # Save the current instructions if they differ from default
        if instructions != load_instructions():
            save_instructions(instructions)
        
        # Run the complete analysis using the analyzer instance
        results = analyzer.run_analysis(keyword, temperature, instructions)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reset-instructions', methods=['POST'])
def reset():
    reset_instructions()
    return jsonify({'instructions': load_instructions()})

if __name__ == '__main__':
    # Run the app on all available network interfaces
    app.run(host='0.0.0.0', port=8080, debug=True) 