# KayGraph Nested Batch - Hierarchical Processing

Demonstrates nested batch processing for hierarchical data structures. This example processes student grades at three levels: School → Classes → Students.

## What it does

This example shows:
- **Nested BatchGraph**: Multiple levels of batch processing
- **Hierarchical Aggregation**: Results bubble up through levels
- **Parameter Cascading**: Data flows down through nested batches
- **Progressive Summarization**: Each level aggregates its children

## Features

- Three-level hierarchy: School, Class, Student
- Automatic grade calculation and letter grade assignment
- Statistical aggregation at each level
- Grade distribution analysis
- Performance metrics for top classes

## How to run

```bash
python main.py
```

## Architecture

```
SchoolBatchGraph
    └── ClassBatchGraph (for each class)
            └── StudentGradeGraph (for each student)
                    └── CalculateStudentGradeNode
```

### Processing Flow

1. **School Level**: Iterates over all classes
2. **Class Level**: Iterates over all students in class
3. **Student Level**: Calculates individual grades
4. **Aggregation**: Results flow back up the hierarchy

## Nested Batch Pattern

```python
# Level 1: School processes classes
class SchoolBatchGraph(BatchGraph):
    def __init__(self):
        # Use ClassBatchGraph as base
        base_graph = Graph(start=ClassBatchGraph())
        super().__init__(base_graph)

# Level 2: Class processes students  
class ClassBatchGraph(BatchGraph):
    def __init__(self):
        # Use student graph as base
        base_graph = create_student_grade_graph()
        super().__init__(base_graph)

# Level 3: Individual student processing
def create_student_grade_graph():
    return Graph(start=CalculateStudentGradeNode())
```

## Example Output

```
🎓 KayGraph Nested Batch Processing - School Grades
============================================================
This example demonstrates hierarchical batch processing:
School → Classes → Students

Generated sample data for: KayGraph Academy
  - Classes: 8
  - Total Students: 203

[INFO] Processing school: KayGraph Academy with 8 classes
[INFO] Processing class: Mathematics 101 with 25 students
[INFO] Calculating grade for student: STU00001
[INFO] Calculating grade for student: STU00002
...

📚 Class: Mathematics 101 (Teacher: Mr. Smith)
   Students: 25
   Class Average: 82.45
   Grade Distribution: A:5 B:8 C:7 D:3 F:2

📚 Class: Science 101 (Teacher: Ms. Johnson)
   Students: 28
   Class Average: 85.12
   Grade Distribution: A:7 B:10 C:6 D:4 F:1
...

🏫 SCHOOL REPORT: KayGraph Academy
============================================================
Total Classes: 8
Total Students: 203
School Average: 83.67

📊 School-wide Grade Distribution:
   A: 45 students (22.2%)
   B: 68 students (33.5%)
   C: 52 students (25.6%)
   D: 28 students (13.8%)
   F: 10 students (4.9%)

🏆 Top 3 Classes:
   1. Physics 101 - Average: 87.23
   2. Chemistry 101 - Average: 86.45
   3. Science 101 - Average: 85.12

⏱️  Total processing time: 1.23 seconds
📄 Detailed report saved to: school_report.json

🔄 Nested Batch Processing Benefits:
  - Natural hierarchy: Mirrors real-world structure
  - Isolated processing: Each level has its own context
  - Progressive aggregation: Results bubble up through levels
  - Parallelizable: Each level can be processed concurrently
```

## Data Structure

```json
{
  "school_name": "KayGraph Academy",
  "classes": [
    {
      "class_name": "Mathematics 101",
      "teacher": "Mr. Smith",
      "students": [
        {
          "student_id": "STU00001",
          "name": "Alice Anderson",
          "assignments": [
            {"assignment_id": "A1", "score": 85},
            {"assignment_id": "A2", "score": 92}
          ]
        }
      ]
    }
  ]
}
```

## Use Cases

- **Educational Systems**: Grade processing, report cards
- **Organizational Hierarchies**: Department → Team → Employee metrics
- **Geographic Data**: Country → State → City statistics
- **Product Catalogs**: Category → Subcategory → Product analysis
- **Financial Reports**: Company → Division → Department budgets

## Benefits of Nested Batch Processing

1. **Natural Modeling**: Reflects real-world hierarchical structures
2. **Isolation**: Each level maintains its own processing context
3. **Reusability**: Base graphs can be reused at different levels
4. **Scalability**: Can handle deep hierarchies efficiently
5. **Parallelization**: Each level can process items concurrently

## Customization

### Adding More Levels

```python
# Add District level above School
class DistrictBatchGraph(BatchGraph):
    def __init__(self):
        base_graph = Graph(start=SchoolBatchGraph())
        super().__init__(base_graph)
```

### Custom Aggregation

```python
# In post() method, implement custom logic
def post(self, shared, prep_res, exec_res):
    # Custom statistical analysis
    median_grade = statistics.median(grades)
    std_deviation = statistics.stdev(grades)
    # Add to summary
```

## Performance Considerations

- Each level adds overhead
- Consider flattening if hierarchy is shallow
- Use parallel processing for large datasets
- Cache intermediate results when possible