# KayGraph Tool Integration - Web Crawler

Demonstrates integrating external tools (web crawler) with KayGraph for website analysis. This example shows how to crawl websites, analyze content, and generate comprehensive reports.

## What it does

This tool integration example:
- **Crawls Websites**: Extracts content from multiple pages
- **Analyzes Content**: Extracts topics, sentiment, and insights
- **Generates Reports**: Creates detailed analysis reports
- **Handles Errors**: Graceful failure handling

## Features

- Configurable crawl depth and page limits
- Content analysis with topic extraction
- Sentiment analysis and readability scoring
- Aggregated insights across all pages
- Actionable recommendations
- JSON report generation

## How to run

```bash
# Crawl default example site
python main.py

# Crawl specific URL
python main.py https://example.com
```

## Architecture

```
CrawlWebsiteNode → AnalyzeContentBatchNode → GenerateReportNode
        ↓ (failed)
   ErrorHandlerNode
```

### Node Descriptions

1. **CrawlWebsiteNode**: Uses web crawler tool to extract pages
2. **AnalyzeContentBatchNode**: Batch processes pages for analysis
3. **GenerateReportNode**: Aggregates results and creates report
4. **ErrorHandlerNode**: Handles crawl failures gracefully

## Tool Integration Pattern

```python
# 1. External tool in utils/
from utils.web_crawler import crawl_website

# 2. Node wraps tool functionality
class CrawlWebsiteNode(Node):
    def exec(self, params):
        # Use external tool
        pages = crawl_website(url, max_pages)
        return {"pages": pages}

# 3. Clean separation of concerns
# - Tool: Handles crawling logic
# - Node: Handles orchestration
```

## Example Output

```
🕷️  KayGraph Web Crawler Tool Integration
============================================================
This example demonstrates integrating a web crawler
with KayGraph for website analysis.

Starting crawl of https://example.com...
Settings: max_pages=10, depth=2

[INFO] Starting crawl from https://example.com
[INFO] Fetching https://example.com
[INFO] Fetching https://example.com/about
[INFO] Fetching https://example.com/products
...

✅ Crawl Complete!
  - Base URL: https://example.com
  - Pages crawled: 10

📊 Content Analysis Complete!
  - Pages analyzed: 10
  - Total words: 2,543
  - Main topics: products, company, technology

============================================================
📄 WEBSITE ANALYSIS REPORT
============================================================

🌐 Crawl Summary:
  - URL: https://example.com
  - Pages: 10

📊 Content Insights:
  - Total words: 2,543
  - Avg readability: 75.3/100
  - Main topics: products, company, technology, blog, business
  - Sentiment: Positive(7) Neutral(2) Negative(1)

📋 Top Pages:
  1. Home - Example Site
     - Topics: company, products, technology
     - Readability: 82/100
  2. Products - Example Site
     - Topics: products, business, technology
     - Readability: 78/100
  3. About Us - Example Site
     - Topics: company, business
     - Readability: 71/100

💡 Recommendations:
  1. Consider adding product/service information pages
  2. Add clear contact information to improve user engagement
  3. Website has limited content - consider expanding

📁 Full report saved to: website_analysis_report.json

✨ Analysis complete!
```

## Analysis Features

### Topic Extraction
- Identifies main themes across pages
- Tracks topic distribution
- Highlights content gaps

### Sentiment Analysis
- Evaluates overall tone
- Page-by-page sentiment
- Aggregated sentiment distribution

### Readability Scoring
- Calculates readability metrics
- Identifies complex content
- Provides improvement suggestions

### Content Coverage
- Checks for essential pages
- Identifies missing information
- Suggests improvements

## Report Structure

```json
{
  "report_title": "Website Analysis Report",
  "crawl_summary": {
    "base_url": "https://example.com",
    "pages_crawled": 10,
    "success": true
  },
  "content_insights": {
    "total_pages": 10,
    "total_words": 2543,
    "avg_readability": 75.3,
    "main_topics": ["products", "company", "technology"],
    "sentiment_distribution": {
      "positive": 7,
      "neutral": 2,
      "negative": 1
    }
  },
  "page_details": [...],
  "recommendations": [...]
}
```

## Use Cases

- **SEO Analysis**: Content coverage and structure
- **Competitor Analysis**: Understanding competitor websites
- **Content Audits**: Identifying content gaps
- **Website Migration**: Pre-migration content inventory
- **Quality Assurance**: Automated content checking

## Customization

### Adjust Crawl Parameters

```python
shared = {
    "base_url": "https://example.com",
    "max_pages": 50,      # Crawl more pages
    "crawl_depth": 3      # Go deeper
}
```

### Add Custom Analysis

```python
# In analyze_content.py
def custom_analysis(content):
    # Add your analysis logic
    return results
```

### Extend Recommendations

```python
# In GenerateReportNode
def _generate_recommendations(self, insights, pages):
    # Add domain-specific recommendations
    if "ecommerce" in insights["main_topics"]:
        recommendations.append("Add product reviews section")
```

## Best Practices

1. **Respect robots.txt**: Check crawling permissions
2. **Rate Limiting**: Don't overwhelm servers
3. **Error Handling**: Gracefully handle failures
4. **Caching**: Cache results for repeated analysis
5. **Scalability**: Use batch processing for large sites

## Dependencies

The example uses mock implementations. For production:
- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `robots`: robots.txt parsing
- Optional: `scrapy` for advanced crawling