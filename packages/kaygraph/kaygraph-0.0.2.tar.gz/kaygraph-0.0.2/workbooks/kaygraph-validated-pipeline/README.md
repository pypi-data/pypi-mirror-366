# KayGraph Validated Pipeline

This example demonstrates KayGraph's ValidatedNode for building robust data pipelines with strict input/output validation. It showcases how proper validation prevents bad data propagation and ensures data quality throughout the pipeline.

## Features Demonstrated

1. **ValidatedNode Usage**: Input and output validation at each pipeline stage
2. **Schema Validation**: Type checking and data structure validation
3. **Error Prevention**: Stop bad data early before expensive operations
4. **Custom Validators**: Domain-specific validation rules
5. **Validation Metrics**: Track validation failures and patterns

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   DataLoader    │────▶│  DataCleaner     │────▶│ DataTransformer │
│ (ValidatedNode) │     │ (ValidatedNode)  │     │ (ValidatedNode) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                         │
         ▼                       ▼                         ▼
    [Schema Check]         [Quality Check]         [Business Rules]
                                                           │
                          ┌──────────────────┐             │
                          │  DataAggregator  │◀────────────┘
                          │ (ValidatedNode)  │
                          └──────────────────┘
                                   │
                                   ▼
                            [Final Validation]
```

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run the example
python main.py

# Try with invalid data to see validation in action
python main.py --invalid-data
```

## Key Concepts

### ValidatedNode Benefits
- Fail fast on invalid inputs
- Ensure output quality before passing downstream
- Separate validation logic from business logic
- Reusable validation patterns

### Validation Patterns
- Schema validation (structure, types)
- Business rule validation (domain logic)
- Cross-field validation (relationships)
- Statistical validation (outliers, distributions)

## Example Validations

1. **Input Schema**: Ensures required fields exist with correct types
2. **Data Quality**: Checks for nulls, duplicates, invalid ranges
3. **Business Rules**: Validates against domain-specific constraints
4. **Output Contract**: Guarantees downstream nodes receive valid data