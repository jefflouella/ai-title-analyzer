import requests
import json
from collections import Counter
import nltk
import ssl
import certifi
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import openai
from typing import List, Dict, Tuple
import os
from dotenv import load_dotenv

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
# Function to safely download NLTK data
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
    def __init__(self, serpapi_key: str, openai_key: str):
        """Initialize the TitleAnalyzer with necessary API keys."""
        self.serpapi_key = serpapi_key
        self.openai_key = openai_key
        self.stop_words = set(stopwords.words('english'))
        # Add custom stop words relevant for titles
        self.stop_words.update(['|', '-', '2025', '2024', '2023', 'best', 'top', 'guide'])

    def get_search_results(self, keyword: str, num_results: int = 100) -> List[str]:
        """Fetch search results using SERPAPI."""
        url = "https://serpapi.com/search.json"
        params = {
            "q": keyword,
            "api_key": self.serpapi_key,
            "num": num_results
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract titles from organic results
            titles = [result.get('title', '') for result in data.get('organic_results', [])]
            return titles[:num_results]

        except requests.exceptions.RequestException as e:
            print(f"Error fetching search results: {e}")
            return []

    def analyze_titles(self, titles: List[str]) -> Tuple[Dict[str, int], List[str]]:
        """Analyze titles to find common terms and patterns."""
        try:
            all_text = ' '.join(titles).lower()
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

        term_frequency = Counter(filtered_tokens)
        top_terms = [term for term, _ in term_frequency.most_common(10)]

        return dict(term_frequency), top_terms

    def generate_title(self, keyword: str, top_terms: List[str]) -> str:
        """Generate a unique title using ChatGPT based on analysis."""
        prompt = f"""Based on analysis of top-ranking titles for the keyword '{keyword}',
        the most common terms are: {', '.join(top_terms)}.
        Create a unique and engaging title tag (max 60 characters) that:
        1. Incorporates 2-3 of the most relevant common terms
        2. Adds a unique angle or perspective
        3. Maintains search intent
        4. Includes the main keyword naturally
        """

        try:
            client = openai.OpenAI(api_key=self.openai_key)
            response = client.chat.completions.create(
                model="gpt-4o",  # Using more widely available model
                messages=[
                    {"role": "system", "content": "You are an SEO expert specialized in creating optimized title tags."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.4
            )

            generated_title = response.choices[0].message.content.strip()
            return generated_title

        except Exception as e:
            print(f"Error generating title with ChatGPT: {e}")
            return ""

    def run_analysis(self, keyword: str) -> Dict:
        """Run the complete analysis and title generation process."""
        # Get search results
        print(f"Fetching search results for: {keyword}")
        titles = self.get_search_results(keyword)

        if not titles:
            return {"error": "No titles found"}

        # Analyze titles
        print("Analyzing titles...")
        term_frequency, top_terms = self.analyze_titles(titles)

        # Generate new title
        print("Generating optimized title...")
        new_title = self.generate_title(keyword, top_terms)

        return {
            "keyword": keyword,
            "num_titles_analyzed": len(titles),
            "top_terms": top_terms,
            "term_frequency": term_frequency,
            "generated_title": new_title
        }

def print_results(results: Dict):
    """Print results in a formatted way"""
    print("\nAnalysis Results")
    print(f"Keyword: {results['keyword']}")
    print(f"Titles Analyzed: {results['num_titles_analyzed']}")
    print("\nTop Terms:")
    for term in results['top_terms']:
        print(f"- {term}: {results['term_frequency'][term]} occurrences")
    print("\nGenerated Title:")
    print(f"{results['generated_title']}")

def main():
    # Get API keys from environment variables
    serpapi_key = os.getenv('SERPAPI_KEY')
    openai_key = os.getenv('OPENAI_KEY')

    if not serpapi_key or not openai_key:
        print("Error: API keys not found. Please set SERPAPI_KEY and OPENAI_KEY in your .env file")
        return

    # Initialize analyzer
    analyzer = TitleAnalyzer(serpapi_key, openai_key)

    # Get keyword from user
    keyword = input("Enter the keyword to analyze: ")

    # Run analysis
    results = analyzer.run_analysis(keyword)

    # Display results
    print_results(results)

if __name__ == "__main__":
    main()