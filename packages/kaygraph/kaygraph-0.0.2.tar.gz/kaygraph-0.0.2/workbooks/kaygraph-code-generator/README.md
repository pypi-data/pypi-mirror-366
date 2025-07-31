# KayGraph Code Generator

Demonstrates AI-powered code generation from natural language descriptions using KayGraph for building development tools.

## What it does

This example shows how to:
- **Requirements Parsing**: Extract specifications from descriptions
- **Architecture Design**: Plan code structure and components
- **Code Generation**: Create functional code implementations
- **Code Validation**: Check syntax and logic correctness
- **Error Correction**: Fix compilation and runtime errors
- **Code Refactoring**: Apply best practices and optimizations
- **Documentation**: Generate comprehensive documentation

## Features

- Mock code parser with requirement extraction
- Template-based code generation
- Multi-language support (Python, JavaScript, etc.)
- Syntax validation and error detection
- Automatic error correction
- Code optimization and refactoring
- Documentation generation

## How to run

```bash
python main.py
```

## Architecture

```
ParseRequirementsNode → DesignArchitectureNode → GenerateCodeNode → ValidateCodeNode → RefactorCodeNode → DocumentCodeNode
                                                                           ↓ (invalid)
                                                                        FixCodeNode ←┘
```

### Node Descriptions

1. **ParseRequirementsNode**: Analyzes natural language to extract functional requirements
2. **DesignArchitectureNode**: Creates high-level design and component structure
3. **GenerateCodeNode**: Produces initial code implementation
4. **ValidateCodeNode**: Checks for syntax errors and logic issues
5. **FixCodeNode**: Corrects identified problems
6. **RefactorCodeNode**: Improves code quality and performance
7. **DocumentCodeNode**: Adds documentation and comments

## Example Requests

### Basic Functions
```
"Create a function to calculate fibonacci numbers"
→ Generates optimized fibonacci function with memoization

"Write a class for managing a todo list"
→ Creates TodoList class with add, remove, complete methods

"Build a REST API endpoint for user authentication"
→ Generates Flask/FastAPI endpoint with JWT auth
```

### Complex Applications
```
"Create a web scraper for news articles"
→ Generates complete scraper with:
  - URL fetching
  - HTML parsing
  - Data extraction
  - Error handling
  - Rate limiting

"Build a data pipeline for CSV processing"
→ Creates pipeline with:
  - File reading
  - Data validation
  - Transformation
  - Output generation
  - Progress tracking
```

## Code Templates

### Python Function Template
```python
def {function_name}({parameters}):
    """
    {description}
    
    Args:
        {param_docs}
    
    Returns:
        {return_docs}
    """
    {implementation}
```

### JavaScript Class Template
```javascript
class {ClassName} {
    constructor({parameters}) {
        {initialization}
    }
    
    {methods}
}
```

### API Endpoint Template
```python
@app.route('/{endpoint}', methods=['{method}'])
def {handler_name}():
    """Handle {description}."""
    {validation}
    {business_logic}
    return {response}
```

## Code Patterns

### 1. Algorithm Implementation
- Sorting algorithms
- Search algorithms
- Dynamic programming
- Graph algorithms
- Mathematical computations

### 2. Data Structures
- Custom collections
- Tree structures
- Graph implementations
- Cache systems
- Queue managers

### 3. Web Development
- REST APIs
- WebSocket handlers
- Authentication systems
- Database models
- Frontend components

### 4. Utility Functions
- File processors
- Data validators
- Format converters
- Helper utilities
- CLI tools

## Validation Features

1. **Syntax Checking**
   - Language-specific syntax validation
   - Import verification
   - Variable scope checking

2. **Logic Validation**
   - Function return type checking
   - Error handling verification
   - Edge case detection

3. **Best Practices**
   - Code style compliance
   - Security vulnerability detection
   - Performance anti-patterns

## Refactoring Capabilities

### 1. Code Optimization
```python
# Before
def sum_list(lst):
    total = 0
    for item in lst:
        total = total + item
    return total

# After
def sum_list(lst):
    """Calculate sum of list elements."""
    return sum(lst)
```

### 2. Design Patterns
```python
# Apply singleton pattern
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 3. Error Handling
```python
# Add comprehensive error handling
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    return handle_error(e)
except Exception as e:
    logger.exception("Unexpected error")
    raise
```

## Multi-Language Support

### Python
- Functions, classes, decorators
- Async/await support
- Type hints
- Context managers

### JavaScript
- ES6+ features
- Promise/async patterns
- React components
- Node.js modules

### TypeScript
- Interface definitions
- Generic types
- Decorators
- Namespaces

### Go
- Struct definitions
- Interface implementations
- Goroutines
- Error handling

## Documentation Generation

### 1. Docstrings
- Parameter descriptions
- Return value documentation
- Usage examples
- Raises documentation

### 2. Type Annotations
```python
def process_data(
    input_file: str,
    output_format: Literal["json", "csv", "xml"] = "json",
    validate: bool = True
) -> Dict[str, Any]:
    """Process data file and return results."""
```

### 3. README Generation
- Installation instructions
- Usage examples
- API documentation
- Contributing guidelines

## Advanced Features

### 1. Test Generation
```python
def test_fibonacci():
    """Test fibonacci function."""
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(10) == 55
    with pytest.raises(ValueError):
        fibonacci(-1)
```

### 2. Dependency Injection
```python
class Service:
    def __init__(self, database: Database, cache: Cache):
        self.database = database
        self.cache = cache
```

### 3. Configuration Management
```python
@dataclass
class Config:
    api_key: str
    timeout: int = 30
    retry_count: int = 3
    
    @classmethod
    def from_env(cls) -> 'Config':
        return cls(
            api_key=os.getenv('API_KEY'),
            timeout=int(os.getenv('TIMEOUT', 30))
        )
```

## Use Cases

- **Rapid Prototyping**: Quick proof of concepts
- **Boilerplate Generation**: Standard code templates
- **Learning Tool**: Understanding code patterns
- **Productivity**: Accelerate development
- **Code Migration**: Convert between languages

## Best Practices

1. **Clear Requirements**: Provide specific descriptions
2. **Iterative Refinement**: Review and refine generated code
3. **Testing**: Always test generated code
4. **Security Review**: Check for vulnerabilities
5. **Performance Testing**: Validate efficiency

## Integration Examples

### With IDEs
```python
# VS Code extension integration
def generate_code_snippet(description: str) -> str:
    """Generate code from description."""
    graph = create_code_generator_graph()
    result = graph.run({"description": description})
    return result["generated_code"]
```

### With CI/CD
```yaml
# GitHub Actions workflow
- name: Generate boilerplate
  run: |
    python generate_code.py --template api --output src/
    python validate_code.py src/
```

## Performance Tips

1. **Cache Templates**: Reuse common patterns
2. **Incremental Generation**: Build code step by step
3. **Parallel Validation**: Check multiple files concurrently
4. **Smart Refactoring**: Only refactor changed sections
5. **Lazy Documentation**: Generate docs on demand

## Dependencies

This example uses mock implementations. For production:
- `black`: Python code formatting
- `pylint`: Code quality checking
- `jedi`: Code completion and analysis
- `jinja2`: Template engine