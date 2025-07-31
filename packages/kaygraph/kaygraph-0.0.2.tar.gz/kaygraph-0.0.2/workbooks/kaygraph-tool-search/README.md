# KayGraph Tool Integration - Web Search

Demonstrates integrating web search capabilities with KayGraph for building information retrieval and analysis workflows.

## What it does

This example shows how to:
- **Web Search**: Query multiple search engines
- **Multi-Source Search**: Aggregate results from different sources
- **Result Analysis**: Extract patterns and insights
- **Information Synthesis**: Combine findings into summaries
- **Report Generation**: Create comprehensive search reports

## Features

- Mock search engine with realistic results
- Support for web, news, and academic searches
- Relevance scoring and ranking
- Date filtering and language support
- Search result aggregation and analysis
- Automated insight extraction

## How to run

```bash
python main.py
```

## Architecture

```
SearchQueryNode → MultiSourceSearchNode → AnalyzeResultsNode → SearchSynthesisNode → SaveSearchReportNode
      ↓ (error)            ↗
```

### Node Descriptions

1. **SearchQueryNode**: Performs single-source web search
2. **MultiSourceSearchNode**: Searches across multiple sources
3. **AnalyzeResultsNode**: Analyzes patterns in results
4. **SearchSynthesisNode**: Synthesizes key information
5. **SaveSearchReportNode**: Generates comprehensive report

## Search Types

### 1. Web Search
General web content including:
- Documentation and guides
- Blog posts and articles
- Stack Overflow answers
- Official references

### 2. News Search
Recent news and updates:
- Technology news
- Industry updates
- Press releases
- Breaking developments

### 3. Academic Search
Research papers and studies:
- ArXiv papers
- Conference proceedings
- Journal articles
- Technical reports

## Example Output

```
🔍 KayGraph Web Search Tool Integration
============================================================
This example demonstrates web search integration
for information retrieval and analysis.

============================================================
Query 1/2: latest advances in quantum computing 2024
============================================================

🔍 Search Results for 'latest advances in quantum computing 2024':
Found 15 results (type: web)
------------------------------------------------------------

1. Everything You Need to Know About latest advances in quantum computing 2024
   🔗 https://encyclopedia.com/article
   📝 Comprehensive information about latest advances in quantum computing 2024. This article covers history, current state, and future prospects...
   📊 Relevance: 0.90

2. Latest developments in latest advances in quantum computing 2024: What you need to know
   🔗 https://news.example.com/article/1
   📝 Recent advances in latest advances in quantum computing 2024 have shown promising results. Experts predict significant impact on the industry...
   📊 Relevance: 0.85

🔍 Multi-Source Search Results:
============================================================

📌 WEB (5 results):
  1. Understanding latest advances in quantum computing 2024: A Comprehensive Overview
     Explore the fundamentals of latest advances in quantum computing 2024 and its applications...
  2. latest advances in quantum computing 2024 in Practice: Real-World Applications
     See how latest advances in quantum computing 2024 is being used in industry today...

📌 NEWS (5 results):
  1. Latest developments in latest advances in quantum computing 2024: What you need to know
     Recent advances in latest advances in quantum computing 2024 have shown promising results...

📌 ACADEMIC (5 results):
  1. A Survey of latest advances in quantum computing 2024: Methods, Applications, and Future Directions
     Abstract: This paper presents a comprehensive survey of latest advances in quantum computing...

📊 Search Insights:
  - Total results: 15
  - Sources searched: web, news, academic

  Top domains:
    • encyclopedia.com: 1 results
    • news.example.com: 1 results
    • ai-blog.com: 1 results

  Common terms:
    latest, advances, quantum, computing, 2024

🧠 Search Analysis:
============================================================

🔍 Patterns Identified:
  • Educational content available

💡 Key Findings:
  • High average relevance across sources

📝 Recommendations:
  • Academic sources available - good for in-depth research

📝 Search Synthesis:
============================================================
Query: 'latest advances in quantum computing 2024'
Sources: web, news, academic
Confidence: 73%

📌 Summary:
Based on 30 search results for 'latest advances in quantum computing 2024', the most relevant information comes from 3 sources. Key findings include insights on latest advances in quantum computing 2024 from various perspectives.

🔑 Key Points:

1. Comprehensive information about latest advances in quantum computing 2024.
   Source: Everything You Need to Know About latest advances in quantum computing 2024
   Relevance: 0.90

2. Recent advances in latest advances in quantum computing 2024 have shown promising results.
   Source: Latest developments in latest advances in quantum computing 2024: What you need to know
   Relevance: 0.85

💾 Search report saved to: search_report.json
   Contains 10 top results
   Query: 'latest advances in quantum computing 2024'

✅ Completed search workflow for query 1
```

## Integration with Real Search APIs

### Google Custom Search
```python
from googleapiclient.discovery import build

class GoogleSearchEngine(SearchEngine):
    def __init__(self, api_key, cse_id):
        self.service = build("customsearch", "v1", developerKey=api_key)
        self.cse_id = cse_id
    
    def search(self, query, num_results=10):
        result = self.service.cse().list(
            q=query,
            cx=self.cse_id,
            num=num_results
        ).execute()
        
        return self._parse_google_results(result)
```

### Bing Search API
```python
import requests

class BingSearchEngine(SearchEngine):
    def __init__(self, api_key):
        self.api_key = api_key
        self.endpoint = "https://api.bing.microsoft.com/v7.0/search"
    
    def search(self, query, num_results=10):
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {"q": query, "count": num_results}
        
        response = requests.get(self.endpoint, headers=headers, params=params)
        return self._parse_bing_results(response.json())
```

### SerpAPI (Multiple Search Engines)
```python
from serpapi import GoogleSearch

class SerpAPIEngine(SearchEngine):
    def __init__(self, api_key):
        self.api_key = api_key
    
    def search(self, query, num_results=10):
        params = {
            "q": query,
            "num": num_results,
            "api_key": self.api_key
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        return self._parse_serp_results(results)
```

## Advanced Features

### 1. Query Expansion
```python
def expand_query(original_query):
    """Expand query with synonyms and related terms."""
    expanded_terms = get_synonyms(original_query)
    related_terms = get_related_terms(original_query)
    
    return f"{original_query} {' '.join(expanded_terms + related_terms)}"
```

### 2. Result Re-ranking
```python
def rerank_results(results, user_preferences):
    """Re-rank results based on user preferences."""
    for result in results:
        # Boost score based on preferences
        if user_preferences.get("prefer_recent") and is_recent(result):
            result.relevance_score *= 1.2
        
        if user_preferences.get("prefer_academic") and result.source == "academic":
            result.relevance_score *= 1.3
    
    return sorted(results, key=lambda x: x.relevance_score, reverse=True)
```

### 3. Fact Extraction
```python
def extract_facts(search_results):
    """Extract factual statements from search results."""
    facts = []
    
    for result in search_results:
        # Extract sentences with factual patterns
        sentences = extract_factual_sentences(result.snippet)
        facts.extend(sentences)
    
    return deduplicate_facts(facts)
```

## Use Cases

- **Research Assistant**: Gather information on topics
- **News Monitoring**: Track latest developments
- **Competitive Intelligence**: Monitor industry trends
- **Content Curation**: Find relevant content
- **Fact Checking**: Verify information

## Performance Tips

1. **Caching**: Cache search results to avoid API limits
2. **Rate Limiting**: Respect API rate limits
3. **Parallel Searches**: Search multiple sources concurrently
4. **Result Deduplication**: Remove duplicate results
5. **Smart Filtering**: Pre-filter irrelevant results

## Best Practices

1. **API Key Security**: Store keys in environment variables
2. **Error Handling**: Handle API failures gracefully
3. **Result Validation**: Verify result quality
4. **User Privacy**: Don't log sensitive queries
5. **Citation**: Always attribute sources

## Dependencies

This example uses mock search. For production:
- `google-api-python-client`: Google Custom Search
- `requests`: HTTP requests for APIs
- `serpapi`: Multiple search engine access
- `beautifulsoup4`: Parse search result pages