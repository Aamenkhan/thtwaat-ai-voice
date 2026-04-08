import logging
import requests
import re
from typing import List

logger = logging.getLogger("thtwaat.images_internet")

def search_images_internet(query: str, count: int = 3) -> List[str]:
    """
    Simulate fetching high-quality images from the internet based on a scene query.
    In a real production environment, this would call a Search API (Google/Bing/Unsplash).
    """
    logger.info("Searching internet for: %s", query)
    
    # Mock behavior: Using high-quality placeholder URLs that match the query context
    # In practice, we'd use a real search engine API here.
    
    # Simple keyword extraction for better placeholders
    keywords = re.sub(r'[^a-zA-Z\s]', '', query).split()
    keyword_str = ",".join(keywords[:2]) if keywords else "technology"
    
    placeholders = [
        f"https://source.unsplash.com/featured/?{keyword_str},cinematic&{i}" 
        for i in range(count)
    ]
    
    return placeholders

def generate(script_text: str, count: int = 3) -> List[str]:
    """
    Main interface for the image step. Now switches to Internet-based searching.
    """
    # Extract a central theme from the script for searching
    theme = script_text[:100].split('.')[0] if script_text else "AI Future"
    return search_images_internet(theme, count)

if __name__ == "__main__":
    # Test
    imgs = generate("A futuristic city floating in the clouds with neon lights.")
    for img in imgs:
        print(img)