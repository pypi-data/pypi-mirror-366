"""
Web crawler tool integration example using KayGraph.

Demonstrates crawling a website, analyzing content, and generating reports
using external tools integrated with KayGraph nodes.
"""

import json
import logging
from typing import List, Dict, Any
from kaygraph import Node, Graph, BatchNode
from utils.web_crawler import crawl_website
from utils.analyze_content import analyze_page_content, aggregate_analyses

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class CrawlWebsiteNode(Node):
    """Crawl a website and extract content."""
    
    def prep(self, shared):
        """Get crawl parameters."""
        return {
            "base_url": shared.get("base_url", "https://example.com"),
            "max_pages": shared.get("max_pages", 10),
            "crawl_depth": shared.get("crawl_depth", 2)
        }
    
    def exec(self, params):
        """Execute web crawling."""
        base_url = params["base_url"]
        max_pages = params["max_pages"]
        
        self.logger.info(f"Starting crawl of {base_url} (max {max_pages} pages)")
        
        # Use the web crawler tool
        try:
            pages = crawl_website(base_url, max_pages)
            
            self.logger.info(f"Successfully crawled {len(pages)} pages")
            
            return {
                "success": True,
                "pages_crawled": len(pages),
                "pages": pages,
                "base_url": base_url
            }
        
        except Exception as e:
            self.logger.error(f"Crawl failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "pages_crawled": 0,
                "pages": []
            }
    
    def post(self, shared, prep_res, exec_res):
        """Store crawl results."""
        shared["crawl_results"] = exec_res
        
        if exec_res["success"]:
            print(f"\n✅ Crawl Complete!")
            print(f"  - Base URL: {exec_res['base_url']}")
            print(f"  - Pages crawled: {exec_res['pages_crawled']}")
            return "analyze"
        else:
            print(f"\n❌ Crawl Failed: {exec_res['error']}")
            return "failed"


class AnalyzeContentBatchNode(BatchNode):
    """Analyze crawled pages using batch processing."""
    
    def prep(self, shared):
        """Get pages to analyze."""
        crawl_results = shared.get("crawl_results", {})
        pages = crawl_results.get("pages", [])
        
        if not pages:
            self.logger.warning("No pages to analyze")
            return []
        
        self.logger.info(f"Preparing to analyze {len(pages)} pages")
        return pages
    
    def exec(self, page):
        """Analyze a single page."""
        self.logger.info(f"Analyzing: {page['title']}")
        
        # Use content analysis tool
        analysis = analyze_page_content(page)
        
        return analysis
    
    def post(self, shared, prep_res, exec_res):
        """Store analysis results."""
        shared["analyzed_pages"] = exec_res
        
        # Aggregate insights
        aggregated = aggregate_analyses(exec_res)
        shared["aggregated_insights"] = aggregated
        
        print(f"\n📊 Content Analysis Complete!")
        print(f"  - Pages analyzed: {len(exec_res)}")
        print(f"  - Total words: {aggregated.get('total_words', 0):,}")
        print(f"  - Main topics: {', '.join(aggregated.get('main_topics', []))}")
        
        return "report"


class GenerateReportNode(Node):
    """Generate final report from analysis."""
    
    def prep(self, shared):
        """Gather all analysis data."""
        return {
            "crawl_results": shared.get("crawl_results", {}),
            "analyzed_pages": shared.get("analyzed_pages", []),
            "aggregated_insights": shared.get("aggregated_insights", {})
        }
    
    def exec(self, data):
        """Generate comprehensive report."""
        crawl_results = data["crawl_results"]
        analyzed_pages = data["analyzed_pages"]
        insights = data["aggregated_insights"]
        
        report = {
            "report_title": "Website Analysis Report",
            "crawl_summary": {
                "base_url": crawl_results.get("base_url"),
                "pages_crawled": crawl_results.get("pages_crawled"),
                "success": crawl_results.get("success")
            },
            "content_insights": insights,
            "page_details": [],
            "recommendations": []
        }
        
        # Add page summaries
        for page in analyzed_pages[:5]:  # Top 5 pages
            page_summary = {
                "url": page["url"],
                "title": page["title"],
                "topics": page["topics"],
                "sentiment": page["sentiment"],
                "readability": page["readability_score"],
                "summary": page["summary"]
            }
            report["page_details"].append(page_summary)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(insights, analyzed_pages)
        report["recommendations"] = recommendations
        
        return report
    
    def _generate_recommendations(self, insights: Dict, pages: List[Dict]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Content recommendations
        if insights.get("avg_readability", 0) < 60:
            recommendations.append("Consider simplifying content for better readability")
        
        if not insights.get("content_coverage", {}).get("has_contact_details"):
            recommendations.append("Add clear contact information to improve user engagement")
        
        if not insights.get("content_coverage", {}).get("has_product_info"):
            recommendations.append("Consider adding product/service information pages")
        
        # Sentiment recommendations
        sentiment_dist = insights.get("sentiment_distribution", {})
        if sentiment_dist.get("negative", 0) > sentiment_dist.get("positive", 0):
            recommendations.append("Review content tone - consider more positive messaging")
        
        # Structure recommendations
        if insights.get("avg_words_per_page", 0) > 1000:
            recommendations.append("Consider breaking up long pages for better user experience")
        
        if insights.get("total_pages", 0) < 5:
            recommendations.append("Website has limited content - consider expanding")
        
        return recommendations
    
    def post(self, shared, prep_res, exec_res):
        """Save and display report."""
        shared["final_report"] = exec_res
        
        # Save report to file
        with open("website_analysis_report.json", "w") as f:
            json.dump(exec_res, f, indent=2)
        
        # Display report
        print("\n" + "=" * 60)
        print("📄 WEBSITE ANALYSIS REPORT")
        print("=" * 60)
        
        print(f"\n🌐 Crawl Summary:")
        print(f"  - URL: {exec_res['crawl_summary']['base_url']}")
        print(f"  - Pages: {exec_res['crawl_summary']['pages_crawled']}")
        
        insights = exec_res["content_insights"]
        print(f"\n📊 Content Insights:")
        print(f"  - Total words: {insights.get('total_words', 0):,}")
        print(f"  - Avg readability: {insights.get('avg_readability', 0)}/100")
        print(f"  - Main topics: {', '.join(insights.get('main_topics', []))}")
        
        sentiment = insights.get("sentiment_distribution", {})
        print(f"  - Sentiment: Positive({sentiment.get('positive', 0)}) "
              f"Neutral({sentiment.get('neutral', 0)}) "
              f"Negative({sentiment.get('negative', 0)})")
        
        print(f"\n📋 Top Pages:")
        for i, page in enumerate(exec_res["page_details"][:3], 1):
            print(f"  {i}. {page['title']}")
            print(f"     - Topics: {', '.join(page['topics'])}")
            print(f"     - Readability: {page['readability']}/100")
        
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(exec_res["recommendations"], 1):
            print(f"  {i}. {rec}")
        
        print(f"\n📁 Full report saved to: website_analysis_report.json")
        
        return None


class ErrorHandlerNode(Node):
    """Handle crawl failures gracefully."""
    
    def prep(self, shared):
        """Get error information."""
        return shared.get("crawl_results", {})
    
    def exec(self, error_data):
        """Process error."""
        return {
            "error_handled": True,
            "message": f"Crawl failed: {error_data.get('error', 'Unknown error')}",
            "suggestion": "Please check the URL and try again"
        }
    
    def post(self, shared, prep_res, exec_res):
        """Display error message."""
        print(f"\n⚠️  {exec_res['message']}")
        print(f"💡 {exec_res['suggestion']}")
        return None


def create_crawler_graph():
    """Create the web crawler analysis graph."""
    # Create nodes
    crawler = CrawlWebsiteNode(node_id="crawler")
    analyzer = AnalyzeContentBatchNode(node_id="analyzer")
    reporter = GenerateReportNode(node_id="reporter")
    error_handler = ErrorHandlerNode(node_id="error_handler")
    
    # Connect nodes
    crawler >> ("analyze", analyzer)
    crawler >> ("failed", error_handler)
    analyzer >> ("report", reporter)
    
    return Graph(start=crawler)


def main():
    """Run the web crawler example."""
    print("🕷️  KayGraph Web Crawler Tool Integration")
    print("=" * 60)
    print("This example demonstrates integrating a web crawler")
    print("with KayGraph for website analysis.\n")
    
    # Get URL from user or use default
    import sys
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter URL to crawl (default: https://example.com): ").strip()
        if not url:
            url = "https://example.com"
    
    # Create graph
    graph = create_crawler_graph()
    
    # Shared context
    shared = {
        "base_url": url,
        "max_pages": 10,
        "crawl_depth": 2
    }
    
    print(f"\nStarting crawl of {url}...")
    print(f"Settings: max_pages={shared['max_pages']}, depth={shared['crawl_depth']}\n")
    
    # Run the analysis
    graph.run(shared)
    
    print("\n✨ Analysis complete!")


if __name__ == "__main__":
    main()