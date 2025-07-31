"""
Web search tool integration example using KayGraph.

Demonstrates integrating web search capabilities for information
retrieval and analysis workflows.
"""

import json
import logging
from typing import List, Dict, Any
from kaygraph import Node, Graph, BatchNode
from utils.search_tool import SearchEngine, SearchAggregator, SearchResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class SearchQueryNode(Node):
    """Perform web search based on query."""
    
    def __init__(self, search_type: str = "web", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_type = search_type
        self.engine = SearchEngine()
    
    def prep(self, shared):
        """Get search parameters."""
        return {
            "query": shared.get("search_query", ""),
            "num_results": shared.get("num_results", 10),
            "date_filter": shared.get("date_filter"),
            "language": shared.get("language", "en")
        }
    
    def exec(self, params):
        """Execute search."""
        if not params["query"]:
            return {"results": [], "error": "No search query provided"}
        
        self.logger.info(f"Searching for: '{params['query']}'")
        
        try:
            results = self.engine.search(
                query=params["query"],
                num_results=params["num_results"],
                search_type=self.search_type,
                language=params["language"],
                date_filter=params["date_filter"]
            )
            
            return {
                "results": results,
                "query": params["query"],
                "count": len(results),
                "search_type": self.search_type
            }
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return {
                "results": [],
                "query": params["query"],
                "error": str(e)
            }
    
    def post(self, shared, prep_res, exec_res):
        """Store search results."""
        shared["search_results"] = exec_res
        
        if exec_res.get("error"):
            print(f"\n❌ Search failed: {exec_res['error']}")
            return "error"
        
        print(f"\n🔍 Search Results for '{exec_res['query']}':")
        print(f"Found {exec_res['count']} results (type: {exec_res['search_type']})")
        print("-" * 60)
        
        for i, result in enumerate(exec_res["results"][:5], 1):
            print(f"\n{i}. {result.title}")
            print(f"   🔗 {result.url}")
            print(f"   📝 {result.snippet[:150]}...")
            print(f"   📊 Relevance: {result.relevance_score:.2f}")
        
        if exec_res["count"] > 5:
            print(f"\n... and {exec_res['count'] - 5} more results")
        
        return "analyze"


class MultiSourceSearchNode(Node):
    """Search across multiple sources."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aggregator = SearchAggregator()
    
    def prep(self, shared):
        """Get multi-source search parameters."""
        return {
            "query": shared.get("search_query", ""),
            "sources": shared.get("search_sources", ["web", "news"]),
            "results_per_source": shared.get("results_per_source", 5)
        }
    
    def exec(self, params):
        """Search multiple sources."""
        if not params["query"]:
            return {"results": {}, "error": "No search query provided"}
        
        self.logger.info(f"Multi-source search for: '{params['query']}'")
        self.logger.info(f"Sources: {params['sources']}")
        
        try:
            results = self.aggregator.multi_search(
                query=params["query"],
                sources=params["sources"],
                num_results_per_source=params["results_per_source"]
            )
            
            # Get insights
            insights = self.aggregator.get_insights(results)
            
            return {
                "results": results,
                "insights": insights,
                "query": params["query"]
            }
            
        except Exception as e:
            self.logger.error(f"Multi-source search failed: {e}")
            return {
                "results": {},
                "error": str(e)
            }
    
    def post(self, shared, prep_res, exec_res):
        """Store multi-source results."""
        shared["multi_source_results"] = exec_res.get("results", {})
        shared["search_insights"] = exec_res.get("insights", {})
        
        if exec_res.get("error"):
            print(f"\n❌ Multi-source search failed: {exec_res['error']}")
            return "error"
        
        print(f"\n🔍 Multi-Source Search Results:")
        print("=" * 60)
        
        for source, results in exec_res["results"].items():
            print(f"\n📌 {source.upper()} ({len(results)} results):")
            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. {result.title}")
                print(f"     {result.snippet[:100]}...")
        
        # Show insights
        insights = exec_res["insights"]
        print(f"\n📊 Search Insights:")
        print(f"  - Total results: {insights['total_results']}")
        print(f"  - Sources searched: {', '.join(insights['sources'])}")
        
        if insights.get("top_domains"):
            print(f"\n  Top domains:")
            for domain, count in insights["top_domains"][:3]:
                print(f"    • {domain}: {count} results")
        
        if insights.get("common_terms"):
            print(f"\n  Common terms:")
            terms = [term for term, _ in insights["common_terms"][:5]]
            print(f"    {', '.join(terms)}")
        
        return "default"


class AnalyzeResultsNode(Node):
    """Analyze search results for patterns and insights."""
    
    def prep(self, shared):
        """Get results to analyze."""
        return {
            "search_results": shared.get("search_results", {}),
            "multi_source_results": shared.get("multi_source_results", {}),
            "insights": shared.get("search_insights", {})
        }
    
    def exec(self, data):
        """Analyze search results."""
        analysis = {
            "summary": {},
            "patterns": [],
            "recommendations": [],
            "key_findings": []
        }
        
        # Analyze single source results
        if data["search_results"].get("results"):
            results = data["search_results"]["results"]
            
            # Content analysis
            analysis["summary"]["single_source"] = {
                "query": data["search_results"]["query"],
                "result_count": len(results),
                "avg_relevance": sum(r.relevance_score for r in results) / len(results),
                "top_result": results[0].title if results else None
            }
            
            # Identify patterns
            if all(r.relevance_score > 0.8 for r in results[:3]):
                analysis["patterns"].append("High relevance - query matches well with available content")
            
            if any("tutorial" in r.title.lower() or "guide" in r.title.lower() for r in results):
                analysis["patterns"].append("Educational content available")
        
        # Analyze multi-source results
        if data["multi_source_results"]:
            total_results = sum(len(r) for r in data["multi_source_results"].values())
            
            analysis["summary"]["multi_source"] = {
                "total_results": total_results,
                "sources": list(data["multi_source_results"].keys()),
                "insights": data["insights"]
            }
            
            # Key findings from insights
            if data["insights"].get("date_distribution"):
                dist = data["insights"]["date_distribution"]
                if dist.get("today", 0) + dist.get("week", 0) > total_results * 0.5:
                    analysis["key_findings"].append("Majority of results are recent (within a week)")
            
            if data["insights"].get("relevance_stats"):
                stats = data["insights"]["relevance_stats"]
                if stats["avg"] > 0.7:
                    analysis["key_findings"].append("High average relevance across sources")
        
        # Generate recommendations
        if analysis["summary"].get("single_source", {}).get("avg_relevance", 0) < 0.5:
            analysis["recommendations"].append("Consider refining search query for better results")
        
        if "academic" in data.get("multi_source_results", {}):
            analysis["recommendations"].append("Academic sources available - good for in-depth research")
        
        return analysis
    
    def post(self, shared, prep_res, exec_res):
        """Store and display analysis."""
        shared["search_analysis"] = exec_res
        
        print(f"\n🧠 Search Analysis:")
        print("=" * 60)
        
        # Show summary
        if exec_res["summary"].get("single_source"):
            summary = exec_res["summary"]["single_source"]
            print(f"\nSingle Source Summary:")
            print(f"  Query: '{summary['query']}'")
            print(f"  Results: {summary['result_count']}")
            print(f"  Avg relevance: {summary['avg_relevance']:.2f}")
        
        # Show patterns
        if exec_res["patterns"]:
            print(f"\n🔍 Patterns Identified:")
            for pattern in exec_res["patterns"]:
                print(f"  • {pattern}")
        
        # Show key findings
        if exec_res["key_findings"]:
            print(f"\n💡 Key Findings:")
            for finding in exec_res["key_findings"]:
                print(f"  • {finding}")
        
        # Show recommendations
        if exec_res["recommendations"]:
            print(f"\n📝 Recommendations:")
            for rec in exec_res["recommendations"]:
                print(f"  • {rec}")
        
        return "default"


class SearchSynthesisNode(Node):
    """Synthesize information from search results."""
    
    def prep(self, shared):
        """Get all search data."""
        return {
            "query": shared.get("search_query", ""),
            "search_results": shared.get("search_results", {}),
            "multi_source": shared.get("multi_source_results", {}),
            "analysis": shared.get("search_analysis", {})
        }
    
    def exec(self, data):
        """Synthesize search findings."""
        synthesis = {
            "query": data["query"],
            "summary": "",
            "key_points": [],
            "sources_used": [],
            "confidence": 0.0
        }
        
        # Collect all results
        all_results = []
        
        if data["search_results"].get("results"):
            all_results.extend(data["search_results"]["results"])
            synthesis["sources_used"].append("web")
        
        for source, results in data["multi_source"].items():
            all_results.extend(results)
            if source not in synthesis["sources_used"]:
                synthesis["sources_used"].append(source)
        
        if not all_results:
            synthesis["summary"] = "No search results available for synthesis."
            return synthesis
        
        # Create summary based on top results
        top_results = sorted(all_results, key=lambda x: x.relevance_score, reverse=True)[:5]
        
        # Extract key points from top results
        for result in top_results:
            # Extract key sentences from snippets
            sentences = result.snippet.split('. ')
            if sentences:
                key_point = sentences[0] + '.'
                if len(key_point) > 20:  # Meaningful content
                    synthesis["key_points"].append({
                        "point": key_point,
                        "source": result.title,
                        "relevance": result.relevance_score
                    })
        
        # Generate summary
        synthesis["summary"] = f"Based on {len(all_results)} search results for '{data['query']}', " \
                              f"the most relevant information comes from {len(synthesis['sources_used'])} sources. "
        
        if synthesis["key_points"]:
            synthesis["summary"] += f"Key findings include insights on {data['query']} from various perspectives."
        
        # Calculate confidence
        if all_results:
            avg_relevance = sum(r.relevance_score for r in all_results) / len(all_results)
            synthesis["confidence"] = avg_relevance
        
        return synthesis
    
    def post(self, shared, prep_res, exec_res):
        """Store and display synthesis."""
        shared["search_synthesis"] = exec_res
        
        print(f"\n📝 Search Synthesis:")
        print("=" * 60)
        print(f"Query: '{exec_res['query']}'")
        print(f"Sources: {', '.join(exec_res['sources_used'])}")
        print(f"Confidence: {exec_res['confidence']:.2%}")
        
        print(f"\n📌 Summary:")
        print(exec_res["summary"])
        
        if exec_res["key_points"]:
            print(f"\n🔑 Key Points:")
            for i, point in enumerate(exec_res["key_points"][:5], 1):
                print(f"\n{i}. {point['point']}")
                print(f"   Source: {point['source']}")
                print(f"   Relevance: {point['relevance']:.2f}")
        
        return None


class SaveSearchReportNode(Node):
    """Save comprehensive search report."""
    
    def prep(self, shared):
        """Gather all search data."""
        return {
            "query": shared.get("search_query"),
            "results": shared.get("search_results"),
            "multi_source": shared.get("multi_source_results"),
            "insights": shared.get("search_insights"),
            "analysis": shared.get("search_analysis"),
            "synthesis": shared.get("search_synthesis")
        }
    
    def exec(self, data):
        """Create search report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "search_query": data["query"],
            "results_summary": {
                "single_source": {
                    "count": len(data["results"].get("results", [])) if data["results"] else 0,
                    "type": data["results"].get("search_type") if data["results"] else None
                },
                "multi_source": {
                    "sources": list(data["multi_source"].keys()) if data["multi_source"] else [],
                    "total_results": sum(len(r) for r in data["multi_source"].values()) if data["multi_source"] else 0
                }
            },
            "insights": data["insights"],
            "analysis": data["analysis"],
            "synthesis": data["synthesis"],
            "top_results": []
        }
        
        # Add top results
        all_results = []
        if data["results"] and data["results"].get("results"):
            all_results.extend(data["results"]["results"])
        
        for results in (data["multi_source"] or {}).values():
            all_results.extend(results)
        
        # Sort by relevance and take top 10
        top_results = sorted(all_results, key=lambda x: x.relevance_score, reverse=True)[:10]
        report["top_results"] = [r.to_dict() for r in top_results]
        
        return report
    
    def post(self, shared, prep_res, exec_res):
        """Save report to file."""
        report_path = "search_report.json"
        
        with open(report_path, 'w') as f:
            json.dump(exec_res, f, indent=2)
        
        print(f"\n💾 Search report saved to: {report_path}")
        print(f"   Contains {len(exec_res['top_results'])} top results")
        print(f"   Query: '{exec_res['search_query']}'")
        
        return None


def create_search_graph():
    """Create the search workflow graph."""
    # Create nodes
    single_search = SearchQueryNode(search_type="web", node_id="single_search")
    multi_search = MultiSourceSearchNode(node_id="multi_search")
    analyze = AnalyzeResultsNode(node_id="analyze")
    synthesize = SearchSynthesisNode(node_id="synthesize")
    save_report = SaveSearchReportNode(node_id="save_report")
    
    # Connect nodes
    single_search >> ("analyze", analyze)
    single_search >> ("error", multi_search)  # Try multi-source on error
    
    multi_search >> analyze
    analyze >> synthesize >> save_report
    
    return Graph(start=single_search)


def main():
    """Run the search tool integration example."""
    print("🔍 KayGraph Web Search Tool Integration")
    print("=" * 60)
    print("This example demonstrates web search integration")
    print("for information retrieval and analysis.\n")
    
    # Example queries to demonstrate
    queries = [
        {
            "search_query": "latest advances in quantum computing 2024",
            "num_results": 15,
            "search_sources": ["web", "news", "academic"],
            "date_filter": "month"
        },
        {
            "search_query": "Python async programming best practices",
            "num_results": 10,
            "search_sources": ["web", "news"],
            "results_per_source": 5
        }
    ]
    
    # Create graph
    graph = create_search_graph()
    
    # Run for each query
    for i, query_params in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}/{len(queries)}: {query_params['search_query']}")
        print(f"{'='*60}")
        
        # Run search workflow
        graph.run(query_params)
        
        print(f"\n✅ Completed search workflow for query {i}")
    
    print("\n✨ Search tool integration example complete!")


if __name__ == "__main__":
    main()