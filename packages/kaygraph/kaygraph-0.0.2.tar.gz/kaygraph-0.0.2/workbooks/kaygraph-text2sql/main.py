"""
Text to SQL generation example using KayGraph.

Demonstrates converting natural language queries to SQL statements
with validation and execution.
"""

import sys
sys.path.insert(0, '../..')

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from kaygraph import Node, Graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class ParseQueryNode(Node):
    """Parse natural language query to extract intent and entities."""
    
    def prep(self, shared):
        """Get the natural language query."""
        return shared.get("query", "")
    
    def exec(self, query):
        """Parse the query to extract components."""
        if not query:
            return {"error": "No query provided"}
        
        self.logger.info(f"Parsing query: '{query}'")
        
        # Import parser utility
        from utils.sql_parser import NLQueryParser
        parser = NLQueryParser()
        
        try:
            parsed = parser.parse(query)
            self.logger.info(f"Parsed intent: {parsed['intent']}")
            self.logger.info(f"Entities: {parsed['entities']}")
            
            return parsed
            
        except Exception as e:
            self.logger.error(f"Failed to parse query: {e}")
            return {"error": str(e)}
    
    def post(self, shared, prep_res, exec_res):
        """Store parsed query components."""
        if "error" in exec_res:
            print(f"\n❌ Failed to parse query: {exec_res['error']}")
            return None
        
        shared["parsed_query"] = exec_res
        
        print(f"\n📝 Query Analysis:")
        print(f"  Intent: {exec_res['intent']}")
        print(f"  Main Entity: {exec_res['entities'].get('main', 'N/A')}")
        
        if exec_res.get('filters'):
            print(f"  Filters: {', '.join(f'{k}={v}' for k,v in exec_res['filters'].items())}")
        
        if exec_res.get('aggregation'):
            print(f"  Aggregation: {exec_res['aggregation']['type']}")
        
        return "analyze_schema"


class SchemaAnalysisNode(Node):
    """Analyze database schema to identify relevant tables and columns."""
    
    def prep(self, shared):
        """Get parsed query and database schema."""
        return {
            "parsed": shared.get("parsed_query", {}),
            "schema": shared.get("database_schema")
        }
    
    def exec(self, data):
        """Analyze schema for query requirements."""
        from utils.schema_analyzer import SchemaAnalyzer
        from utils.database import get_mock_schema
        
        # Get schema if not provided
        if not data["schema"]:
            data["schema"] = get_mock_schema()
        
        analyzer = SchemaAnalyzer(data["schema"])
        
        # Analyze what tables and columns are needed
        analysis = analyzer.analyze_for_query(data["parsed"])
        
        self.logger.info(f"Identified tables: {analysis['tables']}")
        self.logger.info(f"Identified columns: {analysis['columns']}")
        
        return analysis
    
    def post(self, shared, prep_res, exec_res):
        """Store schema analysis results."""
        shared["schema_analysis"] = exec_res
        shared["database_schema"] = prep_res["schema"]
        
        print(f"\n🗂️ Schema Analysis:")
        print(f"  Tables: {', '.join(exec_res['tables'])}")
        print(f"  Columns: {len(exec_res['columns'])} identified")
        
        if exec_res.get('joins'):
            print(f"  Joins needed: {len(exec_res['joins'])}")
        
        return "generate_sql"


class SQLGenerationNode(Node):
    """Generate SQL query from parsed components and schema."""
    
    def __init__(self, dialect: str = "sqlite", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dialect = dialect
    
    def prep(self, shared):
        """Get all necessary data for SQL generation."""
        return {
            "parsed": shared.get("parsed_query", {}),
            "schema": shared.get("schema_analysis", {}),
            "previous_error": shared.get("sql_error")
        }
    
    def exec(self, data):
        """Generate SQL query."""
        from utils.sql_generator import SQLGenerator
        
        generator = SQLGenerator(dialect=self.dialect)
        
        try:
            # Generate SQL considering any previous errors
            if data["previous_error"]:
                self.logger.info(f"Regenerating SQL after error: {data['previous_error']}")
            
            sql = generator.generate(
                data["parsed"],
                data["schema"],
                previous_error=data["previous_error"]
            )
            
            return {
                "sql": sql,
                "dialect": self.dialect,
                "parameterized": generator.is_parameterized(sql)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate SQL: {e}")
            return {"error": str(e)}
    
    def post(self, shared, prep_res, exec_res):
        """Store generated SQL."""
        if "error" in exec_res:
            print(f"\n❌ Failed to generate SQL: {exec_res['error']}")
            return None
        
        shared["generated_sql"] = exec_res
        shared["sql_error"] = None  # Clear any previous error
        
        print(f"\n💾 Generated SQL:")
        print(f"  {exec_res['sql']}")
        print(f"  Dialect: {exec_res['dialect']}")
        print(f"  Parameterized: {'Yes' if exec_res['parameterized'] else 'No'}")
        
        return "validate_sql"


class SQLValidationNode(Node):
    """Validate SQL query for syntax and security."""
    
    def prep(self, shared):
        """Get SQL to validate."""
        return shared.get("generated_sql", {})
    
    def exec(self, data):
        """Validate the SQL query."""
        if not data.get("sql"):
            return {"valid": False, "errors": ["No SQL provided"]}
        
        from utils.sql_generator import SQLValidator
        validator = SQLValidator()
        
        # Perform validation
        validation_result = validator.validate(data["sql"])
        
        self.logger.info(f"Validation result: {validation_result['valid']}")
        if not validation_result["valid"]:
            self.logger.warning(f"Validation errors: {validation_result['errors']}")
        
        return validation_result
    
    def post(self, shared, prep_res, exec_res):
        """Handle validation results."""
        shared["validation_result"] = exec_res
        
        if exec_res["valid"]:
            print(f"\n✅ SQL Validation Passed")
            if exec_res.get("warnings"):
                print(f"  ⚠️ Warnings: {', '.join(exec_res['warnings'])}")
            return "execute"
        else:
            print(f"\n❌ SQL Validation Failed:")
            for error in exec_res["errors"]:
                print(f"  - {error}")
            
            # Store error for correction
            shared["sql_error"] = exec_res["errors"][0]
            return "correct_sql"


class SQLCorrectionNode(Node):
    """Attempt to correct invalid SQL queries."""
    
    def prep(self, shared):
        """Get SQL and validation errors."""
        return {
            "sql": shared.get("generated_sql", {}).get("sql"),
            "errors": shared.get("validation_result", {}).get("errors", []),
            "attempt": shared.get("correction_attempts", 0)
        }
    
    def exec(self, data):
        """Attempt to correct the SQL."""
        if data["attempt"] >= 3:
            return {"corrected": False, "reason": "Max correction attempts reached"}
        
        from utils.sql_generator import SQLCorrector
        corrector = SQLCorrector()
        
        # Try to correct the SQL
        correction_result = corrector.correct(
            data["sql"],
            data["errors"]
        )
        
        if correction_result["corrected"]:
            self.logger.info(f"SQL corrected: {correction_result['sql']}")
        else:
            self.logger.warning(f"Could not correct SQL: {correction_result['reason']}")
        
        return correction_result
    
    def post(self, shared, prep_res, exec_res):
        """Handle correction results."""
        shared["correction_attempts"] = prep_res["attempt"] + 1
        
        if exec_res["corrected"]:
            print(f"\n🔧 SQL Corrected:")
            print(f"  {exec_res['sql']}")
            print(f"  Fix: {exec_res.get('fix_description', 'N/A')}")
            
            # Update generated SQL
            shared["generated_sql"]["sql"] = exec_res["sql"]
            return "validate_sql"
        else:
            print(f"\n❌ Could not correct SQL: {exec_res['reason']}")
            return None


class ExecuteQueryNode(Node):
    """Execute the validated SQL query."""
    
    def prep(self, shared):
        """Get SQL to execute."""
        return {
            "sql": shared.get("generated_sql", {}).get("sql"),
            "schema": shared.get("database_schema")
        }
    
    def exec(self, data):
        """Execute the SQL query against mock database."""
        if not data["sql"]:
            return {"error": "No SQL to execute"}
        
        from utils.database import MockDatabase
        
        # Create mock database with schema
        db = MockDatabase(data["schema"])
        
        try:
            # Execute query
            self.logger.info(f"Executing SQL: {data['sql']}")
            result = db.execute(data["sql"])
            
            return {
                "success": True,
                "rows": result["rows"],
                "columns": result["columns"],
                "row_count": len(result["rows"]),
                "execution_time": result.get("execution_time", 0.01)
            }
            
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def post(self, shared, prep_res, exec_res):
        """Store query results."""
        shared["query_result"] = exec_res
        
        if exec_res.get("success"):
            print(f"\n✅ Query Executed Successfully")
            print(f"  Rows returned: {exec_res['row_count']}")
            print(f"  Execution time: {exec_res['execution_time']:.3f}s")
            return "format_results"
        else:
            print(f"\n❌ Query execution failed: {exec_res.get('error', 'Unknown error')}")
            return None


class FormatResultsNode(Node):
    """Format query results for display."""
    
    def __init__(self, format_type: str = "table", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format_type = format_type
    
    def prep(self, shared):
        """Get query results to format."""
        return shared.get("query_result", {})
    
    def exec(self, data):
        """Format the results."""
        if not data.get("success"):
            return {"formatted": "No results to format"}
        
        from utils.sql_generator import ResultFormatter
        formatter = ResultFormatter()
        
        # Format results
        formatted = formatter.format(
            data["rows"],
            data["columns"],
            format_type=self.format_type
        )
        
        return {
            "formatted": formatted,
            "format_type": self.format_type,
            "row_count": data["row_count"]
        }
    
    def post(self, shared, prep_res, exec_res):
        """Display formatted results."""
        shared["formatted_result"] = exec_res
        
        print(f"\n📊 Query Results ({exec_res['format_type']}):")
        print("-" * 60)
        print(exec_res["formatted"])
        
        if exec_res["row_count"] == 0:
            print("\n(No rows returned)")
        
        return None


def create_text2sql_graph():
    """Create the text-to-SQL workflow graph."""
    # Create nodes
    parse = ParseQueryNode(node_id="parse")
    schema = SchemaAnalysisNode(node_id="schema")
    generate = SQLGenerationNode(dialect="sqlite", node_id="generate")
    validate = SQLValidationNode(node_id="validate")
    correct = SQLCorrectionNode(node_id="correct")
    execute = ExecuteQueryNode(node_id="execute")
    format_results = FormatResultsNode(format_type="table", node_id="format")
    
    # Connect nodes using - operator for named actions
    parse - "analyze_schema" >> schema
    schema - "generate_sql" >> generate
    generate - "validate_sql" >> validate
    validate - "execute" >> execute
    validate - "correct_sql" >> correct
    correct - "validate_sql" >> validate
    execute - "format_results" >> format_results
    
    return Graph(start=parse)


def main():
    """Run the text-to-SQL example."""
    print("🔍 KayGraph Text to SQL Generator")
    print("=" * 60)
    print("Convert natural language queries to SQL statements.\n")
    
    # Example queries to demonstrate
    queries = [
        # Basic queries
        "Show all customers",
        "Find products under $50",
        "Count orders by status",
        
        # Complex queries
        "Top 5 customers by total spending",
        "Products that have never been ordered",
        
        # Queries with errors (to test correction)
        "Select from nowhere",  # Invalid table
        "Show me the stuffs"    # Ambiguous query
    ]
    
    # Create graph
    graph = create_text2sql_graph()
    
    # Process each query
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}/{len(queries)}: \"{query}\"")
        print(f"{'='*60}")
        
        # Reset state
        shared_state = {
            "query": query,
            "correction_attempts": 0
        }
        
        # Run the workflow
        graph.run(shared_state)
        
        print(f"\n✨ Completed query {i}")
    
    print("\n🎉 Text-to-SQL example complete!")


if __name__ == "__main__":
    main()