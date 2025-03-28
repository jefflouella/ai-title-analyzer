import json
from collections import Counter
import nltk
import ssl
import certifi
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import openai
from anthropic import Anthropic
from typing import List, Dict, Tuple
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from urllib.parse import urlparse
import random

# Load environment variables
load_dotenv()

# Fix SSL certificate issues
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Set up NLTK data path
nltk_data_dir = os.path.expanduser('~/nltk_data')
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir)

# Download NLTK data with SSL verification
def download_nltk_data():
    resources = [
        'punkt',
        'stopwords',
        'punkt_tab',
        'tokenizers/punkt'
    ]
    
    for resource in resources:
        try:
            nltk.data.find(resource)
        except LookupError:
            print(f"Downloading {resource}...")
            nltk.download(resource, quiet=True)

# Download all required NLTK data
download_nltk_data()

class TitleAnalyzer:
    def __init__(self, openai_key: str = None, anthropic_key: str = None):
        """Initialize the TitleAnalyzer with available API keys."""
        self.openai_key = openai_key
        self.anthropic_key = anthropic_key
        self.stop_words = set(stopwords.words('english'))
        # Add custom stop words relevant for titles
        self.stop_words.update(['|', '-', '2025', '2024', '2023', 'best', 'top', 'guide'])
        
        # Initialize API clients only if keys are provided
        self.openai_client = None
        self.anthropic_client = None
        
        print("\nInitializing API clients:")
        if self.openai_key:
            print("- Setting up OpenAI client")
            self.openai_client = openai.OpenAI(api_key=self.openai_key)
        else:
            print("- OpenAI client not initialized (no API key)")
        
        if self.anthropic_key:
            print("- Setting up Anthropic client")
            self.anthropic_client = Anthropic(api_key=self.anthropic_key)
        else:
            print("- Anthropic client not initialized (no API key)")
        
        # Set up Chrome options
        self.chrome_options = Options()
        # Configure headless mode with new syntax
        self.chrome_options.add_argument('--headless=new')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_argument('--disable-infobars')
        self.chrome_options.add_argument('--disable-notifications')
        self.chrome_options.add_argument('--disable-popup-blocking')
        self.chrome_options.add_argument('--start-maximized')
        
        # Add a realistic user agent
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
        
        # Add additional headers to look more like a real browser
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Add additional preferences
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.images": 1,
            "profile.default_content_setting_values.cookies": 1
        }
        self.chrome_options.add_experimental_option("prefs", prefs)

    def get_search_results(self, keyword: str, num_results: int = 100) -> List[str]:
        """Fetch search results by scraping Google."""
        print(f"Scraping Google results for: {keyword}")
        
        # Initialize the Chrome WebDriver
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.chrome_options)
            
            # Set page load timeout
            driver.set_page_load_timeout(30)
            
            # Add more realistic browser headers
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                "platform": "MacIntel",
                "acceptLanguage": "en-US,en;q=0.9",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1"
            })
            
            # Add random delay between 3-5 seconds to look more human-like
            time.sleep(random.uniform(3, 5))
            
            # Navigate directly to Google search with num parameter and additional parameters
            # Replace spaces with plus signs in the keyword
            formatted_keyword = keyword.replace(' ', '+')
            search_url = f'https://www.google.com/search?q={formatted_keyword}&num={num_results}&hl=en&safe=off&gl=US&pws=0&sourceid=chrome&ie=UTF-8&oe=UTF-8'
            print(f"Navigating to: {search_url}")
            driver.get(search_url)
            
            # Add random delay after page load
            time.sleep(random.uniform(2, 4))
            
            # Scroll the page randomly to simulate human behavior
            for _ in range(random.randint(2, 4)):
                driver.execute_script(f"window.scrollTo(0, {random.randint(100, 500)});")
                time.sleep(random.uniform(0.5, 1.5))
            
            # Check for bot detection signs
            print("Checking page source for bot detection signs...")
            page_source = driver.page_source.lower()
            bot_signs = [
                'unusual traffic',
                'captcha',
                'robot',
                'automated queries',
                'automated requests',
                'please verify you are a human',
                'please type the characters below',
                'please solve this puzzle'
            ]
            
            for sign in bot_signs:
                if sign in page_source:
                    print(f"WARNING: Found bot detection sign: '{sign}'")
                    # Add additional delay if bot detection is found
                    time.sleep(random.uniform(5, 8))
                    # Try to refresh the page once
                    driver.refresh()
                    time.sleep(random.uniform(3, 5))
                    page_source = driver.page_source.lower()
            
            # Try multiple selectors for the main results container
            results_selectors = [
                'div#search',  # Primary selector
                'div[role="main"]',  # Alternative selector
                'div#rso',  # Another common selector
                'div[data-sokoban-container]'  # Mobile results container
            ]
            
            results_container = None
            for selector in results_selectors:
                try:
                    results_container = driver.find_element(By.CSS_SELECTOR, selector)
                    if results_container:
                        print(f"Found results container with selector: {selector}")
                        break
                except:
                    continue
            
            if not results_container:
                print("WARNING: Could not find main results container with any selector")
                # Save the page source for debugging
                with open('debug_page_source.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print("Saved page source to debug_page_source.html")
                return []
            
            # Try multiple selectors for titles
            title_selectors = [
                'h3',  # Primary selector
                'div.g h3',  # Alternative selector
                'div[data-sokoban-container] h3',  # Mobile results selector
                'div[role="heading"]'  # Another common selector
            ]
            
            # List of titles to exclude
            excluded_titles = {
                'popular products',
                'people also ask',
                'more products',
                'fast pickup or delivery',
                'in stores nearby',
                'deals on basketball shoes',
                'images',
                'discussions and forums',
                'shopping results',
                'related searches',
                'top stories',
                'videos',
                'news',
                'maps',
                'books',
                'flights',
                'hotels',
                'finance',
                'all',
                'shopping',
                'news',
                'videos',
                'images',
                'maps',
                'books',
                'flights',
                'finance',
                'all filters',
                'reviews'
            }
            
            titles = []
            domains = []
            for selector in title_selectors:
                try:
                    elements = results_container.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"Found {len(elements)} titles with selector: {selector}")
                        for elem in elements:
                            title_text = elem.text.strip().lower()
                            # Skip if title is in excluded list
                            if title_text in excluded_titles:
                                continue
                            if elem.text:
                                # Try to find the parent anchor tag that contains the href
                                try:
                                    parent_a = elem.find_element(By.XPATH, "./ancestor::a")
                                    if parent_a:
                                        href = parent_a.get_attribute("href")
                                        if href:
                                            domain = urlparse(href).netloc
                                            if domain.startswith('www.'):
                                                domain = domain[4:]  # Remove www.
                                            if domain:
                                                titles.append(f"{elem.text} ({domain})")
                                                continue
                                except:
                                    pass
                                # If we couldn't get the domain or there was an error, just add the title
                                titles.append(elem.text)
                except Exception as e:
                    print(f"Error with selector {selector}: {str(e)}")
                    continue
            
            # Remove duplicates while preserving order
            titles = list(dict.fromkeys(titles))
            print(f"Found {len(titles)} unique titles")
            
            # Save the page source for debugging if no results found
            if not titles:
                print("WARNING: No titles found, saving page source for debugging")
                with open('debug_page_source.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print("Saved page source to debug_page_source.html")
            
            return titles
            
        except Exception as e:
            print(f"Error scraping Google results: {str(e)}")
            print("Full error details:", e.__class__.__name__)
            return []
            
        finally:
            try:
                driver.quit()
            except:
                pass

    def analyze_titles(self, titles: List[str]) -> Tuple[Dict[str, int], List[str]]:
        """Analyze titles to find common terms and patterns."""
        try:
            # Strip domains from titles before analysis
            clean_titles = [title.split(' (')[0] for title in titles]
            
            all_text = ' '.join(clean_titles).lower()
            # Simple word splitting as fallback if NLTK tokenization fails
            try:
                tokens = word_tokenize(all_text)
            except:
                print("NLTK tokenization failed, falling back to basic splitting")
                tokens = all_text.split()
            
            filtered_tokens = [
                token for token in tokens
                if token not in self.stop_words
                and token.isalnum()
                and len(token) > 2
            ]
            
            term_frequency = Counter(filtered_tokens)
            top_terms = [term for term, _ in term_frequency.most_common(10)]
            
            return dict(term_frequency), top_terms
            
        except Exception as e:
            print(f"Error in analyze_titles: {e}")
            return {}, []

    def generate_title_with_gpt4(self, keyword: str, top_terms: List[str], temperature: float = 0.4, instructions: str = None) -> str:
        """Generate a unique title using GPT-4 based on analysis."""
        if not self.openai_client:
            print("Skipping GPT-4 title generation - no API key available")
            return "OpenAI API key not provided"

        prompt = f"""Based on analysis of top-ranking titles for the keyword '{keyword}',
        the most common terms are: {', '.join(top_terms)}.
        
        {instructions}"""

        try:
            print("Generating title with GPT-4...")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-2024-11-20",
                messages=[
                    {"role": "system", "content": "You are an SEO expert specialized in creating optimized title tags. Return only the title without quotes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=temperature
            )

            # Get the response and clean it up
            title = response.choices[0].message.content.strip()
            
            # Remove any quotes
            title = title.strip('"').strip("'")
            print(f"GPT-4 generated title: {title}")
            
            return title

        except Exception as e:
            print(f"Error generating title with GPT-4: {e}")
            return "Error generating title with GPT-4"

    def generate_title_with_claude(self, keyword: str, top_terms: List[str], temperature: float = 0.4, instructions: str = None) -> str:
        """Generate a unique title using Claude based on analysis."""
        if not self.anthropic_client:
            print("Skipping Claude title generation - no API key available")
            return "Anthropic API key not provided"

        try:
            print("Generating title with Claude...")
            prompt = f"""Based on analysis of top-ranking titles for the keyword '{keyword}',
            the most common terms are: {', '.join(top_terms)}.
            
            {instructions}"""

            response = self.anthropic_client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=100,
                temperature=temperature,
                system="You are an SEO expert. Generate only the title tag without any additional text or explanation.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Get the response and clean it up
            title = response.content[0].text.strip()
            
            # Remove any quotes or extra formatting
            title = title.strip('"').strip("'")
            
            print(f"Claude generated title: {title}")

            if not title:
                return "Error: Claude did not generate a title"

            return title

        except Exception as e:
            print(f"Error generating title with Claude: {e}")
            return "Error generating title with Claude"

    def run_analysis(self, keyword: str, temperature: float = 0.4, instructions: str = None) -> Dict:
        """Run the complete analysis and title generation process."""
        # Get search results
        print(f"\nStarting analysis for keyword: {keyword}")
        titles = self.get_search_results(keyword)

        if not titles:
            print("No titles found to analyze")
            return {
                "keyword": keyword,
                "num_titles_analyzed": 0,
                "top_terms": [],
                "term_frequency": {},
                "gpt4_title": "No titles found to analyze",
                "claude_title": "No titles found to analyze",
                "analyzed_titles": []
            }

        # Analyze titles
        print(f"\nAnalyzing {len(titles)} titles...")
        term_frequency, top_terms = self.analyze_titles(titles)

        # Generate new titles based on available APIs
        print("\nGenerating optimized titles...")
        results = {
            "keyword": keyword,
            "num_titles_analyzed": len(titles),
            "top_terms": top_terms,
            "term_frequency": term_frequency,
            "analyzed_titles": titles
        }

        # Generate titles only if API clients are available
        if self.openai_client:
            results["gpt4_title"] = self.generate_title_with_gpt4(keyword, top_terms, temperature, instructions)
        else:
            results["gpt4_title"] = "OpenAI API key not provided"

        if self.anthropic_client:
            results["claude_title"] = self.generate_title_with_claude(keyword, top_terms, temperature, instructions)
        else:
            results["claude_title"] = "Anthropic API key not provided"

        return results

def print_results(results: Dict):
    """Print results in a formatted way"""
    print("\nAnalysis Results")
    print(f"Keyword: {results['keyword']}")
    print(f"Titles Analyzed: {results['num_titles_analyzed']}")
    print("\nTop Terms:")
    for term in results['top_terms']:
        print(f"- {term}: {results['term_frequency'][term]} occurrences")
    print("\nGenerated Titles:")
    
    if results['gpt4_title'] != "OpenAI API key not provided":
        print(f"GPT-4o: {results['gpt4_title']}")
    
    if results['claude_title'] != "Anthropic API key not provided":
        print(f"Claude 3.7 Sonnet: {results['claude_title']}")

def main():
    # Get API keys from environment variables
    openai_key = os.getenv('OPENAI_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')

    if not openai_key and not anthropic_key:
        print("Error: Neither OPENAI_KEY nor ANTHROPIC_API_KEY found. Please set at least one API key in your .env file")
        return

    # Initialize analyzer with available keys
    analyzer = TitleAnalyzer(openai_key, anthropic_key)

    # Print available services
    print("\nAvailable AI Services:")
    if openai_key:
        print("✓ GPT-4")
    if anthropic_key:
        print("✓ Claude")
    print()

    # Get keyword from user
    keyword = input("Enter the keyword to analyze: ")

    # Run analysis
    results = analyzer.run_analysis(keyword)

    # Display results
    print_results(results)

if __name__ == "__main__":
    main()