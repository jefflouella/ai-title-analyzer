# AI Title Analyzer

A Python tool that analyzes Google search results and generates optimized title tags using AI (GPT-4 and/or Claude).

## Screenshot
![AI Title Analyzer Screenshot](images/screenshot.png)

## Features

- Scrapes Google search results for your target keyword
- Analyzes common terms and patterns in top-ranking titles
- Generates optimized title suggestions using GPT-4 and/or Claude
- Handles Google's bot detection gracefully with manual captcha solving
- Persists cookies to minimize captcha challenges
- Filters out non-relevant titles (ads, widgets, etc.)
- Customizable AI temperature for title generation
- Modifiable AI instructions for custom title requirements
- Works with either or both AI services (GPT-4, Claude)

## Requirements

- Python 3.8+
- Chrome browser installed
- At least one API key (OpenAI or Anthropic)
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-title-analyzer.git
cd ai-title-analyzer
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your API key(s):
```
OPENAI_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

Note: You only need to provide one API key, but can use both for comparison.

## Usage

1. Run the script:
```bash
python app.py
```

2. Enter your target keyword when prompted.

3. If a captcha appears:
   - A Chrome window will open automatically
   - Solve the captcha manually
   - Press Enter in the terminal to continue
   - The cookies will be saved for future sessions to minimize captcha challenges

4. The tool will:
   - Scrape and analyze Google search results
   - Filter out non-relevant titles
   - Show common terms and patterns
   - Generate optimized title suggestions using available AI services

## Configuration

### AI Temperature
- Adjust the creativity level of AI-generated titles
- Range: 0.0 (more focused) to 1.0 (more creative)
- Default: 0.4

### AI Instructions
- Customize how titles are generated
- Modify the instructions in the UI
- Reset to default if needed

### Cookie Persistence
- Cookies are saved in `browser_data/google_cookies.json`
- Helps reduce captcha frequency
- Automatically managed by the tool

## Troubleshooting

### Captcha Issues
- If you see a captcha, a Chrome window will open automatically
- Solve the captcha manually
- Cookies will be saved to reduce future captchas
- Delete `browser_data/google_cookies.json` if you want to reset cookies

### No Results
- Check your internet connection
- Verify API keys are correct in `.env`
- Try solving a new captcha
- Ensure Chrome browser is installed

## Notes

- The tool respects Google's terms of service by:
  - Using human verification for captchas
  - Implementing reasonable delays between requests
  - Not making excessive automated queries

- For best results:
  - Use specific, focused keywords
  - Solve captchas when prompted
  - Allow cookie persistence
  - Adjust AI temperature based on needs

## License

MIT License - See LICENSE file for details 