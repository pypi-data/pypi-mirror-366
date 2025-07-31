---
layout: default
title: "Home"
nav_order: 1
---

# KayGraph

An opinionated framework for building context-aware AI applications with production-ready graphs for *Agents, Task Decomposition, RAG, etc* with enterprise features.

- **Opinionated Context Graphs**: Build powerful AI systems with context-aware graphs that seamlessly integrate operations, LLM calls, and complex workflows.
- **Production-Ready**: Core graph abstraction with built-in logging, error handling, metrics, and resource management for enterprise deployments.
- **Expressive Design Patterns**: Everything you love from larger frameworks—([Multi-](./patterns/multi_agent.html))[Agents](./patterns/agent.html), [Workgraph](./patterns/graph.html), [RAG](./patterns/rag.html), and more.
- **Enterprise Features**: Parameter validation, execution hooks, context management, and comprehensive monitoring built-in.

<div align="center">

</div>


## Core Abstraction

We model the LLM graph as a **Graph + Shared Store**:

- [Node](./fundamentals/node.md) handles simple (LLM) tasks.
- [Graph](./fundamentals/graph.md) connects nodes through **Actions** (labeled edges).
- [Shared Store](./fundamentals/communication.md) enables communication between nodes within graphs.
- [Batch](./fundamentals/batch.md) nodes/graphs allow for data-intensive tasks.
- [Async](./fundamentals/async.md) nodes/graphs allow waiting for asynchronous tasks.
- [(Advanced) Parallel](./fundamentals/parallel.md) nodes/graphs handle I/O-bound tasks.

<div align="center">

</div>

## Design Pattern

From there, it's easy to implement popular design patterns:

- [Agent](./patterns/agent.md) autonomously makes decisions.
- [Workgraph](./patterns/graph.md) chains multiple tasks into pipelines.
- [RAG](./patterns/rag.md) integrates data retrieval with generation.
- [Map Reduce](./patterns/mapreduce.md) splits data tasks into Map and Reduce steps.
- [Structured Output](./patterns/structure.md) formats outputs consistently.
- [(Advanced) Multi-Agents](./patterns/multi_agent.md) coordinate multiple agents.

<div align="center">

</div>

## Utility Function

We **do not** provide built-in utilities. Instead, we offer *examples*—please *implement your own*:

- [LLM Wrapper](./integrations/llm.md)
- [Viz and Debug](./integrations/viz.md)
- [Web Search](./integrations/websearch.md)
- [Chunking](./integrations/chunking.md)
- [Embedding](./integrations/embedding.md)
- [Vector Databases](./integrations/vector.md)
- [Text-to-Speech](./integrations/text_to_speech.md)

**Why not built-in?**: I believe it's a *bad practice* for vendor-specific APIs in a general framework:
- *API Volatility*: Frequent changes lead to heavy maintenance for hardcoded APIs.
- *Flexibility*: You may want to switch vendors, use fine-tuned models, or run them locally.
- *Optimizations*: Prompt caching, batching, and streaming are easier without vendor lock-in.

## Ready to build your Apps?

Check out [Agentic Coding Guidance](./guide.md), the fastest way to develop LLM projects with KayGraph!
