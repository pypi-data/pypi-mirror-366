"""
Nested batch processing example using KayGraph.

Demonstrates hierarchical batch processing for calculating student grades
at multiple levels: School → Classes → Students.
"""

import os
import json
import logging
from typing import List, Dict, Any
from kaygraph import Node, Graph, BatchGraph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# Base level nodes - Process individual student

class CalculateStudentGradeNode(Node):
    """Calculate grade for a single student."""
    
    def prep(self, shared):
        """Get student data from parameters."""
        return self.params
    
    def exec(self, student_data):
        """Calculate student's final grade."""
        student_id = student_data.get("student_id")
        assignments = student_data.get("assignments", [])
        
        self.logger.info(f"Calculating grade for student: {student_id}")
        
        if not assignments:
            return {
                "student_id": student_id,
                "grade": 0,
                "letter_grade": "F",
                "assignment_count": 0
            }
        
        # Calculate average
        total_score = sum(a["score"] for a in assignments)
        avg_score = total_score / len(assignments)
        
        # Determine letter grade
        if avg_score >= 90:
            letter_grade = "A"
        elif avg_score >= 80:
            letter_grade = "B"
        elif avg_score >= 70:
            letter_grade = "C"
        elif avg_score >= 60:
            letter_grade = "D"
        else:
            letter_grade = "F"
        
        return {
            "student_id": student_id,
            "grade": round(avg_score, 2),
            "letter_grade": letter_grade,
            "assignment_count": len(assignments),
            "assignments": assignments
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store student grade."""
        shared["student_grade"] = exec_res
        return None


def create_student_grade_graph():
    """Create graph for processing a single student."""
    calculator = CalculateStudentGradeNode(node_id="grade_calculator")
    return Graph(start=calculator)


# Middle level - Process all students in a class

class ClassBatchGraph(BatchGraph):
    """Process all students in a class."""
    
    def __init__(self, *args, **kwargs):
        base_graph = create_student_grade_graph()
        super().__init__(base_graph, *args, **kwargs)
        
    def prep(self, shared):
        """Get all students in the class."""
        class_data = self.params
        class_name = class_data.get("class_name")
        students = class_data.get("students", [])
        
        self.logger.info(f"Processing class: {class_name} with {len(students)} students")
        
        # Create parameter set for each student
        param_sets = []
        for student in students:
            param_sets.append({
                "class_name": class_name,
                "student_id": student["student_id"],
                "student_name": student["name"],
                "assignments": student["assignments"]
            })
        
        return param_sets
    
    def post(self, shared, prep_res, exec_res):
        """Aggregate class results."""
        class_data = self.params
        class_name = class_data.get("class_name")
        
        # Extract student grades
        student_grades = []
        total_grade = 0
        grade_distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        
        for result in exec_res:
            grade_info = result.get("shared", {}).get("student_grade", {})
            if grade_info:
                student_grades.append(grade_info)
                total_grade += grade_info["grade"]
                grade_distribution[grade_info["letter_grade"]] += 1
        
        # Calculate class average
        class_average = total_grade / len(student_grades) if student_grades else 0
        
        class_summary = {
            "class_name": class_name,
            "teacher": class_data.get("teacher"),
            "student_count": len(student_grades),
            "class_average": round(class_average, 2),
            "grade_distribution": grade_distribution,
            "student_grades": student_grades
        }
        
        shared["class_summary"] = class_summary
        
        # Print class summary
        print(f"\n📚 Class: {class_name} (Teacher: {class_data.get('teacher')})")
        print(f"   Students: {len(student_grades)}")
        print(f"   Class Average: {class_average:.2f}")
        print(f"   Grade Distribution: A:{grade_distribution['A']} B:{grade_distribution['B']} "
              f"C:{grade_distribution['C']} D:{grade_distribution['D']} F:{grade_distribution['F']}")
        
        return class_summary


# Top level - Process all classes in a school

class SchoolBatchGraph(BatchGraph):
    """Process all classes in a school."""
    
    def __init__(self, *args, **kwargs):
        # Use ClassBatchGraph as the base graph
        base_graph = Graph(start=ClassBatchGraph(graph_id="class_processor"))
        super().__init__(base_graph, *args, **kwargs)
    
    def prep(self, shared):
        """Get all classes in the school."""
        school_data = shared.get("school_data", {})
        classes = school_data.get("classes", [])
        
        school_name = school_data.get("school_name", "Unknown School")
        self.logger.info(f"Processing school: {school_name} with {len(classes)} classes")
        
        # Each class becomes a parameter set
        return classes
    
    def post(self, shared, prep_res, exec_res):
        """Aggregate school-wide results."""
        school_data = shared.get("school_data", {})
        school_name = school_data.get("school_name", "Unknown School")
        
        # Extract class summaries
        class_summaries = []
        total_students = 0
        total_grade_sum = 0
        school_grade_distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        
        for result in exec_res:
            class_summary = result.get("shared", {}).get("class_summary", {})
            if class_summary:
                class_summaries.append(class_summary)
                total_students += class_summary["student_count"]
                total_grade_sum += class_summary["class_average"] * class_summary["student_count"]
                
                # Aggregate grade distribution
                for grade, count in class_summary["grade_distribution"].items():
                    school_grade_distribution[grade] += count
        
        # Calculate school average
        school_average = total_grade_sum / total_students if total_students > 0 else 0
        
        school_summary = {
            "school_name": school_name,
            "total_classes": len(class_summaries),
            "total_students": total_students,
            "school_average": round(school_average, 2),
            "grade_distribution": school_grade_distribution,
            "class_summaries": class_summaries
        }
        
        # Save detailed report
        with open("school_report.json", 'w') as f:
            json.dump(school_summary, f, indent=2)
        
        shared["school_summary"] = school_summary
        
        # Print school summary
        print(f"\n🏫 SCHOOL REPORT: {school_name}")
        print("=" * 60)
        print(f"Total Classes: {len(class_summaries)}")
        print(f"Total Students: {total_students}")
        print(f"School Average: {school_average:.2f}")
        print(f"\n📊 School-wide Grade Distribution:")
        for grade in ["A", "B", "C", "D", "F"]:
            count = school_grade_distribution[grade]
            percentage = (count / total_students * 100) if total_students > 0 else 0
            print(f"   {grade}: {count} students ({percentage:.1f}%)")
        
        # Top performing classes
        sorted_classes = sorted(class_summaries, key=lambda x: x["class_average"], reverse=True)
        print(f"\n🏆 Top 3 Classes:")
        for i, class_info in enumerate(sorted_classes[:3], 1):
            print(f"   {i}. {class_info['class_name']} - Average: {class_info['class_average']:.2f}")
        
        return None


def generate_sample_school_data():
    """Generate sample school data for demonstration."""
    import random
    
    # Subject names
    subjects = ["Mathematics", "Science", "English", "History", "Art", "Physics", "Chemistry", "Biology"]
    teachers = ["Mr. Smith", "Ms. Johnson", "Dr. Brown", "Mrs. Davis", "Mr. Wilson", "Ms. Garcia", "Dr. Lee", "Mr. Taylor"]
    
    # Generate student names
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Ethan", "Fiona", "George", "Hannah", "Ian", "Julia"]
    last_names = ["Anderson", "Brown", "Campbell", "Davis", "Evans", "Fisher", "Green", "Harris", "Jones", "King"]
    
    classes = []
    
    # Generate 8 classes
    for i in range(8):
        class_data = {
            "class_name": f"{subjects[i]} 101",
            "teacher": teachers[i],
            "students": []
        }
        
        # Generate 20-30 students per class
        num_students = random.randint(20, 30)
        
        for j in range(num_students):
            student = {
                "student_id": f"STU{i:02d}{j:03d}",
                "name": f"{random.choice(first_names)} {random.choice(last_names)}",
                "assignments": []
            }
            
            # Generate 5-8 assignments per student
            num_assignments = random.randint(5, 8)
            for k in range(num_assignments):
                # Generate scores with some randomness
                # Most students get 70-95, some outliers
                if random.random() < 0.1:  # 10% chance of low score
                    score = random.randint(40, 60)
                elif random.random() < 0.9:  # 80% chance of normal score
                    score = random.randint(70, 95)
                else:  # 10% chance of perfect score
                    score = random.randint(96, 100)
                
                assignment = {
                    "assignment_id": f"A{k+1}",
                    "name": f"Assignment {k+1}",
                    "score": score
                }
                student["assignments"].append(assignment)
            
            class_data["students"].append(student)
        
        classes.append(class_data)
    
    return {
        "school_name": "KayGraph Academy",
        "school_id": "KGA001",
        "classes": classes
    }


def main():
    """Run the nested batch processing example."""
    print("🎓 KayGraph Nested Batch Processing - School Grades")
    print("=" * 60)
    print("This example demonstrates hierarchical batch processing:")
    print("School → Classes → Students\n")
    
    # Generate sample data
    school_data = generate_sample_school_data()
    
    print(f"Generated sample data for: {school_data['school_name']}")
    print(f"  - Classes: {len(school_data['classes'])}")
    total_students = sum(len(c["students"]) for c in school_data["classes"])
    print(f"  - Total Students: {total_students}\n")
    
    # Create the school-level batch processor
    school_processor = SchoolBatchGraph(graph_id="school_processor")
    
    # Shared context
    shared = {
        "school_data": school_data
    }
    
    # Run the nested batch processing
    import time
    start_time = time.time()
    
    school_processor.run(shared)
    
    end_time = time.time()
    
    print(f"\n⏱️  Total processing time: {end_time - start_time:.2f} seconds")
    print(f"📄 Detailed report saved to: school_report.json")
    
    # Show nesting benefit
    print(f"\n🔄 Nested Batch Processing Benefits:")
    print(f"  - Natural hierarchy: Mirrors real-world structure")
    print(f"  - Isolated processing: Each level has its own context")
    print(f"  - Progressive aggregation: Results bubble up through levels")
    print(f"  - Parallelizable: Each level can be processed concurrently")


if __name__ == "__main__":
    main()