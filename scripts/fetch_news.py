import urllib.request
import xml.etree.ElementTree as ET
import json
import os

# Fuentes RSS más institucionales y educativas
FEEDS = {
    "nacional": "https://www.telam.com.ar/rss/cultura.xml", # Cultura suele ser más escolar
    "ciencias": "https://www.agenciasinc.es/rss/content/view/full/356", # Agencia SINC es excelente para ciencia
    "geopolitica": "http://feeds.bbci.co.uk/mundo/rss.xml", # RSS general de BBC Mundo
    "sustentabilidad": "https://elpais.com/rss/clima_y_medio_ambiente/portada.xml"
}

def fetch_feed(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        xml_data = response.read()
        root = ET.fromstring(xml_data)
        news = []
        # Buscamos items tanto en RSS 2.0 como en Atom
        items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
        
        for item in items[:8]:
            title = item.find('title').text if item.find('title') is not None else "Sin título"
            link = item.find('link').text if item.find('link') is not None else ""
            if not link and item.find('{http://www.w3.org/2005/Atom}link') is not None:
                link = item.find('{http://www.w3.org/2005/Atom}link').get('href')
            
            news.append({
                "title": title.strip(),
                "link": link,
                "source": "Automático"
            })
        return news
    except Exception as e:
        return [{"title": f"Error cargando fuente", "link": url, "source": "Error"}]

def main():
    results = {}
    
    # 1. Cargar noticias sugeridas manualmente por Julieta
    manual_file = 'manual_news.json'
    if not os.path.exists(manual_file):
        with open(manual_file, 'w', encoding='utf-8') as f:
            json.dump([
                {"category": "nacional", "title": "Iniciativa popular contra la reforma de glaciares", "link": ""},
                {"category": "nacional", "title": "Comienza la Feria Internacional del Libro de Buenos Aires", "link": ""}
            ], f, ensure_ascii=False, indent=4)
    
    with open(manual_file, 'r', encoding='utf-8') as f:
        manual_entries = json.load(f)

    # 2. Buscar automáticas
    for category, url in FEEDS.items():
        print(f"Buscando noticias de {category}...")
        results[category] = fetch_feed(url)
        
        # Inyectar las manuales en su categoría correspondiente
        for entry in manual_entries:
            if entry['category'] == category:
                results[category].insert(0, {
                    "title": entry['title'],
                    "link": entry.get('link', ''),
                    "source": "Julieta"
                })

    with open('pending_news.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print("\n¡Listo! He incluido tus sugerencias y mejorado la búsqueda.")

if __name__ == "__main__":
    main()
