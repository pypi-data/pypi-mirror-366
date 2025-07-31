"""
Web crawler utility for crawling websites and extracting content.
"""

import time
import logging
from typing import List, Dict, Set, Optional
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class WebCrawler:
    """Simple web crawler for extracting content from websites."""
    
    def __init__(self, max_pages: int = 10, delay: float = 0.5):
        """
        Initialize crawler.
        
        Args:
            max_pages: Maximum number of pages to crawl
            delay: Delay between requests in seconds
        """
        self.max_pages = max_pages
        self.delay = delay
        self.visited_urls: Set[str] = set()
    
    def crawl(self, base_url: str, max_depth: int = 2) -> List[Dict[str, str]]:
        """
        Crawl website starting from base URL.
        
        Args:
            base_url: Starting URL
            max_depth: Maximum crawl depth
            
        Returns:
            List of pages with url, title, and content
        """
        logger.info(f"Starting crawl from {base_url}")
        
        # Mock implementation - in production use requests + BeautifulSoup
        results = []
        urls_to_visit = [(base_url, 0)]  # (url, depth)
        
        while urls_to_visit and len(results) < self.max_pages:
            url, depth = urls_to_visit.pop(0)
            
            if url in self.visited_urls or depth > max_depth:
                continue
                
            self.visited_urls.add(url)
            
            # Mock page fetch
            page_data = self._fetch_page(url)
            if page_data:
                results.append(page_data)
                
                # Add linked pages (mock)
                if depth < max_depth:
                    links = self._extract_links(url, page_data)
                    for link in links[:3]:  # Limit links per page
                        if link not in self.visited_urls:
                            urls_to_visit.append((link, depth + 1))
            
            # Rate limiting
            time.sleep(self.delay)
        
        logger.info(f"Crawled {len(results)} pages")
        return results
    
    def _fetch_page(self, url: str) -> Optional[Dict[str, str]]:
        """
        Fetch and parse a single page.
        
        Args:
            url: URL to fetch
            
        Returns:
            Page data or None if failed
        """
        logger.info(f"Fetching {url}")
        
        # Mock implementation
        # In production, use requests to fetch and BeautifulSoup to parse
        
        # Generate mock content based on URL
        path = urlparse(url).path
        
        if not path or path == "/":
            title = "Home - Example Site"
            content = """Welcome to our example website. This site demonstrates web crawling capabilities.
            
We have several sections:
- About Us: Learn more about our company
- Products: Browse our product catalog  
- Blog: Read our latest articles
- Contact: Get in touch with us

Our mission is to provide excellent examples for web crawling demonstrations."""
        
        elif "about" in path:
            title = "About Us - Example Site"
            content = """About Our Company

Founded in 2020, we are a leading provider of example content for demonstrations.
Our team is dedicated to creating high-quality mock data for testing purposes.

Key Facts:
- 50+ employees
- Offices in 3 countries
- 1000+ satisfied customers
- Award-winning example content"""
        
        elif "product" in path:
            title = "Products - Example Site"
            content = """Our Product Catalog

Product 1: Widget Pro
- Advanced features for professionals
- Price: $99.99
- In stock

Product 2: Widget Basic
- Essential features for beginners
- Price: $29.99
- Limited availability

Product 3: Widget Enterprise
- Complete solution for businesses
- Contact for pricing
- Custom configurations available"""
        
        elif "blog" in path:
            title = "Blog - Example Site"
            content = """Latest Blog Posts

1. "10 Tips for Better Web Crawling" (March 2024)
   Learn the best practices for efficient and respectful web crawling.

2. "Understanding Robots.txt" (February 2024)
   A comprehensive guide to robots.txt and crawling etiquette.

3. "Building Scalable Crawlers" (January 2024)
   Architecture patterns for large-scale web crawling operations."""
        
        else:
            title = f"Page - {path}"
            content = f"This is example content for the page at {path}. It contains various information relevant to web crawling demonstrations."
        
        return {
            "url": url,
            "title": title,
            "content": content,
            "word_count": len(content.split())
        }
    
    def _extract_links(self, base_url: str, page_data: Dict[str, str]) -> List[str]:
        """
        Extract links from page (mock implementation).
        
        Args:
            base_url: Current page URL
            page_data: Page data
            
        Returns:
            List of absolute URLs
        """
        # Mock link extraction
        base_domain = urlparse(base_url).netloc
        
        # Generate some mock links based on content
        mock_links = []
        
        if "home" in page_data["title"].lower() or base_url.endswith("/"):
            # Home page links
            mock_links = [
                urljoin(base_url, "/about"),
                urljoin(base_url, "/products"),
                urljoin(base_url, "/blog"),
                urljoin(base_url, "/contact")
            ]
        elif "product" in page_data["content"].lower():
            # Product page links
            mock_links = [
                urljoin(base_url, "/products/widget-pro"),
                urljoin(base_url, "/products/widget-basic"),
                urljoin(base_url, "/products/widget-enterprise")
            ]
        elif "blog" in page_data["content"].lower():
            # Blog links
            mock_links = [
                urljoin(base_url, "/blog/web-crawling-tips"),
                urljoin(base_url, "/blog/robots-txt-guide"),
                urljoin(base_url, "/blog/scalable-crawlers")
            ]
        
        # Filter to same domain only
        filtered_links = []
        for link in mock_links:
            if urlparse(link).netloc == base_domain:
                filtered_links.append(link)
        
        return filtered_links


def crawl_website(base_url: str, max_pages: int = 10) -> List[Dict[str, str]]:
    """
    Convenience function to crawl a website.
    
    Args:
        base_url: Starting URL
        max_pages: Maximum pages to crawl
        
    Returns:
        List of crawled pages
    """
    crawler = WebCrawler(max_pages=max_pages)
    return crawler.crawl(base_url)


if __name__ == "__main__":
    # Test the crawler
    import json
    
    print("Testing Web Crawler")
    print("=" * 50)
    
    test_url = "https://example.com"
    results = crawl_website(test_url, max_pages=5)
    
    print(f"\nCrawled {len(results)} pages from {test_url}:")
    for page in results:
        print(f"\n- {page['title']}")
        print(f"  URL: {page['url']}")
        print(f"  Words: {page['word_count']}")
        print(f"  Preview: {page['content'][:100]}...")
    
    # Save results
    with open("crawl_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to crawl_results.json")