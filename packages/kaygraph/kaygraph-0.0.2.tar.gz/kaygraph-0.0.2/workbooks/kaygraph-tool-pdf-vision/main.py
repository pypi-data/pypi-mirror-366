"""
PDF Vision tool integration example using KayGraph.

Demonstrates processing PDF files with vision/OCR capabilities
for extracting structured data from documents.
"""

import os
import json
import logging
from typing import List, Dict, Any
from kaygraph import Node, Graph, BatchNode, BatchGraph
from utils.pdf_processor import PDFProcessor, PDFAnalyzer, process_pdf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class LoadPDFNode(Node):
    """Load PDF files for processing."""
    
    def prep(self, shared):
        """Get PDF source configuration."""
        return {
            "source": shared.get("pdf_source", "mock"),
            "pdf_paths": shared.get("pdf_paths", [])
        }
    
    def exec(self, config):
        """Load PDF file paths."""
        if config["source"] == "mock":
            # Generate mock PDF paths
            pdf_files = [
                "documents/invoice_2024_001.pdf",
                "documents/invoice_2024_002.pdf",
                "documents/quarterly_report_Q1.pdf",
                "documents/research_paper_nlp.pdf",
                "documents/application_form_jane.pdf",
                "documents/contract_services.pdf",
                "documents/technical_manual.pdf",
                "documents/financial_statement.pdf"
            ]
        elif config["source"] == "directory":
            # Scan directory for PDFs
            directory = config.get("directory", "documents")
            pdf_files = []
            if os.path.exists(directory):
                for file in os.listdir(directory):
                    if file.endswith('.pdf'):
                        pdf_files.append(os.path.join(directory, file))
        else:
            pdf_files = config["pdf_paths"]
        
        self.logger.info(f"Found {len(pdf_files)} PDF files")
        
        return {
            "pdf_files": pdf_files,
            "count": len(pdf_files)
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store PDF list."""
        shared["pdf_files"] = exec_res["pdf_files"]
        
        print(f"\n📄 Found {exec_res['count']} PDF files:")
        for pdf in exec_res["pdf_files"][:5]:
            print(f"  - {os.path.basename(pdf)}")
        if exec_res['count'] > 5:
            print(f"  ... and {exec_res['count'] - 5} more")
        
        return "default"


class ProcessPDFBatchNode(BatchNode):
    """Process multiple PDFs in batch."""
    
    def __init__(self, processing_method: str = "mock", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processing_method = processing_method
        self.processor = PDFProcessor(method=processing_method)
    
    def prep(self, shared):
        """Get PDFs to process."""
        pdf_files = shared.get("pdf_files", [])
        return pdf_files
    
    def exec(self, pdf_path):
        """Process a single PDF."""
        self.logger.info(f"Processing: {os.path.basename(pdf_path)}")
        
        try:
            # Process PDF
            result = self.processor.process_pdf(pdf_path)
            
            # Add success flag
            result["success"] = True
            result["error"] = None
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing {pdf_path}: {e}")
            return {
                "filename": os.path.basename(pdf_path),
                "path": pdf_path,
                "success": False,
                "error": str(e),
                "pages": [],
                "total_pages": 0
            }
    
    def post(self, shared, prep_res, exec_res):
        """Store processing results."""
        shared["pdf_results"] = exec_res
        
        # Count successes
        successful = sum(1 for r in exec_res if r.get("success", False))
        failed = len(exec_res) - successful
        
        print(f"\n📑 PDF Processing Results:")
        print(f"  ✅ Successful: {successful}")
        print(f"  ❌ Failed: {failed}")
        
        # Show sample results
        print("\nSample extractions:")
        for result in exec_res[:3]:
            if result.get("success"):
                print(f"\n  📄 {result['filename']}:")
                print(f"     Pages: {result['total_pages']}")
                
                # Show first few lines of text
                if result.get("pages"):
                    text = result["pages"][0].get("text", "")
                    preview = text.split('\n')[0:3]
                    for line in preview:
                        if line.strip():
                            print(f"     > {line.strip()[:60]}...")
                            break
        
        return "default"


class AnalyzePDFsNode(Node):
    """Analyze all processed PDFs."""
    
    def prep(self, shared):
        """Get processed PDFs."""
        return shared.get("pdf_results", [])
    
    def exec(self, pdf_results):
        """Analyze PDF content."""
        analyzer = PDFAnalyzer()
        
        analyses = []
        document_types = {}
        total_pages = 0
        quality_scores = []
        
        for pdf_data in pdf_results:
            if not pdf_data.get("success"):
                continue
            
            # Analyze individual PDF
            analysis = analyzer.analyze_content(pdf_data)
            analyses.append({
                "filename": pdf_data["filename"],
                "analysis": analysis
            })
            
            # Aggregate statistics
            doc_type = analysis["content_type"]
            document_types[doc_type] = document_types.get(doc_type, 0) + 1
            total_pages += pdf_data.get("total_pages", 0)
            quality_scores.append(analysis["quality_metrics"]["avg_confidence"])
        
        # Overall statistics
        overall_stats = {
            "total_documents": len(analyses),
            "total_pages": total_pages,
            "document_types": document_types,
            "average_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "quality_distribution": {
                "high": sum(1 for s in quality_scores if s >= 0.9),
                "medium": sum(1 for s in quality_scores if 0.7 <= s < 0.9),
                "low": sum(1 for s in quality_scores if s < 0.7)
            }
        }
        
        return {
            "analyses": analyses,
            "statistics": overall_stats
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store and display analysis."""
        shared["pdf_analyses"] = exec_res["analyses"]
        shared["pdf_statistics"] = exec_res["statistics"]
        
        stats = exec_res["statistics"]
        
        print(f"\n📊 PDF Analysis Summary:")
        print(f"  Total documents: {stats['total_documents']}")
        print(f"  Total pages: {stats['total_pages']}")
        print(f"  Average quality: {stats['average_quality']:.2f}")
        
        print(f"\n📋 Document Types:")
        for doc_type, count in stats["document_types"].items():
            print(f"  - {doc_type}: {count}")
        
        print(f"\n🎯 Quality Distribution:")
        print(f"  - High (≥90%): {stats['quality_distribution']['high']}")
        print(f"  - Medium (70-89%): {stats['quality_distribution']['medium']}")
        print(f"  - Low (<70%): {stats['quality_distribution']['low']}")
        
        return "default"


class ExtractStructuredDataNode(Node):
    """Extract structured data from specific document types."""
    
    def prep(self, shared):
        """Get PDF results for extraction."""
        return {
            "pdf_results": shared.get("pdf_results", []),
            "target_types": shared.get("extraction_targets", ["invoice", "form"])
        }
    
    def exec(self, data):
        """Extract structured data."""
        extracted_data = {
            "invoices": [],
            "forms": [],
            "reports": [],
            "other": []
        }
        
        for pdf_result in data["pdf_results"]:
            if not pdf_result.get("success"):
                continue
            
            extracted = pdf_result.get("extracted_data", {})
            doc_type = extracted.get("document_type", "unknown")
            
            # Organize by type
            if doc_type == "invoice":
                invoice_data = {
                    "filename": pdf_result["filename"],
                    "invoice_number": extracted.get("invoice_number"),
                    "date": extracted.get("date"),
                    "total_amount": extracted.get("total_amount"),
                    "customer": extracted.get("customer", {}),
                    "line_items": extracted.get("line_items", [])
                }
                extracted_data["invoices"].append(invoice_data)
                
            elif doc_type == "application_form":
                form_data = {
                    "filename": pdf_result["filename"],
                    "form_data": extracted.get("form_data", {}),
                    "form_type": "application"
                }
                extracted_data["forms"].append(form_data)
                
            elif doc_type in ["quarterly_report", "financial_report"]:
                report_data = {
                    "filename": pdf_result["filename"],
                    "period": extracted.get("period"),
                    "metrics": extracted.get("key_metrics", {}),
                    "revenue": extracted.get("total_revenue")
                }
                extracted_data["reports"].append(report_data)
                
            else:
                extracted_data["other"].append({
                    "filename": pdf_result["filename"],
                    "type": doc_type,
                    "data": extracted
                })
        
        return extracted_data
    
    def post(self, shared, prep_res, exec_res):
        """Store and display extracted data."""
        shared["structured_data"] = exec_res
        
        print(f"\n💎 Structured Data Extraction:")
        
        # Invoices
        if exec_res["invoices"]:
            print(f"\n📑 Invoices ({len(exec_res['invoices'])}):")
            total_amount = 0
            for inv in exec_res["invoices"]:
                amount = inv.get("total_amount", 0)
                total_amount += amount
                print(f"  - {inv['invoice_number']}: ${amount:,.2f} ({inv['filename']})")
            print(f"  Total: ${total_amount:,.2f}")
        
        # Forms
        if exec_res["forms"]:
            print(f"\n📝 Forms ({len(exec_res['forms'])}):")
            for form in exec_res["forms"]:
                form_data = form["form_data"]
                print(f"  - {form['filename']}: {form_data.get('name', 'Unknown')}")
        
        # Reports
        if exec_res["reports"]:
            print(f"\n📊 Reports ({len(exec_res['reports'])}):")
            for report in exec_res["reports"]:
                revenue = report.get("revenue", 0)
                print(f"  - {report['filename']}: {report.get('period', 'Unknown')} - Revenue: ${revenue:,.0f}")
        
        return "default"


class GenerateReportNode(Node):
    """Generate comprehensive processing report."""
    
    def prep(self, shared):
        """Gather all data for report."""
        return {
            "pdf_files": shared.get("pdf_files", []),
            "pdf_results": shared.get("pdf_results", []),
            "analyses": shared.get("pdf_analyses", []),
            "statistics": shared.get("pdf_statistics", {}),
            "structured_data": shared.get("structured_data", {})
        }
    
    def exec(self, data):
        """Generate report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "files_processed": len(data["pdf_results"]),
                "successful": sum(1 for r in data["pdf_results"] if r.get("success")),
                "total_pages": data["statistics"].get("total_pages", 0),
                "average_quality": data["statistics"].get("average_quality", 0)
            },
            "document_types": data["statistics"].get("document_types", {}),
            "structured_extractions": {
                "invoices": len(data["structured_data"].get("invoices", [])),
                "forms": len(data["structured_data"].get("forms", [])),
                "reports": len(data["structured_data"].get("reports", []))
            },
            "quality_metrics": data["statistics"].get("quality_distribution", {}),
            "recommendations": []
        }
        
        # Add recommendations
        if report["summary"]["average_quality"] < 0.8:
            report["recommendations"].append(
                "Overall extraction quality is below 80%. Consider improving document quality."
            )
        
        failed = report["summary"]["files_processed"] - report["summary"]["successful"]
        if failed > 0:
            report["recommendations"].append(
                f"{failed} documents failed to process. Review error logs."
            )
        
        return report
    
    def post(self, shared, prep_res, exec_res):
        """Save and display report."""
        # Save report
        report_path = "pdf_processing_report.json"
        with open(report_path, 'w') as f:
            json.dump(exec_res, f, indent=2)
        
        print("\n" + "=" * 60)
        print("📋 PDF PROCESSING REPORT")
        print("=" * 60)
        print(f"Generated: {exec_res['timestamp']}")
        
        summary = exec_res["summary"]
        print(f"\n📊 Processing Summary:")
        print(f"  - Files processed: {summary['files_processed']}")
        print(f"  - Successful: {summary['successful']}")
        print(f"  - Total pages: {summary['total_pages']}")
        print(f"  - Average quality: {summary['average_quality']:.1%}")
        
        print(f"\n📁 Structured Extractions:")
        extractions = exec_res["structured_extractions"]
        print(f"  - Invoices: {extractions['invoices']}")
        print(f"  - Forms: {extractions['forms']}")
        print(f"  - Reports: {extractions['reports']}")
        
        if exec_res["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in exec_res["recommendations"]:
                print(f"  • {rec}")
        
        print(f"\n💾 Full report saved to: {report_path}")
        
        shared["final_report"] = exec_res
        return None


def create_pdf_processing_graph():
    """Create the PDF processing graph."""
    # Create nodes
    load_pdfs = LoadPDFNode(node_id="load_pdfs")
    process_pdfs = ProcessPDFBatchNode(
        processing_method="mock",
        node_id="process_pdfs"
    )
    analyze_pdfs = AnalyzePDFsNode(node_id="analyze_pdfs")
    extract_data = ExtractStructuredDataNode(node_id="extract_data")
    generate_report = GenerateReportNode(node_id="generate_report")
    
    # Connect nodes
    load_pdfs >> process_pdfs >> analyze_pdfs >> extract_data >> generate_report
    
    return Graph(start=load_pdfs)


def main():
    """Run the PDF vision tool integration example."""
    print("📄 KayGraph PDF Vision Tool Integration")
    print("=" * 60)
    print("This example demonstrates PDF processing with")
    print("vision/OCR capabilities for data extraction.\n")
    
    # Create graph
    graph = create_pdf_processing_graph()
    
    # Shared context
    shared = {
        "pdf_source": "mock",  # Use mock PDFs
        "extraction_targets": ["invoice", "form", "report"]
    }
    
    # Run the graph
    graph.run(shared)
    
    print("\n✨ PDF processing example complete!")


if __name__ == "__main__":
    main()