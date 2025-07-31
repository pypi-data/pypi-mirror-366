# KayGraph Workbooks

Welcome to the KayGraph Workbooks! This collection demonstrates how to build sophisticated AI applications using the KayGraph framework. Each workbook is a complete, runnable example that showcases different patterns and capabilities.

## 📚 Available Workbooks

### Core Examples

#### 1. 👋 [Hello World](./kaygraph-hello-world/)
**Difficulty**: ⭐

The simplest KayGraph application:
- Basic node creation and connection
- Graph execution
- Shared state usage

```bash
cd kaygraph-hello-world
python main.py
```

#### 2. 📝 [Writing Workflow](./kaygraph-workflow/)
**Difficulty**: ⭐⭐

Multi-stage content creation pipeline:
- Topic validation
- Outline generation
- Content writing
- Style application

```bash
cd kaygraph-workflow
python main.py
```

#### 3. 📊 [Structured Output](./kaygraph-structured-output/)
**Difficulty**: ⭐⭐

Extract structured data from unstructured text:
- Resume parsing example
- Data validation
- Multiple output formats
- Information extraction

```bash
cd kaygraph-structured-output
python main.py
```

### Advanced Patterns

#### 4. 🧠 [Chain-of-Thought Reasoning](./kaygraph-thinking/)
**Difficulty**: ⭐⭐⭐

Implement structured reasoning for complex problem-solving:
- Hierarchical planning with status tracking
- Self-evaluation and error correction
- Step-by-step execution with plan updates
- Performance metrics via MetricsNode

```bash
cd kaygraph-thinking
python main.py "What is the expected value of rolling dice until getting 3,4,5?"
```

#### 5. 💬 [Interactive Chat](./kaygraph-chat/)
**Difficulty**: ⭐⭐

Build a conversational chatbot with memory:
- Conversation history management
- Graceful error handling with retries
- Custom system prompts for personalities
- Interactive command-line interface

```bash
cd kaygraph-chat
python main.py "You are a helpful pirate assistant"
```

#### 6. 🤖 [Autonomous Agent](./kaygraph-agent/)
**Difficulty**: ⭐⭐⭐

Create an agent that searches and answers questions:
- Query analysis and decision making
- Web search integration
- Result synthesis
- Conditional graph execution

```bash
cd kaygraph-agent
python main.py "What are the latest developments in quantum computing?"
```

### Production Patterns

#### 7. 📖 [RAG System](./kaygraph-rag/)
**Difficulty**: ⭐⭐⭐⭐

Build a complete Retrieval-Augmented Generation system:
- Document indexing pipeline
- Embedding generation and vector storage
- Semantic search
- Context-aware answer generation

```bash
cd kaygraph-rag
python main.py index data/
python main.py query "What is KayGraph?"
```

#### 8. 👥 [Multi-Agent Collaboration](./kaygraph-multi-agent/)
**Difficulty**: ⭐⭐⭐⭐⭐

Orchestrate multiple specialized agents:
- Supervisor coordination pattern
- Asynchronous message passing
- Shared workspace collaboration
- Complex task decomposition

```bash
cd kaygraph-multi-agent
python main.py "Write a blog post about renewable energy"
```

#### 9. ⚡ [Parallel Batch Processing](./kaygraph-parallel-batch/)
**Difficulty**: ⭐⭐⭐

Demonstrate parallel processing performance:
- Sequential vs parallel comparison
- Automatic batch sizing
- Progress tracking
- Performance metrics and speedup analysis

```bash
cd kaygraph-parallel-batch
python main.py benchmark
```

#### 10. 👨‍💼 [Supervisor Pattern](./kaygraph-supervisor/)
**Difficulty**: ⭐⭐⭐⭐

Manage unreliable worker agents:
- Task assignment and retry logic
- Worker performance tracking
- Result validation
- Smart worker selection

```bash
cd kaygraph-supervisor
python main.py
```

### Advanced Chat Features

#### 11. 🧠 [Chat with Memory](./kaygraph-chat-memory/)
**Difficulty**: ⭐⭐⭐⭐

Persistent chat with user profiles:
- Short-term conversation memory
- Long-term user profiles
- Topic tracking across sessions
- Personalized responses

```bash
cd kaygraph-chat-memory
python main.py
```

#### 12. 🛡️ [Chat with Guardrails](./kaygraph-chat-guardrail/)
**Difficulty**: ⭐⭐⭐

Topic-filtered chatbot (travel assistant):
- Content moderation
- Topic classification
- Polite redirects for off-topic queries
- Safety filters

```bash
cd kaygraph-chat-guardrail
python main.py
```

### Batch Processing

#### 13. 🔄 [Basic Batch Processing](./kaygraph-batch/)
**Difficulty**: ⭐⭐

Sequential batch processing:
- Translation to multiple languages
- Progress tracking
- Result aggregation
- Performance metrics

```bash
cd kaygraph-batch
python main.py
```

#### 14. 📊 [CSV Chunk Processing](./kaygraph-batch-node/)
**Difficulty**: ⭐⭐⭐

Process large files in chunks:
- Memory-efficient CSV processing
- Statistical aggregation
- Iterator-based batching
- Chunk-level error isolation

```bash
cd kaygraph-batch-node
python main.py
```

#### 15. 🖼️ [Batch Flow - Image Pipeline](./kaygraph-batch-flow/)
**Difficulty**: ⭐⭐⭐

Apply multiple filters to multiple images:
- BatchGraph wrapper pattern
- Parameter injection
- Cartesian product processing
- Metrics collection

```bash
cd kaygraph-batch-flow
python main.py
```

#### 16. 🎓 [Nested Batch - School Grades](./kaygraph-nested-batch/)
**Difficulty**: ⭐⭐⭐⭐

Hierarchical batch processing:
- Three-level nesting (School → Class → Student)
- Progressive aggregation
- Statistical analysis at each level
- Grade distribution reports

```bash
cd kaygraph-nested-batch
python main.py
```

### Tool Integrations

#### 17. 🕷️ [Web Crawler](./kaygraph-tool-crawler/)
**Difficulty**: ⭐⭐⭐

Web scraping with intelligent extraction:
- Multi-page crawling
- Content analysis
- Report generation
- Link following

```bash
cd kaygraph-tool-crawler
python main.py
```

#### 18. 🗄️ [Database Integration](./kaygraph-tool-database/)
**Difficulty**: ⭐⭐⭐

SQLite database operations:
- CRUD operations
- Transaction management
- History tracking
- Report generation

```bash
cd kaygraph-tool-database
python main.py
```

#### 19. 🔍 [Embeddings & Search](./kaygraph-tool-embeddings/)
**Difficulty**: ⭐⭐⭐

Text embeddings and similarity search:
- Multiple embedding methods
- Vector similarity search
- Clustering and analysis
- Visualization generation

```bash
cd kaygraph-tool-embeddings
python main.py
```

#### 20. 📄 [PDF & Vision Processing](./kaygraph-tool-pdf-vision/)
**Difficulty**: ⭐⭐⭐⭐

Document processing with OCR:
- PDF text extraction
- Table detection
- Form processing
- Multi-format support

```bash
cd kaygraph-tool-pdf-vision
python main.py
```

#### 21. 🔎 [Web Search Integration](./kaygraph-tool-search/)
**Difficulty**: ⭐⭐⭐

Search engine integration:
- Multi-source search
- Result aggregation
- Search synthesis
- Report generation

```bash
cd kaygraph-tool-search
python main.py
```

### Specialized Applications

#### 22. 🗃️ [Text to SQL](./kaygraph-text2sql/)
**Difficulty**: ⭐⭐⭐⭐

Natural language to SQL:
- Query parsing
- Schema awareness
- SQL generation & validation
- Error correction

```bash
cd kaygraph-text2sql
python main.py
```

#### 23. 💻 [Code Generator](./kaygraph-code-generator/)
**Difficulty**: ⭐⭐⭐⭐

AI-powered code generation:
- Requirement parsing
- Architecture design
- Code generation & validation
- Refactoring & documentation

```bash
cd kaygraph-code-generator
python main.py
```

## 🚀 Getting Started

### Prerequisites

1. Install KayGraph:
```bash
pip install kaygraph
```

2. Clone this repository:
```bash
git clone <repository-url>
cd workbooks
```

3. Install workbook dependencies:
```bash
cd <workbook-name>
pip install -r requirements.txt
```

### Running Workbooks

Each workbook includes:
- `main.py` - Entry point with examples
- `README.md` - Detailed documentation
- `design.md` - Architecture and design decisions
- `requirements.txt` - Dependencies

Most workbooks work with mock/demo data by default. To use real services:
1. Edit `utils/call_llm.py` for LLM integration
2. Edit `utils/search_web.py` for search APIs
3. Add your API keys as environment variables

## 📊 Workbook Comparison

| Workbook | Complexity | Async | Parallel | External APIs | Best For |
|----------|-----------|--------|----------|---------------|----------|
| Hello World | Low | ❌ | ❌ | None | Learning basics |
| Workflow | Low | ❌ | ❌ | LLM | Content creation |
| Structured Output | Low | ❌ | ❌ | LLM | Data extraction |
| Chat | Low | ❌ | ❌ | LLM | Basic interactions |
| Chat Memory | Medium | ❌ | ❌ | LLM | Persistent chat |
| Chat Guardrail | Medium | ❌ | ❌ | LLM | Safe chat |
| Agent | Medium | ❌ | ❌ | LLM, Search | Information retrieval |
| Thinking | Medium | ❌ | ❌ | LLM | Complex reasoning |
| Batch | Low | ❌ | ❌ | None | Sequential batch |
| Batch Node | Medium | ❌ | ❌ | None | Large file processing |
| Batch Flow | Medium | ❌ | ❌ | None | Pipeline batching |
| Nested Batch | High | ❌ | ❌ | None | Hierarchical data |
| RAG | High | ❌ | ✅ | LLM, Embeddings | Knowledge bases |
| Multi-Agent | Very High | ✅ | ✅ | LLM | Complex workflows |
| Parallel Batch | Medium | ✅ | ✅ | None | Performance demos |
| Supervisor | High | ❌ | ❌ | LLM | Worker management |

## 🏗️ Framework Features Demonstrated

### Core Concepts
- **Nodes**: Basic computation units (`Node`, `BaseNode`)
- **Graphs**: Workflow orchestration (`Graph`)
- **Shared State**: Data passing between nodes
- **Actions**: Conditional execution paths

### Advanced Features
- **Async Operations**: `AsyncNode`, `AsyncGraph`
- **Batch Processing**: `BatchNode`, `ParallelBatchNode`
- **Validation**: `ValidatedNode` with input/output checks
- **Metrics**: `MetricsNode` for performance tracking
- **Error Handling**: Retries, fallbacks, graceful degradation

### Design Patterns
- **Sequential Pipeline**: Step-by-step processing
- **Conditional Branching**: Dynamic path selection
- **Self-Loop**: Iterative refinement
- **Parallel Execution**: Concurrent processing
- **Message Passing**: Agent communication

## 🛠️ Creating Your Own Workbook

1. **Plan Your Application**
   - Define the problem and workflow
   - Identify node responsibilities
   - Design the graph structure

2. **Create Directory Structure**
   ```
   my-workbook/
   ├── main.py          # Entry point
   ├── nodes.py         # Node implementations
   ├── graph.py         # Graph construction
   ├── utils/           # Helper functions
   ├── design.md        # Architecture docs
   ├── README.md        # User documentation
   └── requirements.txt # Dependencies
   ```

3. **Implement Nodes**
   - Inherit from appropriate base class
   - Implement `prep()`, `exec()`, `post()`
   - Add error handling and logging

4. **Build Graph**
   - Connect nodes with actions
   - Configure parameters
   - Test execution flow

5. **Document Everything**
   - Clear README with examples
   - Design rationale
   - Performance considerations

## 📈 Performance Tips

1. **Choose the Right Node Type**
   - `Node` for simple operations
   - `BatchNode` for collections
   - `ParallelBatchNode` for I/O operations
   - `AsyncNode` for concurrent tasks

2. **Optimize Shared State**
   - Minimize data copying
   - Use references for large objects
   - Clear unused data

3. **Error Handling**
   - Use retries for transient failures
   - Implement fallbacks
   - Log errors comprehensively

4. **Monitoring**
   - Use MetricsNode for performance
   - Add logging at key points
   - Track execution paths

## 🤝 Contributing

We welcome contributions! To add a new workbook:

1. Follow the structure of existing workbooks
2. Ensure it demonstrates unique KayGraph features
3. Include comprehensive documentation
4. Add tests if applicable
5. Submit a pull request

## 📝 License

These workbooks are part of the KayGraph project and follow the same license terms.

## 🙏 Acknowledgments

These workbooks are inspired by various AI application patterns and real-world use cases. Special thanks to the KayGraph community for feedback and suggestions.

---

Happy building with KayGraph! 🚀