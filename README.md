# AI Title Analyzer

A web application that analyzes search engine titles and generates optimized title suggestions using AI (GPT-4 and Claude).

## Screenshot
![AI Title Analyzer Screenshot](images/screenshot.png)

## Features

- Scrapes Google search results for any given keyword
- Analyzes common terms and patterns in existing titles
- Generates optimized title suggestions using GPT-4 and Claude
- Adjustable AI temperature for creativity control
- Customizable AI instructions
- Modern, responsive UI

## Requirements

- Python 3.8+
- OpenAI API key
- Anthropic API key
- Chrome/Chromium for web scraping

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jefflouella/ai-title-analyzer.git
cd ai-title-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your API keys:
```
OPENAI_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. Enter a keyword and adjust the AI temperature as needed

4. Click "Analyze" to generate optimized titles

## License

MIT License 