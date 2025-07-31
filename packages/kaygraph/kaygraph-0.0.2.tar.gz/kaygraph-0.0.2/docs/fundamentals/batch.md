---
layout: default
title: "Batch"
parent: "Fundamentals"
nav_order: 4
---

# Batch

**Batch** makes it easier to handle large inputs in one Node or **rerun** a Graph multiple times. Example use cases:
- **Chunk-based** processing (e.g., splitting large texts).
- **Iterative** processing over lists of input items (e.g., user queries, files, URLs).

## 1. BatchNode

A **BatchNode** extends `Node` but changes `prep()` and `exec()`:

- **`prep(shared)`**: returns an **iterable** (e.g., list, generator).
- **`exec(item)`**: called **once** per item in that iterable.
- **`post(shared, prep_res, exec_res_list)`**: after all items are processed, receives a **list** of results (`exec_res_list`) and returns an **Action**.


### Example: Summarize a Large File

```python
class MapSummaries(BatchNode):
    def prep(self, shared):
        # Suppose we have a big file; chunk it
        content = shared["data"]
        chunk_size = 10000
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
        return chunks

    def exec(self, chunk):
        prompt = f"Summarize this chunk in 10 words: {chunk}"
        summary = call_llm(prompt)
        return summary

    def post(self, shared, prep_res, exec_res_list):
        combined = "\n".join(exec_res_list)
        shared["summary"] = combined
        return "default"

map_summaries = MapSummaries()
graph = Graph(start=map_summaries)
graph.run(shared)
```

---

## 2. BatchGraph

A **BatchGraph** runs a **Graph** multiple times, each time with different `params`. Think of it as a loop that replays the Graph for each parameter set.

### Key Differences from BatchNode

**Important**: Unlike BatchNode, which processes items and modifies the shared store:

1. BatchGraph returns **parameters to pass to the child Graph**, not data to process
2. These parameters are accessed in child nodes via `self.params`, not from the shared store
3. Each child Graph runs independently with a different set of parameters
4. Child nodes can be regular Nodes, not BatchNodes (the batching happens at the Graph level)

### Example: Summarize Many Files

```python
class SummarizeAllFiles(BatchGraph):
    def prep(self, shared):
        # IMPORTANT: Return a list of param dictionaries (not data for processing)
        filenames = list(shared["data"].keys())  # e.g., ["file1.txt", "file2.txt", ...]
        return [{"filename": fn} for fn in filenames]

# Child node that accesses filename from params, not shared store
class LoadFile(Node):
    def prep(self, shared):
        # Access filename from params (not from shared)
        filename = self.params["filename"]  # Important! Use self.params, not shared
        return filename

    def exec(self, filename):
        with open(filename, 'r') as f:
            return f.read()

    def post(self, shared, prep_res, exec_res):
        # Store file content in shared
        shared["current_file_content"] = exec_res
        return "default"

# Summarize node that works on the currently loaded file
class Summarize(Node):
    def prep(self, shared):
        return shared["current_file_content"]

    def exec(self, content):
        prompt = f"Summarize this file in 50 words: {content}"
        return call_llm(prompt)

    def post(self, shared, prep_res, exec_res):
        # Store summary in shared, indexed by current filename
        filename = self.params["filename"]  # Again, using params
        if "summaries" not in shared:
            shared["summaries"] = {}
        shared["summaries"][filename] = exec_res
        return "default"

# Create a per-file graph
load_file = LoadFile()
summarize = Summarize()
load_file >> summarize
summarize_file_graph = Graph(start=load_file)

# Wrap in a BatchGraph to process all files
summarize_all_files = SummarizeAllFiles(start=summarize_file_graph)
summarize_all_files.run(shared)
```

### Under the Hood
1. `prep(shared)` in the BatchGraph returns a list of param dicts—e.g., `[{"filename": "file1.txt"}, {"filename": "file2.txt"}, ...]`.
2. The **BatchGraph** loops through each dict. For each one:
   - It merges the dict with the BatchGraph's own `params` (if any): `{**batch_graph.params, **dict_from_prep}`
   - It calls `graph.run(shared)` using the merged parameters
   - **IMPORTANT**: These parameters are passed to the child Graph's nodes via `self.params`, NOT via the shared store
3. This means the sub-Graph is run **repeatedly**, once for every param dict, with each node in the graph accessing the parameters via `self.params`.

---

## 3. Nested or Multi-Level Batches

You can nest a **BatchGraph** in another **BatchGraph**. For instance:
- **Outer** batch: returns a list of directory param dicts (e.g., `{"directory": "/pathA"}`, `{"directory": "/pathB"}`, ...).
- **Inner** batch: returning a list of per-file param dicts.

At each level, **BatchGraph** merges its own param dict with the parent’s. By the time you reach the **innermost** node, the final `params` is the merged result of **all** parents in the chain. This way, a nested structure can keep track of the entire context (e.g., directory + file name) at once.

```python

class FileBatchGraph(BatchGraph):
    def prep(self, shared):
        # Access directory from params (set by parent)
        directory = self.params["directory"]
        # e.g., files = ["file1.txt", "file2.txt", ...]
        files = [f for f in os.listdir(directory) if f.endswith(".txt")]
        return [{"filename": f} for f in files]

class DirectoryBatchGraph(BatchGraph):
    def prep(self, shared):
        directories = [ "/path/to/dirA", "/path/to/dirB"]
        return [{"directory": d} for d in directories]

# The actual processing node
class ProcessFile(Node):
    def prep(self, shared):
        # Access both directory and filename from params
        directory = self.params["directory"]  # From outer batch
        filename = self.params["filename"]    # From inner batch
        full_path = os.path.join(directory, filename)
        return full_path

    def exec(self, full_path):
        # Process the file...
        return f"Processed {full_path}"

    def post(self, shared, prep_res, exec_res):
        # Store results, perhaps indexed by path
        if "results" not in shared:
            shared["results"] = {}
        shared["results"][prep_res] = exec_res
        return "default"

# Set up the nested batch structure
process_node = ProcessFile()
inner_graph = FileBatchGraph(start=process_node)
outer_graph = DirectoryBatchGraph(start=inner_graph)

# Run it
outer_graph.run(shared)
```
