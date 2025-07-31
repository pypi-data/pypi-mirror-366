"""
Web search tool utility for searching and retrieving information.

This module provides mock search functionality that simulates
real search APIs for demonstration purposes.
"""

import hashlib
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class SearchResult:
    """Represents a single search result."""
    
    def __init__(
        self,
        title: str,
        url: str,
        snippet: str,
        source: str = "web",
        published_date: Optional[str] = None,
        relevance_score: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.source = source
        self.published_date = published_date or datetime.now().isoformat()
        self.relevance_score = relevance_score
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "published_date": self.published_date,
            "relevance_score": self.relevance_score,
            "metadata": self.metadata
        }


class SearchEngine:
    """Mock search engine for web searches."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize search engine.
        
        Args:
            api_key: API key (not used in mock implementation)
        """
        self.api_key = api_key
        self.search_count = 0
    
    def search(
        self,
        query: str,
        num_results: int = 10,
        search_type: str = "web",
        region: str = "us",
        language: str = "en",
        date_filter: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Perform a web search.
        
        Args:
            query: Search query
            num_results: Number of results to return
            search_type: Type of search (web, news, images, videos)
            region: Region code
            language: Language code
            date_filter: Date filter (day, week, month, year)
            
        Returns:
            List of search results
        """
        self.search_count += 1
        logger.info(f"Searching for: '{query}' (type: {search_type})")
        
        # Generate mock results based on query
        if search_type == "web":
            results = self._generate_web_results(query, num_results)
        elif search_type == "news":
            results = self._generate_news_results(query, num_results)
        elif search_type == "academic":
            results = self._generate_academic_results(query, num_results)
        else:
            results = self._generate_web_results(query, num_results)
        
        # Apply date filter if specified
        if date_filter:
            results = self._apply_date_filter(results, date_filter)
        
        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results[:num_results]
    
    def _generate_web_results(self, query: str, num_results: int) -> List[SearchResult]:
        """Generate mock web search results."""
        results = []
        
        # Create deterministic but varied results
        query_hash = hashlib.md5(query.encode()).hexdigest()
        random.seed(query_hash)
        
        # Define result templates based on common queries
        templates = self._get_web_templates(query)
        
        for i in range(min(num_results, len(templates))):
            template = templates[i]
            
            # Calculate relevance based on query match
            relevance = self._calculate_relevance(query, template["title"], template["snippet"])
            
            result = SearchResult(
                title=template["title"],
                url=template["url"],
                snippet=template["snippet"],
                source="web",
                published_date=self._generate_date(i),
                relevance_score=relevance,
                metadata={
                    "domain": self._extract_domain(template["url"]),
                    "word_count": len(template["snippet"].split()),
                    "has_code": "code" in template["snippet"].lower()
                }
            )
            results.append(result)
        
        return results
    
    def _generate_news_results(self, query: str, num_results: int) -> List[SearchResult]:
        """Generate mock news search results."""
        results = []
        
        news_sources = ["TechNews", "AI Daily", "Developer Weekly", "Tech Crunch", "The Verge"]
        
        for i in range(num_results):
            # Generate news-style content
            title = f"Latest developments in {query}: What you need to know"
            snippet = f"Recent advances in {query} have shown promising results. Experts predict significant impact on the industry as companies race to implement new solutions..."
            
            result = SearchResult(
                title=title,
                url=f"https://news.example.com/article/{i+1}",
                snippet=snippet,
                source="news",
                published_date=self._generate_recent_date(i),
                relevance_score=0.9 - (i * 0.05),
                metadata={
                    "source": random.choice(news_sources),
                    "category": "Technology",
                    "read_time": f"{random.randint(3, 8)} min"
                }
            )
            results.append(result)
        
        return results
    
    def _generate_academic_results(self, query: str, num_results: int) -> List[SearchResult]:
        """Generate mock academic search results."""
        results = []
        
        for i in range(num_results):
            # Generate academic-style content
            title = f"A Survey of {query}: Methods, Applications, and Future Directions"
            authors = ["Smith, J.", "Johnson, A.", "Williams, B."]
            
            snippet = f"Abstract: This paper presents a comprehensive survey of {query}. We review the state-of-the-art approaches, analyze their strengths and limitations, and identify key challenges..."
            
            result = SearchResult(
                title=title,
                url=f"https://arxiv.org/abs/2024.{1000+i}",
                snippet=snippet,
                source="academic",
                published_date=self._generate_date(i * 30),  # Spread over months
                relevance_score=0.85 - (i * 0.08),
                metadata={
                    "authors": authors[:random.randint(1, 3)],
                    "venue": "International Conference on AI",
                    "citations": random.randint(0, 100),
                    "pdf_available": True
                }
            )
            results.append(result)
        
        return results
    
    def _get_web_templates(self, query: str) -> List[Dict[str, str]]:
        """Get web result templates based on query."""
        query_lower = query.lower()
        
        # Programming/Tech queries
        if any(term in query_lower for term in ["python", "programming", "code", "javascript", "api"]):
            return [
                {
                    "title": f"Getting Started with {query} - Complete Guide",
                    "url": "https://docs.example.com/guide",
                    "snippet": f"Learn {query} from scratch with our comprehensive guide. This tutorial covers everything from basic concepts to advanced techniques..."
                },
                {
                    "title": f"{query} Best Practices and Common Patterns",
                    "url": "https://blog.dev/best-practices",
                    "snippet": f"Discover the most effective patterns and practices for {query}. Our experts share insights from years of experience..."
                },
                {
                    "title": f"Stack Overflow - How to implement {query}",
                    "url": "https://stackoverflow.com/questions/12345",
                    "snippet": f"I'm trying to implement {query} but running into issues. Here's my code: [code example]. The error I'm getting is..."
                },
                {
                    "title": f"{query} Documentation - Official Reference",
                    "url": "https://official-docs.com/reference",
                    "snippet": f"Official documentation for {query}. Find API references, tutorials, and examples to help you build applications..."
                },
                {
                    "title": f"GitHub - awesome-{query.replace(' ', '-')}",
                    "url": "https://github.com/awesome/list",
                    "snippet": f"A curated list of awesome {query} resources, libraries, tools, and tutorials. Contributions welcome!"
                }
            ]
        
        # AI/ML queries
        elif any(term in query_lower for term in ["ai", "machine learning", "neural", "deep learning"]):
            return [
                {
                    "title": f"Understanding {query}: A Comprehensive Overview",
                    "url": "https://ai-blog.com/overview",
                    "snippet": f"Explore the fundamentals of {query} and its applications in modern technology. From basic concepts to cutting-edge research..."
                },
                {
                    "title": f"{query} in Practice: Real-World Applications",
                    "url": "https://ml-journal.com/applications",
                    "snippet": f"See how {query} is being used in industry today. Case studies from leading companies show the transformative power..."
                },
                {
                    "title": f"Research Paper: Advances in {query}",
                    "url": "https://arxiv.org/papers/latest",
                    "snippet": f"We present novel approaches to {query} that achieve state-of-the-art results on benchmark datasets..."
                },
                {
                    "title": f"Tutorial: Implementing {query} from Scratch",
                    "url": "https://tutorials.ai/implement",
                    "snippet": f"Step-by-step guide to implementing {query} using Python and popular frameworks. Includes code examples..."
                },
                {
                    "title": f"The Future of {query}: Trends and Predictions",
                    "url": "https://tech-future.com/trends",
                    "snippet": f"Industry experts weigh in on where {query} is headed. Key trends include increased automation and..."
                }
            ]
        
        # General queries
        else:
            return [
                {
                    "title": f"Everything You Need to Know About {query}",
                    "url": "https://encyclopedia.com/article",
                    "snippet": f"Comprehensive information about {query}. This article covers history, current state, and future prospects..."
                },
                {
                    "title": f"{query} - Wikipedia",
                    "url": "https://wikipedia.org/wiki/topic",
                    "snippet": f"{query} refers to... [brief description]. The concept has evolved significantly since its introduction..."
                },
                {
                    "title": f"Latest News: {query} Updates and Developments",
                    "url": "https://news.com/latest",
                    "snippet": f"Stay updated with the latest news about {query}. Recent developments include new initiatives and..."
                },
                {
                    "title": f"How {query} Works: Explained Simply",
                    "url": "https://explainer.com/how-it-works",
                    "snippet": f"Simple explanation of {query} for beginners. We break down complex concepts into easy-to-understand parts..."
                },
                {
                    "title": f"Top 10 Resources for Learning {query}",
                    "url": "https://learning-hub.com/resources",
                    "snippet": f"Curated list of the best resources to learn about {query}. From online courses to books and tutorials..."
                }
            ]
    
    def _calculate_relevance(self, query: str, title: str, snippet: str) -> float:
        """Calculate relevance score for a result."""
        query_words = set(query.lower().split())
        title_words = set(title.lower().split())
        snippet_words = set(snippet.lower().split())
        
        # Title matches are weighted more
        title_matches = len(query_words & title_words)
        snippet_matches = len(query_words & snippet_words)
        
        # Base score
        score = 0.5
        
        # Boost for title matches
        score += title_matches * 0.2
        
        # Boost for snippet matches
        score += min(snippet_matches * 0.05, 0.3)
        
        # Exact phrase match bonus
        if query.lower() in title.lower():
            score += 0.2
        elif query.lower() in snippet.lower():
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_date(self, days_ago: int) -> str:
        """Generate a date string."""
        date = datetime.now() - timedelta(days=days_ago)
        return date.isoformat()
    
    def _generate_recent_date(self, hours_ago: int) -> str:
        """Generate a recent date string."""
        date = datetime.now() - timedelta(hours=hours_ago)
        return date.isoformat()
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        # Simple extraction
        if "://" in url:
            domain = url.split("://")[1].split("/")[0]
            return domain
        return "unknown"
    
    def _apply_date_filter(self, results: List[SearchResult], date_filter: str) -> List[SearchResult]:
        """Apply date filter to results."""
        now = datetime.now()
        
        filters = {
            "day": timedelta(days=1),
            "week": timedelta(days=7),
            "month": timedelta(days=30),
            "year": timedelta(days=365)
        }
        
        if date_filter not in filters:
            return results
        
        cutoff = now - filters[date_filter]
        
        filtered = []
        for result in results:
            try:
                result_date = datetime.fromisoformat(result.published_date)
                if result_date >= cutoff:
                    filtered.append(result)
            except:
                # Keep results with invalid dates
                filtered.append(result)
        
        return filtered


class SearchAggregator:
    """Aggregate and analyze search results."""
    
    def __init__(self):
        self.engines = {
            "web": SearchEngine(),
            "news": SearchEngine(),
            "academic": SearchEngine()
        }
    
    def multi_search(
        self,
        query: str,
        sources: List[str] = ["web"],
        num_results_per_source: int = 5
    ) -> Dict[str, List[SearchResult]]:
        """
        Search across multiple sources.
        
        Args:
            query: Search query
            sources: List of sources to search
            num_results_per_source: Results per source
            
        Returns:
            Dictionary mapping source to results
        """
        results = {}
        
        for source in sources:
            if source in self.engines:
                engine = self.engines[source]
                source_results = engine.search(
                    query,
                    num_results=num_results_per_source,
                    search_type=source
                )
                results[source] = source_results
            else:
                logger.warning(f"Unknown source: {source}")
        
        return results
    
    def get_insights(self, results: Dict[str, List[SearchResult]]) -> Dict[str, Any]:
        """Extract insights from search results."""
        insights = {
            "total_results": sum(len(r) for r in results.values()),
            "sources": list(results.keys()),
            "top_domains": self._get_top_domains(results),
            "date_distribution": self._get_date_distribution(results),
            "relevance_stats": self._get_relevance_stats(results),
            "common_terms": self._extract_common_terms(results)
        }
        
        return insights
    
    def _get_top_domains(self, results: Dict[str, List[SearchResult]]) -> List[Tuple[str, int]]:
        """Get most common domains."""
        domain_counts = {}
        
        for source_results in results.values():
            for result in source_results:
                domain = result.metadata.get("domain", "unknown")
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # Sort by count
        sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_domains[:5]
    
    def _get_date_distribution(self, results: Dict[str, List[SearchResult]]) -> Dict[str, int]:
        """Get distribution of result dates."""
        distribution = {
            "today": 0,
            "week": 0,
            "month": 0,
            "older": 0
        }
        
        now = datetime.now()
        
        for source_results in results.values():
            for result in source_results:
                try:
                    result_date = datetime.fromisoformat(result.published_date)
                    days_ago = (now - result_date).days
                    
                    if days_ago == 0:
                        distribution["today"] += 1
                    elif days_ago <= 7:
                        distribution["week"] += 1
                    elif days_ago <= 30:
                        distribution["month"] += 1
                    else:
                        distribution["older"] += 1
                except:
                    distribution["older"] += 1
        
        return distribution
    
    def _get_relevance_stats(self, results: Dict[str, List[SearchResult]]) -> Dict[str, float]:
        """Get relevance statistics."""
        all_scores = []
        
        for source_results in results.values():
            for result in source_results:
                all_scores.append(result.relevance_score)
        
        if not all_scores:
            return {"avg": 0, "min": 0, "max": 0}
        
        return {
            "avg": sum(all_scores) / len(all_scores),
            "min": min(all_scores),
            "max": max(all_scores)
        }
    
    def _extract_common_terms(self, results: Dict[str, List[SearchResult]]) -> List[Tuple[str, int]]:
        """Extract common terms from results."""
        word_counts = {}
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were"}
        
        for source_results in results.values():
            for result in source_results:
                # Process title and snippet
                text = f"{result.title} {result.snippet}".lower()
                words = text.split()
                
                for word in words:
                    # Clean word
                    word = word.strip(".,!?;:\"'")
                    
                    # Skip short words and stop words
                    if len(word) > 3 and word not in stop_words:
                        word_counts[word] = word_counts.get(word, 0) + 1
        
        # Sort by count
        sorted_terms = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_terms[:10]


# Convenience functions

def search_web(query: str, num_results: int = 10) -> List[SearchResult]:
    """Perform a simple web search."""
    engine = SearchEngine()
    return engine.search(query, num_results=num_results)


def search_multi_source(query: str, sources: List[str] = ["web", "news"]) -> Dict[str, List[SearchResult]]:
    """Search across multiple sources."""
    aggregator = SearchAggregator()
    return aggregator.multi_search(query, sources=sources)


if __name__ == "__main__":
    # Test search functionality
    print("Testing Search Tool")
    print("=" * 50)
    
    # Test queries
    queries = [
        "Python machine learning tutorials",
        "Latest AI developments 2024",
        "How to build neural networks"
    ]
    
    for query in queries:
        print(f"\nSearching for: '{query}'")
        
        # Web search
        results = search_web(query, num_results=3)
        print(f"\nWeb Results ({len(results)}):")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.title}")
            print(f"   URL: {result.url}")
            print(f"   Relevance: {result.relevance_score:.2f}")
            print(f"   Snippet: {result.snippet[:100]}...")
    
    # Multi-source search
    print("\n\nMulti-Source Search Test:")
    multi_results = search_multi_source(
        "artificial intelligence breakthroughs",
        sources=["web", "news", "academic"]
    )
    
    for source, results in multi_results.items():
        print(f"\n{source.upper()} Results:")
        for result in results[:2]:
            print(f"  - {result.title}")