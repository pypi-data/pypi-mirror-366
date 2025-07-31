# KayGraph Agent

This workbook demonstrates how to build an autonomous research agent using KayGraph that can analyze queries, search for information, and provide comprehensive answers.

## What it does

The agent:
- Analyzes user queries to understand information needs
- Decides autonomously whether to search the web
- Performs web searches when current information is needed
- Synthesizes search results into coherent answers
- Provides well-structured, informative responses

## How to run

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure utilities (in `utils/` folder):
   - `call_llm.py`: Add your LLM API integration
   - `search_web.py`: Add your web search API

3. Run with a query:
```bash
python main.py "What is the latest news about AI?"
```

4. Or run interactively:
```bash
python main.py
```

## How it works

### Graph Structure
```
QueryNode → ThinkNode → SearchNode → SynthesizeNode → AnswerNode
              ↓                                           ↑
              └───────────────────────────────────────────┘
                        (direct answer path)
```

### Key Components

1. **QueryNode** (ValidatedNode):
   - Validates and processes user input
   - Ensures query is not empty

2. **ThinkNode**:
   - Analyzes query to determine information needs
   - Decides whether web search is necessary
   - Routes to appropriate path

3. **SearchNode**:
   - Performs web search when needed
   - Handles search failures gracefully
   - Configurable result limit

4. **SynthesizeNode**:
   - Processes search results
   - Extracts key information
   - Creates coherent summary

5. **AnswerNode**:
   - Combines all available information
   - Generates comprehensive response
   - Provides context about sources

### Decision Logic

The agent decides to search when:
- Query asks for current events or news
- Recent information is likely needed
- Factual data might have changed
- Search would improve answer quality

### Features from KayGraph

- **ValidatedNode**: Input validation
- **Conditional routing**: Dynamic path selection
- **Retry mechanism**: Handles API failures
- **Comprehensive logging**: Full execution trace

## Example Queries

Try these to see different agent behaviors:

### Queries that trigger search:
- "What is the weather in Paris today?"
- "Latest developments in quantum computing"
- "Current stock price of Apple"
- "Who won the latest Nobel Prize?"

### Queries answered directly:
- "What is Python programming?"
- "Explain the theory of relativity"
- "How does photosynthesis work?"
- "What are the benefits of exercise?"

## Customization

### Enhance the Agent

1. **Add Tools**: Extend with calculator, code execution, etc.
2. **Memory**: Add conversation history for context
3. **Multi-step**: Allow agent to search multiple times
4. **Verification**: Add fact-checking nodes

### Configure Search

Edit `SearchNode` parameters:
```python
search_node = SearchNode(
    max_results=10,        # More results
    timeout=30,           # Longer timeout
    safe_search=True      # Content filtering
)
```

### Custom Analysis

Modify `ThinkNode` to add domain-specific logic:
- Technical queries → search documentation
- Math problems → skip search, use calculation
- Creative tasks → generate without search

## Performance Tips

1. **Cache Results**: Store search results to avoid repeated queries
2. **Parallel Search**: Use AsyncNode for multiple searches
3. **Result Ranking**: Implement relevance scoring
4. **Fallback Sources**: Try multiple search providers

## Example Output

```
🤖 Processing query: What is the latest AI news?

💭 Thought Process: This query asks for latest/current information about AI news, which requires web search.

🔍 Search performed: Yes
   Found 5 results

📝 Answer:
Based on recent search results, here are the latest developments in AI:

1. Major tech companies are advancing large language models...
2. New regulations for AI safety are being discussed...
3. Breakthrough in computer vision technology...

These developments show rapid progress in making AI more capable and accessible while addressing safety concerns.
```