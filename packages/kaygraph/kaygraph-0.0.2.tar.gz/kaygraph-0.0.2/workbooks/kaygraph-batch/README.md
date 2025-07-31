# KayGraph Batch Processing

Basic batch processing example that translates a README file into multiple languages sequentially using KayGraph's BatchNode.

## What it does

This example demonstrates:
- **BatchNode Usage**: Process a list of items through the same logic
- **Sequential Processing**: Each translation happens one after another
- **Automatic Retry**: Built-in retry mechanism for failed items
- **Result Aggregation**: Collect and summarize all batch results

## Features

- Translates content into 10 different languages
- Saves each translation to a separate file
- Creates a summary with statistics
- Shows processing time for performance comparison

## How to run

```bash
python main.py
```

## Output

The example creates:
- `translations/` directory with translated files
- `translations/README_<language>.md` for each language
- `translations/translation_summary.json` with statistics

## Architecture

```
TranslationBatchNode
    ├── prep() → Create list of (content, language) tuples
    ├── exec() → Translate each item individually
    └── post() → Save translations and create summary
```

## Batch Processing Concepts

1. **Preparation Phase**: Create an iterable of items to process
2. **Execution Phase**: Process each item independently
3. **Post-processing Phase**: Aggregate results and perform cleanup

## Example Output

```
🌐 KayGraph Batch Translation Example
==================================================
Translating README into 10 languages...
This demonstrates sequential batch processing.

[INFO] Prepared 10 translation tasks
[INFO] Translating to Spanish...
[INFO] Saved Spanish translation to translations/readme_spanish.md
[INFO] Translating to French...
[INFO] Saved French translation to translations/readme_french.md
...

✅ Translation Summary:
  - Languages: Spanish, French, German, Italian, Portuguese, Japanese, Korean, Chinese, Russian, Arabic
  - Total translations: 10
  - Output directory: translations/

⏱️  Processing time: 5.23 seconds
📊 Average time per translation: 0.52 seconds

💡 Note: For faster processing, see kaygraph-parallel-batch example!
```

## Performance

Sequential batch processing is simple but can be slow for I/O-bound tasks like API calls. For better performance with concurrent processing, see the `kaygraph-parallel-batch` example.

## Use Cases

- File format conversions
- Data transformations
- API batch operations
- Report generation
- Multi-language content generation