import time
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from io import BytesIO
import pypdf

class WebSearchManager:
    def __init__(self):
        self.cache = {} # Simple in-memory cache URL -> content
        self.ddgs = DDGS()

    def search(self, query, num_results=3):
        try:
            # 1. Get raw search results (link & Snippet)
            results = list(self.ddgs.text(query, max_results=num_results))
            
            # 2. Deep Scrape the top result to improve accuracy
            # (Fetching full content prevents "hallucination based on limited snippet")
            if results:
                top_url = results[0]['href']
                print(f"DEBUG: Deep Scraping top result: {top_url}")
                full_content = self.scrape(top_url)
                
                # Append full content to the result body
                results[0]['body'] += f"\n\n[FULL CONTENT RETRIEVED VIA JINA READER]:\n{full_content[:3000]}..." # Limit 3k chars

            return results
        except Exception as e:
             # Fallback
            print(f"DEBUG: Search error: {e}")
            return [{"error": f"Search failed: {e}"}]

    def scrape(self, url):
        if url in self.cache:
            return self.cache[url]

        # Use Jina Reader for cleaner Markdown extraction
        jina_url = f"https://r.jina.ai/{url}"
        
        try:
            # Basic Anti-Bot headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'X-Return-Format': 'markdown'
            }
            
            # Check if PDF
            if url.lower().endswith('.pdf'):
                return self._scrape_pdf(url, headers)

            # TRY JINA AI FIRST (Simpler, cleaner)
            try:
                response = requests.get(jina_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    text = response.text
                    self.cache[url] = text[:5000]
                    return text[:5000]
            except Exception as jina_err:
                print(f"DEBUG: Jina Reader failed ({jina_err}), falling back to direct soup.")

            # FALLBACK to BeautifulSoup
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text()
            
            # Clean whitespaces
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            self.cache[url] = text[:2000]
            return text[:5000]
            
        except Exception as e:
            return f"Error scraping {url}: {e}"

    def _scrape_pdf(self, url, headers):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            f = BytesIO(response.content)
            reader = pypdf.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            self.cache[url] = text[:2000]
            return text[:5000]
        except Exception as e:
            return f"Error reading PDF {url}: {e}"
