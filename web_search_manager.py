import time
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from io import BytesIO
import pypdf

class WebSearchManager:
    def __init__(self):
        self.cache = {} # cache simples na memória (url -> conteúdo)
        self.ddgs = DDGS()

    def search(self, query, num_results=3):
        try:
            # 1. pegando resultados brutos (link e trecho)
            results = list(self.ddgs.text(query, max_results=num_results))
            
            # 2. raspando fundo no primeiro resultado pra melhorar a precisão
            # (pegar o conteúdo todo evita alucinação com trecho curto)
            if results:
                top_url = results[0]['href']
                print(f"DEBUG: Deep Scraping top result: {top_url}")
                full_content = self.scrape(top_url)
                
                # juntando o conteúdo todo no corpo do resultado
                results[0]['body'] += f"\n\n[FULL CONTENT RETRIEVED VIA JINA READER]:\n{full_content[:3000]}..." # limitando 3k caracteres

            return results
        except Exception as e:
             # Fallback
            print(f"DEBUG: Search error: {e}")
            return [{"error": f"Search failed: {e}"}]

    def scrape(self, url):
        if url in self.cache:
            return self.cache[url]

        # usando o jina reader pra extrair markdown mais limpo
        jina_url = f"https://r.jina.ai/{url}"
        
        try:
            # headers básicos pra não parecer robô
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'X-Return-Format': 'markdown'
            }
            
            # checando se é pdf
            if url.lower().endswith('.pdf'):
                return self._scrape_pdf(url, headers)

            # tenta jina ai primeiro (mais simples e limpo)
            try:
                response = requests.get(jina_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    text = response.text
                    self.cache[url] = text[:5000]
                    return text[:5000]
            except Exception as jina_err:
                print(f"DEBUG: Jina Reader failed ({jina_err}), falling back to direct soup.")

            # se der ruim, vai de beautifulsoup mesmo
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # tirando scripts e estilos
            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text()
            
            # limpando espaços em branco
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
