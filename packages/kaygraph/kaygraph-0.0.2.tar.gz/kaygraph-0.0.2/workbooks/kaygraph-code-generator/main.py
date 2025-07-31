"""
Code generation example using KayGraph.

Demonstrates generating code from natural language descriptions
with validation, refactoring, and documentation.
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


class ParseRequirementsNode(Node):
    """Parse natural language requirements to extract specifications."""
    
    def prep(self, shared):
        """Get the code description."""
        return shared.get("description", "")
    
    def exec(self, description):
        """Parse requirements from description."""
        if not description:
            return {"error": "No description provided"}
        
        self.logger.info(f"Parsing requirements: '{description}'")
        
        from utils.code_parser import RequirementsParser
        parser = RequirementsParser()
        
        try:
            requirements = parser.parse(description)
            self.logger.info(f"Identified type: {requirements['type']}")
            self.logger.info(f"Language: {requirements['language']}")
            
            return requirements
            
        except Exception as e:
            self.logger.error(f"Failed to parse requirements: {e}")
            return {"error": str(e)}
    
    def post(self, shared, prep_res, exec_res):
        """Store parsed requirements."""
        if "error" in exec_res:
            print(f"\n❌ Failed to parse requirements: {exec_res['error']}")
            return None
        
        shared["requirements"] = exec_res
        
        print(f"\n📋 Requirements Analysis:")
        print(f"  Type: {exec_res['type']}")
        print(f"  Name: {exec_res.get('name', 'N/A')}")
        print(f"  Language: {exec_res['language']}")
        
        if exec_res.get('parameters'):
            print(f"  Parameters: {', '.join(exec_res['parameters'])}")
        
        if exec_res.get('features'):
            print(f"  Features: {', '.join(exec_res['features'])}")
        
        return "design"


class DesignArchitectureNode(Node):
    """Design code architecture based on requirements."""
    
    def prep(self, shared):
        """Get parsed requirements."""
        return shared.get("requirements", {})
    
    def exec(self, requirements):
        """Design the code architecture."""
        from utils.code_templates import ArchitectureDesigner
        designer = ArchitectureDesigner()
        
        try:
            design = designer.design(requirements)
            self.logger.info(f"Created design with {len(design['components'])} components")
            
            return design
            
        except Exception as e:
            self.logger.error(f"Failed to design architecture: {e}")
            return {"error": str(e)}
    
    def post(self, shared, prep_res, exec_res):
        """Store architecture design."""
        if "error" in exec_res:
            print(f"\n❌ Failed to design architecture: {exec_res['error']}")
            return None
        
        shared["design"] = exec_res
        
        print(f"\n🏗️ Architecture Design:")
        print(f"  Pattern: {exec_res.get('pattern', 'standard')}")
        print(f"  Components: {len(exec_res['components'])}")
        
        for comp in exec_res['components']:
            print(f"    - {comp['name']}: {comp['type']}")
        
        return "generate"


class GenerateCodeNode(Node):
    """Generate code based on requirements and design."""
    
    def prep(self, shared):
        """Get requirements and design."""
        return {
            "requirements": shared.get("requirements", {}),
            "design": shared.get("design", {}),
            "previous_error": shared.get("code_error")
        }
    
    def exec(self, data):
        """Generate the code."""
        from utils.code_templates import CodeGenerator
        generator = CodeGenerator()
        
        try:
            # Generate code considering any previous errors
            if data["previous_error"]:
                self.logger.info(f"Regenerating after error: {data['previous_error']}")
            
            code = generator.generate(
                data["requirements"],
                data["design"],
                previous_error=data["previous_error"]
            )
            
            return {
                "code": code["code"],
                "language": code["language"],
                "imports": code.get("imports", []),
                "metadata": code.get("metadata", {})
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate code: {e}")
            return {"error": str(e)}
    
    def post(self, shared, prep_res, exec_res):
        """Store generated code."""
        if "error" in exec_res:
            print(f"\n❌ Failed to generate code: {exec_res['error']}")
            return None
        
        shared["generated_code"] = exec_res
        shared["code_error"] = None  # Clear any previous error
        
        print(f"\n💻 Generated Code ({exec_res['language']}):")
        print("-" * 60)
        print(exec_res["code"])
        print("-" * 60)
        
        return "validate"


class ValidateCodeNode(Node):
    """Validate generated code for syntax and logic errors."""
    
    def prep(self, shared):
        """Get code to validate."""
        return shared.get("generated_code", {})
    
    def exec(self, data):
        """Validate the code."""
        if not data.get("code"):
            return {"valid": False, "errors": ["No code provided"]}
        
        from utils.code_validator import CodeValidator
        validator = CodeValidator(language=data.get("language", "python"))
        
        # Perform validation
        validation_result = validator.validate(data["code"])
        
        self.logger.info(f"Validation result: {validation_result['valid']}")
        if not validation_result["valid"]:
            self.logger.warning(f"Validation errors: {validation_result['errors']}")
        
        return validation_result
    
    def post(self, shared, prep_res, exec_res):
        """Handle validation results."""
        shared["validation_result"] = exec_res
        
        if exec_res["valid"]:
            print(f"\n✅ Code Validation Passed")
            if exec_res.get("warnings"):
                print(f"  ⚠️ Warnings:")
                for warning in exec_res["warnings"]:
                    print(f"    - {warning}")
            return "refactor"
        else:
            print(f"\n❌ Code Validation Failed:")
            for error in exec_res["errors"]:
                print(f"  - {error}")
            
            # Store error for correction
            shared["code_error"] = exec_res["errors"][0]
            return "fix"


class FixCodeNode(Node):
    """Attempt to fix code errors."""
    
    def prep(self, shared):
        """Get code and validation errors."""
        return {
            "code": shared.get("generated_code", {}).get("code"),
            "errors": shared.get("validation_result", {}).get("errors", []),
            "language": shared.get("generated_code", {}).get("language", "python"),
            "attempt": shared.get("fix_attempts", 0)
        }
    
    def exec(self, data):
        """Attempt to fix the code."""
        if data["attempt"] >= 3:
            return {"fixed": False, "reason": "Max fix attempts reached"}
        
        from utils.code_validator import CodeFixer
        fixer = CodeFixer(language=data["language"])
        
        # Try to fix the code
        fix_result = fixer.fix(data["code"], data["errors"])
        
        if fix_result["fixed"]:
            self.logger.info(f"Code fixed: {fix_result['fix_description']}")
        else:
            self.logger.warning(f"Could not fix code: {fix_result['reason']}")
        
        return fix_result
    
    def post(self, shared, prep_res, exec_res):
        """Handle fix results."""
        shared["fix_attempts"] = prep_res["attempt"] + 1
        
        if exec_res["fixed"]:
            print(f"\n🔧 Code Fixed:")
            print(f"  Fix: {exec_res.get('fix_description', 'N/A')}")
            
            # Update generated code
            shared["generated_code"]["code"] = exec_res["code"]
            return "validate"
        else:
            print(f"\n❌ Could not fix code: {exec_res['reason']}")
            return None


class RefactorCodeNode(Node):
    """Refactor code for better quality and performance."""
    
    def prep(self, shared):
        """Get validated code."""
        return {
            "code": shared.get("generated_code", {}),
            "requirements": shared.get("requirements", {})
        }
    
    def exec(self, data):
        """Refactor the code."""
        from utils.code_formatter import CodeRefactorer
        refactorer = CodeRefactorer(language=data["code"].get("language", "python"))
        
        # Apply refactoring
        refactored = refactorer.refactor(
            data["code"]["code"],
            style_guide="pep8" if data["code"]["language"] == "python" else "standard"
        )
        
        return {
            "code": refactored["code"],
            "improvements": refactored["improvements"],
            "metrics": refactored.get("metrics", {})
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store refactored code."""
        shared["refactored_code"] = exec_res
        
        print(f"\n♻️ Code Refactored:")
        if exec_res["improvements"]:
            print(f"  Improvements:")
            for improvement in exec_res["improvements"]:
                print(f"    - {improvement}")
        
        if exec_res.get("metrics"):
            print(f"  Metrics:")
            for metric, value in exec_res["metrics"].items():
                print(f"    - {metric}: {value}")
        
        # Update code
        shared["generated_code"]["code"] = exec_res["code"]
        
        return "document"


class DocumentCodeNode(Node):
    """Add documentation to the code."""
    
    def prep(self, shared):
        """Get final code and requirements."""
        return {
            "code": shared.get("generated_code", {}),
            "requirements": shared.get("requirements", {}),
            "design": shared.get("design", {})
        }
    
    def exec(self, data):
        """Add documentation to code."""
        from utils.code_formatter import CodeDocumenter
        documenter = CodeDocumenter(language=data["code"].get("language", "python"))
        
        # Generate documentation
        documented = documenter.document(
            data["code"]["code"],
            data["requirements"],
            data["design"]
        )
        
        return {
            "code": documented["code"],
            "readme": documented.get("readme", ""),
            "api_docs": documented.get("api_docs", "")
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store final documented code."""
        shared["final_code"] = exec_res
        
        print(f"\n📚 Documentation Added")
        print(f"\n🎉 Final Code:")
        print("=" * 60)
        print(exec_res["code"])
        print("=" * 60)
        
        if exec_res.get("readme"):
            print(f"\n📄 README Generated ({len(exec_res['readme'])} chars)")
        
        # Save to file
        filename = f"generated_{shared.get('requirements', {}).get('name', 'code')}.py"
        with open(filename, 'w') as f:
            f.write(exec_res["code"])
        
        print(f"\n💾 Code saved to: {filename}")
        
        return None


def create_code_generator_graph():
    """Create the code generation workflow graph."""
    # Create nodes
    parse = ParseRequirementsNode(node_id="parse")
    design = DesignArchitectureNode(node_id="design")
    generate = GenerateCodeNode(node_id="generate")
    validate = ValidateCodeNode(node_id="validate")
    fix = FixCodeNode(node_id="fix")
    refactor = RefactorCodeNode(node_id="refactor")
    document = DocumentCodeNode(node_id="document")
    
    # Connect nodes
    parse - "design" >> design
    design - "generate" >> generate
    generate - "validate" >> validate
    validate - "refactor" >> refactor
    validate - "fix" >> fix
    fix - "validate" >> validate
    refactor - "document" >> document
    
    return Graph(start=parse)


def main():
    """Run the code generator example."""
    print("🚀 KayGraph Code Generator")
    print("=" * 60)
    print("Generate code from natural language descriptions.\n")
    
    # Example code generation requests
    requests = [
        # Basic functions
        "Create a function to calculate fibonacci numbers",
        "Write a class for managing a todo list with add, remove, and complete methods",
        
        # Complex implementations
        "Build a rate limiter class that limits API calls to 100 per minute",
        "Create a web scraper function that extracts article titles from a news website",
        
        # With errors to test fixing
        "Make a function that divides by zero",  # Will need fixing
        "Create a class with syntax error"       # Will need fixing
    ]
    
    # Create graph
    graph = create_code_generator_graph()
    
    # Process each request
    for i, description in enumerate(requests, 1):
        print(f"\n{'='*60}")
        print(f"Request {i}/{len(requests)}: \"{description}\"")
        print(f"{'='*60}")
        
        # Reset state
        shared_state = {
            "description": description,
            "fix_attempts": 0
        }
        
        # Run the workflow
        graph.run(shared_state)
        
        print(f"\n✨ Completed request {i}")
    
    print("\n🎊 Code generation example complete!")


if __name__ == "__main__":
    main()