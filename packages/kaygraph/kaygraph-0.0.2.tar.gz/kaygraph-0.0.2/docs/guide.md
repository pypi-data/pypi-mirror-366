---
layout: default
title: "Agentic Coding"
---

# Agentic Coding: Humans Design, Agents code!

> If you are an AI agent involved in building LLM Systems, read this guide **VERY, VERY** carefully! This is the most important chapter in the entire document. Throughout development, you should always (1) start with a small and simple solution, (2) design at a high level (`docs/design.md`) before implementation, and (3) frequently ask humans for feedback and clarification.
{: .warning }

## Agentic Coding Steps

Agentic Coding should be a collaboration between Human System Design and Agent Implementation:

| Steps                  | Human      | AI        | Comment                                                                 |
|:-----------------------|:----------:|:---------:|:------------------------------------------------------------------------|
| 1. Requirements | ★★★ High  | ★☆☆ Low   | Humans understand the requirements and context.                    |
| 2. Graph          | ★★☆ Medium | ★★☆ Medium |  Humans specify the high-level design, and the AI fills in the details. |
| 3. Utilities   | ★★☆ Medium | ★★☆ Medium | Humans provide available external APIs and integrations, and the AI helps with implementation. |
| 4. Node          | ★☆☆ Low   | ★★★ High  | The AI helps design the node types and data handling based on the graph.          |
| 5. Implementation      | ★☆☆ Low   | ★★★ High  |  The AI implements the graph based on the design. |
| 6. Optimization        | ★★☆ Medium | ★★☆ Medium | Humans evaluate the results, and the AI helps optimize. |
| 7. Reliability         | ★☆☆ Low   | ★★★ High  |  The AI writes test cases and addresses corner cases.     |

1. **Requirements**: Clarify the requirements for your project, and evaluate whether an AI system is a good fit.
    - Understand AI systems' strengths and limitations:
      - **Good for**: Routine tasks requiring common sense (filling forms, replying to emails)
      - **Good for**: Creative tasks with well-defined inputs (building slides, writing SQL)
      - **Not good for**: Ambiguous problems requiring complex decision-making (business strategy, startup planning)
    - **Keep It User-Centric:** Explain the "problem" from the user's perspective rather than just listing features.
    - **Balance complexity vs. impact**: Aim to deliver the highest value features with minimal complexity early.

2. **Graph Design**: Outline at a high level, describe how your AI system orchestrates nodes.
    - Identify applicable design patterns (e.g., [Map Reduce](./patterns/mapreduce.md), [Agent](./patterns/agent.md), [RAG](./patterns/rag.md)).
      - For each node in the graph, start with a high-level one-line description of what it does.
      - If using **Map Reduce**, specify how to map (what to split) and how to reduce (how to combine).
      - If using **Agent**, specify what are the inputs (context) and what are the possible actions.
      - If using **RAG**, specify what to embed, noting that there's usually both offline (indexing) and online (retrieval) graphs.
    - Outline the graph and draw it in a mermaid diagram. For example:
      ```mermaid
      graph LR
          start[Start] --> batch[Batch]
          batch --> check[Check]
          check -->|OK| process
          check -->|Error| fix[Fix]
          fix --> check

          subgraph process[Process]
            step1[Step 1] --> step2[Step 2]
          end

          process --> endNode[End]
      ```
    - > **If Humans can't specify the graph, AI Agents can't automate it!** Before building an LLM system, thoroughly understand the problem and potential solution by manually solving example inputs to develop intuition.
      {: .best-practice }

3. **Utilities**: Based on the Graph Design, identify and implement necessary utility functions.
    - Think of your AI system as the brain. It needs a body—these *external utility functions*—to interact with the real world:


        - Reading inputs (e.g., retrieving Slack messages, reading emails)
        - Writing outputs (e.g., generating reports, sending emails)
        - Using external tools (e.g., calling LLMs, searching the web)
        - **NOTE**: *LLM-based tasks* (e.g., summarizing text, analyzing sentiment) are **NOT** utility functions; rather, they are *core functions* internal in the AI system.
    - For each utility function, implement it and write a simple test.
    - Document their input/output, as well as why they are necessary. For example:
      - `name`: `get_embedding` (`utils/get_embedding.py`)
      - `input`: `str`
      - `output`: a vector of 3072 floats
      - `necessity`: Used by the second node to embed text
    - Example utility implementation:
      ```python
      # utils/call_llm.py
      from openai import OpenAI

      def call_llm(prompt):
          client = OpenAI(api_key="YOUR_API_KEY_HERE")
          r = client.chat.completions.create(
              model="gpt-4o",
              messages=[{"role": "user", "content": prompt}]
          )
          return r.choices[0].message.content

      if __name__ == "__main__":
          prompt = "What is the meaning of life?"
          print(call_llm(prompt))
      ```
    - > **Sometimes, design Utilities before Graph:**  For example, for an LLM project to automate a legacy system, the bottleneck will likely be the available interface to that system. Start by designing the hardest utilities for interfacing, and then build the graph around them.
      {: .best-practice }

4. **Node Design**: Plan how each node will read and write data, and use utility functions.
   - One core design principle for KayGraph is to use a [shared store](./fundamentals/communication.md), so start with a shared store design:
      - For simple systems, use an in-memory dictionary.
      - For more complex systems or when persistence is required, use a database.
      - **Don't Repeat Yourself**: Use in-memory references or foreign keys.
      - Example shared store design:
        ```python
        shared = {
            "user": {
                "id": "user123",
                "context": {                # Another nested dict
                    "weather": {"temp": 72, "condition": "sunny"},
                    "location": "San Francisco"
                }
            },
            "results": {}                   # Empty dict to store outputs
        }
        ```
   - For each [Node](./fundamentals/node.md), describe its type, how it reads and writes data, and which utility function it uses. Keep it specific but high-level without codes. For example:
     - `type`: Regular (or Batch, or Async)
     - `prep`: Read "text" from the shared store
     - `exec`: Call the embedding utility function
     - `post`: Write "embedding" to the shared store

5. **Implementation**: Implement the initial nodes and graphs based on the design.
   - 🎉 If you've reached this step, humans have finished the design. Now *Agentic Coding* begins!
   - **"Keep it simple, stupid!"** Start with basic features and add complexity gradually.
   - **FAIL FAST**! Use KayGraph's built-in error handling to quickly identify weak points.
   - **Use Built-in Features**: KayGraph provides logging, parameter validation, and error handling out of the box.
   - **Setup Logging**: Configure logging early to facilitate debugging:
     ```python
     import logging
     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
     ```

7. **Optimization**:
   - **Use Intuition**: For a quick initial evaluation, human intuition is often a good start.
   - **Redesign Graph (Back to Step 3)**: Consider breaking down tasks further, introducing agentic decisions, or better managing input contexts.
   - If your graph design is already solid, move on to micro-optimizations:
     - **Prompt Engineering**: Use clear, specific instructions with examples to reduce ambiguity.
     - **In-Context Learning**: Provide robust examples for tasks that are difficult to specify with instructions alone.

   - > **You'll likely iterate a lot!** Expect to repeat Steps 3–6 hundreds of times.
     >
     >

     {: .best-practice }

8. **Reliability**
   - **Node Retries**: Use the built-in `max_retries` and `wait` parameters in Node constructor for fault tolerance.
   - **Parameter Validation**: Use `ValidatedNode` for input/output validation with custom validation logic.
   - **Performance Monitoring**: Use `MetricsNode` to collect execution statistics and identify bottlenecks.
   - **Error Handling**: Implement custom `on_error` hooks for graceful error recovery.
   - **Resource Management**: Use context managers for automatic resource cleanup.
   - **Logging and Visualization**: KayGraph provides comprehensive logging with node IDs and execution context.
   - **Self-Evaluation**: Add a separate node (powered by an LLM) to review outputs when results are uncertain.

## Example LLM Project File Structure

```
my_project/
├── main.py
├── nodes.py
├── graph.py
├── utils/
│   ├── __init__.py
│   ├── call_llm.py
│   └── search_web.py
├── requirements.txt
└── docs/
    └── design.md
```

- **`docs/design.md`**: Contains project documentation for each step above. This should be *high-level* and *no-code*.
- **`utils/`**: Contains all utility functions.
  - It's recommended to dedicate one Python file to each API call, for example `call_llm.py` or `search_web.py`.
  - Each file should also include a `main()` function to try that API call
- **`nodes.py`**: Contains all the node definitions.
  ```python
  # nodes.py
  from kaygraph import Node, ValidatedNode, MetricsNode
  from utils.call_llm import call_llm

  class GetQuestionNode(Node):
      def __init__(self):
          super().__init__(node_id="question_input")

      def exec(self, _):
          # Get question directly from user input
          user_question = input("Enter your question: ")
          return user_question

      def post(self, shared, prep_res, exec_res):
          # Store the user's question
          shared["question"] = exec_res
          return "default"  # Go to the next node

  class AnswerNode(ValidatedNode):
      def __init__(self):
          super().__init__(max_retries=3, wait=1, node_id="llm_answer")

      def validate_input(self, question):
          if not question or not isinstance(question, str):
              raise ValueError("Question must be a non-empty string")
          return question.strip()

      def prep(self, shared):
          # Read question from shared
          return shared["question"]

      def exec(self, question):
          # Call LLM to get the answer
          return call_llm(question)

      def validate_output(self, answer):
          if not answer or len(answer.strip()) < 10:
              raise ValueError("Answer too short or empty")
          return answer

      def post(self, shared, prep_res, exec_res):
          # Store the answer in shared
          shared["answer"] = exec_res

      def on_error(self, shared, error):
          # Log error and provide fallback
          self.logger.error(f"LLM call failed: {error}")
          shared["answer"] = "I apologize, but I encountered an error processing your question."
          return True  # Suppress the error
  ```
- **`graph.py`**: Implements functions that create graphs by importing node definitions and connecting them.
  ```python
  # graph.py
  from kaygraph import Graph
  from nodes import GetQuestionNode, AnswerNode

  def create_qa_graph():
      """Create and return a question-answering graph."""
      # Create nodes
      get_question_node = GetQuestionNode()
      answer_node = AnswerNode()

      # Connect nodes in sequence
      get_question_node >> answer_node

      # Create graph starting with input node
      return Graph(start=get_question_node)
  ```
- **`main.py`**: Serves as the project's entry point.
  ```python
  # main.py
  import logging
  from graph import create_qa_graph

  # Configure logging
  logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

  # Example main function
  # Please replace this with your own main function
  def main():
      shared = {
          "question": None,  # Will be populated by GetQuestionNode from user input
          "answer": None     # Will be populated by AnswerNode
      }

      # Create the graph and run it
      qa_graph = create_qa_graph()

      # Use context manager for resource management
      with qa_graph:
          qa_graph.run(shared)

      print(f"Question: {shared['question']}")
      print(f"Answer: {shared['answer']}")

  if __name__ == "__main__":
      main()
  ```
