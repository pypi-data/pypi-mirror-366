import argparse
import json
import logging
from typing import Dict, Any
from graph import create_validated_pipeline
from utils.validation import generate_validation_report

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_pipeline_demo(include_invalid: bool = False):
    """Run the validated pipeline demo"""
    
    # Initialize shared context
    shared: Dict[str, Any] = {
        "config": {
            "include_invalid_data": include_invalid,
            "validation_enabled": True
        }
    }
    
    # Create and configure the pipeline
    pipeline = create_validated_pipeline()
    pipeline.set_params({
        "input_file": "sample_data.json",
        "include_invalid": include_invalid
    })
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║          KayGraph Validated Pipeline Demo                 ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  This demo shows:                                         ║
    ║  • ValidatedNode input/output validation                  ║
    ║  • Schema validation at each stage                        ║
    ║  • Business rule enforcement                              ║
    ║  • Statistical validation                                 ║
    ║  • Quality assurance patterns                             ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Running pipeline with {'invalid' if include_invalid else 'valid'} data...
    """)
    
    try:
        # Run the pipeline
        logger.info("Starting validated data pipeline...")
        result = pipeline.run(shared)
        
        # Display results
        display_pipeline_results(shared)
        
        # Generate validation report
        if "transformed_records" in shared:
            logger.info("Generating comprehensive validation report...")
            report = generate_validation_report(shared["transformed_records"])
            display_validation_report(report)
        
        logger.info("Pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"Pipeline failed with validation error: {e}")
        print(f"\n❌ Pipeline failed: {e}")
        print("This demonstrates KayGraph's ValidatedNode preventing bad data propagation!")
        
        # Show what data was processed before failure
        if shared:
            print(f"\n📊 Data processed before failure:")
            for key, value in shared.items():
                if isinstance(value, (list, dict)):
                    print(f"  {key}: {type(value).__name__} with {len(value)} items")
                else:
                    print(f"  {key}: {value}")


def display_pipeline_results(shared: Dict[str, Any]):
    """Display the results of the pipeline execution"""
    
    print(f"\n📊 Pipeline Execution Results:")
    print("=" * 50)
    
    # Load statistics
    if "load_stats" in shared:
        stats = shared["load_stats"]
        print(f"📥 Data Loading:")
        print(f"  Total records loaded: {stats.get('total_loaded', 0)}")
    
    # Cleaning statistics
    if "cleaning_stats" in shared:
        stats = shared["cleaning_stats"]
        print(f"🧹 Data Cleaning:")
        print(f"  Input records: {stats.get('input_count', 0)}")
        print(f"  Output records: {stats.get('output_count', 0)}")
        print(f"  Removed/duplicates: {stats.get('removed_count', 0)}")
    
    # Transformation statistics
    if "transformation_stats" in shared:
        stats = shared["transformation_stats"]
        print(f"🔄 Data Transformation:")
        print(f"  Total transformed: {stats.get('total_transformed', 0)}")
        print(f"  High-risk records: {stats.get('high_risk_count', 0)}")
    
    # Aggregation results
    if "aggregations" in shared:
        agg = shared["aggregations"]
        if "overall" in agg:
            overall = agg["overall"]
            print(f"📈 Aggregation Results:")
            print(f"  Total records: {overall.get('count', 0)}")
            print(f"  Mean value: {overall.get('mean', 0):.2f}")
            print(f"  Std deviation: {overall.get('std_dev', 0):.2f}")
            print(f"  Range: [{overall.get('min', 0):.2f}, {overall.get('max', 0):.2f}]")
        
        if "by_category" in agg:
            print(f"  By category:")
            for cat, stats in agg["by_category"].items():
                print(f"    {cat}: {stats.get('count', 0)} records, mean={stats.get('mean', 0):.2f}")
    
    # Export results
    if "export_result" in shared:
        export = shared["export_result"]
        print(f"📤 Export:")
        print(f"  Format: {export.get('metadata', {}).get('export_format', 'unknown')}")
        print(f"  Timestamp: {export.get('metadata', {}).get('export_timestamp', 'unknown')}")
        print(f"  Validation passed: {export.get('metadata', {}).get('validation_passed', False)}")


def display_validation_report(report: Dict[str, Any]):
    """Display the validation report"""
    
    print(f"\n🔍 Validation Report:")
    print("=" * 50)
    
    summary = report.get("summary", {})
    print(f"📋 Summary:")
    print(f"  Total records: {summary.get('total_records', 0)}")
    print(f"  Total errors: {summary.get('total_errors', 0)}")
    print(f"  Total warnings: {summary.get('total_warnings', 0)}")
    print(f"  Overall valid: {'✅ YES' if summary.get('overall_valid', False) else '❌ NO'}")
    
    # Schema validation details
    schema = report.get("schema_validation", {})
    if schema:
        print(f"\n🏗️ Schema Validation:")
        print(f"  Valid records: {schema.get('valid_records', 0)}")
        print(f"  Invalid records: {schema.get('invalid_records', 0)}")
        print(f"  Warnings: {schema.get('warnings', 0)}")
        
        if schema.get("validation_details"):
            print(f"  Error details (first few):")
            for detail in schema["validation_details"][:3]:
                print(f"    Record {detail['record_id']}: {', '.join(detail['errors'][:2])}")
    
    # Business rules
    business = report.get("business_rules", {})
    if business:
        print(f"\n📏 Business Rules:")
        print(f"  Violations: {business.get('total_violations', 0)}")
        print(f"  Passed: {'✅ YES' if business.get('passed', False) else '❌ NO'}")
        
        if business.get("violations"):
            print(f"  Rule violations:")
            for violation in business["violations"][:3]:
                print(f"    • {violation}")
    
    # Statistical analysis
    stats = report.get("statistical_analysis", {})
    if stats and "statistics" in stats:
        st = stats["statistics"]
        print(f"\n📊 Statistical Analysis:")
        print(f"  Mean: {st.get('mean', 0):.2f}")
        print(f"  Std Dev: {st.get('std_dev', 0):.2f}")
        print(f"  Range: [{st.get('min', 0):.2f}, {st.get('max', 0):.2f}]")
        
        if stats.get("validations"):
            print(f"  Statistical warnings:")
            for validation in stats["validations"][:3]:
                print(f"    • {validation}")


def main():
    """Main entry point with command line options"""
    
    parser = argparse.ArgumentParser(description="KayGraph Validated Pipeline Demo")
    parser.add_argument(
        "--invalid-data",
        action="store_true",
        help="Include invalid data to demonstrate validation failures"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run the demo
    run_pipeline_demo(include_invalid=args.invalid_data)


if __name__ == "__main__":
    main()