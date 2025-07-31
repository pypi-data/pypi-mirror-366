#!/usr/bin/env python3
"""
Script to generate MDC files from the KayGraph docs folder, creating one MDC file per MD file.

Usage:
    python update_kaygraph_mdc.py [--docs-dir PATH] [--rules-dir PATH]
"""

import os
import re
import shutil
from pathlib import Path
import sys
import html.parser

class HTMLTagStripper(html.parser.HTMLParser):
    """HTML Parser subclass to strip HTML tags from content"""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def get_text(self):
        return ''.join(self.text)

def strip_html_tags(html_content):
    """Remove HTML tags from content"""
    stripper = HTMLTagStripper()
    stripper.feed(html_content)
    return stripper.get_text()

def extract_frontmatter(file_path):
    """Extract title, parent, and nav_order from markdown frontmatter"""
    frontmatter = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Extract frontmatter between --- markers
            fm_match = re.search(r'^---\s*(.+?)\s*---', content, re.DOTALL)
            if fm_match:
                frontmatter_text = fm_match.group(1)

                # Extract fields
                title_match = re.search(r'title:\s*"?([^"\n]+)"?', frontmatter_text)
                parent_match = re.search(r'parent:\s*"?([^"\n]+)"?', frontmatter_text)
                nav_order_match = re.search(r'nav_order:\s*(\d+)', frontmatter_text)

                if title_match:
                    frontmatter['title'] = title_match.group(1)
                if parent_match:
                    frontmatter['parent'] = parent_match.group(1)
                if nav_order_match:
                    frontmatter['nav_order'] = int(nav_order_match.group(1))
    except Exception as e:
        print(f"Error reading frontmatter from {file_path}: {e}")

    return frontmatter

def extract_first_heading(file_path):
    """Extract the first heading from markdown content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Remove frontmatter
            content = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL)

            # Find first heading
            heading_match = re.search(r'#\s+(.+)', content)
            if heading_match:
                return heading_match.group(1).strip()
    except Exception as e:
        print(f"Error extracting heading from {file_path}: {e}")

    # Fallback to filename if no heading found
    return Path(file_path).stem.replace('_', ' ').title()

def get_mdc_description(md_file, frontmatter, heading):
    """Generate a description for the MDC file based on file metadata"""
    section = ""
    subsection = ""

    # Determine section from path - UPDATED for new structure
    path_parts = Path(md_file).parts
    if 'fundamentals' in path_parts:
        section = "Fundamentals"
    elif 'patterns' in path_parts:
        section = "Patterns"
    elif 'integrations' in path_parts:
        section = "Integrations"
    elif 'production' in path_parts:
        section = "Production"
    
    # Special handling for advanced_usage.md
    if Path(md_file).name == "advanced_usage.md":
        return "Guidelines for using KayGraph, Advanced Usage and Production Features"

    # Use frontmatter title or heading as subsection
    if 'title' in frontmatter:
        subsection = frontmatter['title']
    else:
        subsection = heading

    # For the combined guide and index
    if Path(md_file).name == "guide.md":
        return "Guidelines for using KayGraph, Agentic Coding and Development Best Practices"

    # For index.md at root level, use a different format
    if Path(md_file).name == "index.md" and section == "":
        return "Guidelines for using KayGraph, a production-ready LLM framework with enterprise features"

    # For other files, create a more specific description
    if section:
        return f"Guidelines for using KayGraph, {section}, {subsection}"
    else:
        return f"Guidelines for using KayGraph, {subsection}"

def process_markdown_content(content, remove_local_refs=False):
    """Process markdown content to make it suitable for MDC file"""
    # Remove frontmatter
    content = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL)

    # Replace HTML div tags and their content
    content = re.sub(r'<div.*?>.*?</div>', '', content, flags=re.DOTALL)

    if remove_local_refs:
        # Replace markdown links to local documentation with just the text in brackets
        # This prevents automatically including all docs when the file is loaded
        # Keep the brackets around the text for better discoverability
        content = re.sub(r'\[([^\]]+)\]\(\./[^)]+\)', r'[\1]', content)
    else:
        # Adjust relative links to maintain references within the docs structure
        content = re.sub(r'\]\(\./([^)]+)\)', r'](mdc:./\1)', content)

        # Ensure links to md files work correctly
        content = re.sub(r'\]\(mdc:\./(.+?)\.md\)', r'](mdc:./\1.md)', content)
        content = re.sub(r'\]\(mdc:\./(.+?)\.html\)', r'](mdc:./\1.md)', content)

    # Strip remaining HTML tags
    content = strip_html_tags(content)

    return content

def get_documentation_first_policy():
    """Return the DOCUMENTATION FIRST POLICY text to be included in the guide"""
    return """# DOCUMENTATION FIRST POLICY

**CRITICAL INSTRUCTION**: When implementing a KayGraph app:

1. **ALWAYS REQUEST MDC FILES FIRST** - Before writing any code, request and review all relevant MDC documentation files. This doc provides an explanation of the documents.
2. **UNDERSTAND THE FRAMEWORK** - Gain comprehensive understanding of the KayGraph framework from documentation including:
   - **Fundamentals**: Core concepts (Node, Graph, async, batch, parallel)
   - **Patterns**: Common implementation patterns (Agent, RAG, Map-Reduce, Multi-Agent)
   - **Integrations**: External service connections (LLM, vector databases, search)
   - **Production**: Enterprise features (validation, monitoring, deployment, troubleshooting)
3. **AVOID ASSUMPTION-DRIVEN DEVELOPMENT** - Do not base your implementation on assumptions or guesswork. Even if the human didn't explicitly mention KayGraph in their request, if the code you are editing is using KayGraph, you should request relevant docs to help you understand best practice before editing.
4. **USE PRODUCTION-READY PATTERNS** - KayGraph includes enterprise features like ValidatedNode, MetricsNode, logging, error handling, and resource management. Use these in production code.

**VERIFICATION**: Begin each implementation with a brief summary of the documentation you've reviewed to inform your approach.

**KEY KAYGRAPH FEATURES TO LEVERAGE**:
- Node identification and execution context tracking
- Built-in comprehensive logging system
- Parameter validation and type checking
- Execution hooks (before_prep, after_exec, on_error)
- Context manager support (setup_resources, cleanup_resources)
- ValidatedNode for input/output validation
- MetricsNode for performance monitoring
- Enhanced error handling with exec_fallback
- Execution context (get_context, set_context)
- Operator overloading (>> for default, - for named actions)
- Thread-safe node copying in graphs
- Async variants (AsyncNode, AsyncBatchNode, AsyncGraph)

"""

def generate_mdc_header(md_file, description, always_apply=False, priority="medium"):
    """Generate MDC file header with appropriate frontmatter"""
    # Determine if we should include globs and priority based on file type
    path_parts = Path(md_file).parts
    file_name = Path(md_file).name
    file_path_lower = str(md_file).lower()
    
    # High priority for core concepts and guide
    if (file_name in ["guide.md", "index.md"] or 
        "fundamentals" in path_parts or 
        "production" in path_parts):
        priority = "high"
        globs = "**/*.py"
        always_apply = True
    
    # High priority for critical production features
    elif ("monitoring" in file_path_lower or 
          "metrics" in file_path_lower or
          "validation" in file_path_lower):
        priority = "high"
        globs = "**/*.py"
        always_apply = False
    
    # Medium priority for patterns and advanced usage
    elif ("patterns" in path_parts or 
          file_name == "advanced_usage.md"):
        priority = "medium"
        globs = "**/*.py"
        always_apply = False
    
    # Lower priority for integrations (utilities)
    elif "integrations" in path_parts:
        priority = "low"
        globs = ""
        always_apply = False
    
    # Default for other files
    else:
        globs = "**/*.py" if always_apply else ""

    return f"""---
description: {description}
globs: {globs}
alwaysApply: {"true" if always_apply else "false"}
priority: {priority}
---
"""

def has_substantive_content(content):
    """Check if the processed content has substantive content beyond the frontmatter"""
    # Remove frontmatter
    content_without_frontmatter = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL)

    # Remove whitespace and common HTML/markdown formatting
    cleaned_content = re.sub(r'\s+', '', content_without_frontmatter)
    cleaned_content = re.sub(r'{:.*?}', '', cleaned_content)

    # If there's almost nothing left after cleaning, consider it empty
    return len(cleaned_content) > 20  # Arbitrary threshold, adjust as needed

def create_combined_guide(docs_dir, rules_dir, dry_run=False):
    """Create a combined guide that includes both the guide and index content"""
    docs_path = Path(docs_dir)
    rules_path = Path(rules_dir)

    guide_file = docs_path / "guide.md"
    index_file = docs_path / "index.md"

    if not guide_file.exists() or not index_file.exists():
        print("Warning: guide.md or index.md not found, skipping combined guide creation")
        return False

    # Get guide content and index content
    with open(guide_file, 'r', encoding='utf-8') as f:
        guide_content = f.read()

    with open(index_file, 'r', encoding='utf-8') as f:
        index_content = f.read()

    # Process the content
    processed_guide = process_markdown_content(guide_content, remove_local_refs=True)
    processed_index = process_markdown_content(index_content, remove_local_refs=True)

    # Get the documentation first policy
    doc_first_policy = get_documentation_first_policy()

    # Combine the content with the documentation first policy at the beginning
    combined_content = doc_first_policy + processed_guide + "\n\n" + processed_index

    # Generate the MDC header
    description = "Guidelines for using KayGraph, Agentic Coding and Development Best Practices"
    mdc_header = generate_mdc_header(guide_file, description, always_apply=True, priority="high")

    # Combine header and processed content
    mdc_content = mdc_header + combined_content

    # Create the output path with the new filename
    output_path = rules_path / "guide_for_kaygraph.mdc"

    # Write the MDC file (skip if dry run)
    if not dry_run:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(mdc_content)
        print(f"Created combined guide MDC file: {output_path}")
    else:
        print(f"[DRY RUN] Would create combined guide: {output_path}")
    
    return True

def convert_md_to_mdc(md_file, output_dir, docs_dir, special_treatment=False, dry_run=False):
    """Convert a markdown file to MDC format and save to the output directory"""
    try:
        print(f"Processing: {md_file}")

        # Skip guide.md and index.md as they'll be handled separately
        file_name = Path(md_file).name
        if file_name in ["guide.md", "index.md"]:
            print(f"Skipping {file_name} for individual processing - it will be included in the combined guide")
            return True

        # Skip empty index.md files in subfolders - UPDATED for new structure
        parent_dir = Path(md_file).parent.name

        # Check if this is an index.md in a subfolder (not the main index.md)
        if (file_name == "index.md" and parent_dir != "docs" and
            parent_dir in ["fundamentals", "patterns", "integrations", "production"]):

            # Read the content
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Skip if it doesn't have substantive content
            if not has_substantive_content(content):
                print(f"Skipping empty subfolder index: {md_file}")
                return True

        # Extract metadata from file
        frontmatter = extract_frontmatter(md_file)
        heading = extract_first_heading(md_file)
        description = get_mdc_description(md_file, frontmatter, heading)

        # Read the content
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Process the content
        processed_content = process_markdown_content(content, remove_local_refs=special_treatment)

        # Generate the MDC header
        mdc_header = generate_mdc_header(md_file, description, always_apply=special_treatment)

        # Combine header and processed content
        mdc_content = mdc_header + processed_content

        # Perform a final check to ensure the processed content is substantive
        if not has_substantive_content(processed_content):
            print(f"Skipping file with no substantive content after processing: {md_file}")
            return True

        # Get the path relative to the docs directory
        rel_path = os.path.relpath(md_file, start=Path(docs_dir))

        # Extract just the filename and directory structure without the 'docs/' prefix
        path_parts = Path(rel_path).parts
        if len(path_parts) > 1 and path_parts[0] == 'docs':
            # Remove the 'docs/' prefix from the path
            rel_path = os.path.join(*path_parts[1:])

        # Create the output path
        output_path = Path(output_dir) / rel_path

        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Change extension from .md to .mdc
        output_path = output_path.with_suffix('.mdc')

        # Write the MDC file (skip if dry run)
        if not dry_run:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(mdc_content)
            print(f"Created MDC file: {output_path}")
        else:
            print(f"[DRY RUN] Would create: {output_path}")
        
        return True

    except Exception as e:
        print(f"Error converting {md_file} to MDC: {e}")
        return False

def generate_mdc_files(docs_dir, rules_dir, dry_run=False):
    """Generate MDC files from all markdown files in the docs directory"""
    docs_path = Path(docs_dir)
    rules_path = Path(rules_dir)

    # Make sure the docs directory exists
    if not docs_path.exists() or not docs_path.is_dir():
        raise ValueError(f"Directory not found: {docs_dir}")

    print(f"Generating MDC files from docs in: {docs_dir}")
    print(f"Output will be written to: {rules_dir}")
    if dry_run:
        print("[DRY RUN MODE - No files will be created]")

    # Create the rules directory if it doesn't exist (skip for dry run)
    if not dry_run:
        rules_path.mkdir(parents=True, exist_ok=True)

    # Check for critical documentation
    critical_docs = ["fundamentals/node.md", "fundamentals/graph.md"]
    missing_critical = [doc for doc in critical_docs if not (docs_path / doc).exists()]
    if missing_critical:
        print(f"⚠️  Warning: Missing critical documentation: {missing_critical}")

    # Create the combined guide file first (includes both guide.md and index.md)
    create_combined_guide(docs_dir, rules_dir, dry_run=dry_run)

    # Process all other markdown files
    success_count = 0
    failure_count = 0
    updated_files = []
    created_files = []

    # Find all markdown files
    md_files = list(docs_path.glob("**/*.md"))

    # Skip the main index.md and guide.md files as we've already processed them in create_combined_guide
    md_files = [f for f in md_files if f.name not in ["index.md", "guide.md"]]

    # Process each markdown file
    for md_file in md_files:
        # Track file creation/updates
        output_path = rules_path / Path(md_file).relative_to(docs_path).with_suffix('.mdc')
        existed = output_path.exists() if output_path else False
        
        if convert_md_to_mdc(md_file, rules_path, docs_dir, dry_run=dry_run):
            success_count += 1
            if existed:
                updated_files.append(output_path)
            else:
                created_files.append(output_path)
        else:
            failure_count += 1

    print(f"\nProcessed {len(md_files) + 1} markdown files:")  # +1 for the combined guide
    print(f"  - Successfully converted: {success_count + 1}")  # +1 for the combined guide
    print(f"  - Failed conversions: {failure_count}")
    if created_files:
        print(f"  - New MDC files created: {len(created_files)}")
    if updated_files:
        print(f"  - Existing MDC files updated: {len(updated_files)}")

    # Print summary of created rules by category
    print(f"\n=== MDC Rules Summary ===")
    print(f"📋 Combined Guide: guide_for_kaygraph.mdc (HIGH priority)")
    
    # Count files by category
    fundamentals_count = len([f for f in md_files if 'fundamentals' in str(f)])
    patterns_count = len([f for f in md_files if 'patterns' in str(f)])
    integrations_count = len([f for f in md_files if 'integrations' in str(f)])
    production_count = len([f for f in md_files if 'production' in str(f)])
    other_count = len(md_files) - fundamentals_count - patterns_count - integrations_count - production_count
    
    print(f"🏗️  Fundamentals: {fundamentals_count} files (HIGH priority)")
    print(f"🎯 Patterns: {patterns_count} files (MEDIUM priority)")
    print(f"🔌 Integrations: {integrations_count} files (LOW priority)")
    print(f"🚀 Production: {production_count} files (HIGH priority)")
    if other_count > 0:
        print(f"📄 Other: {other_count} files")

    return success_count > 0 and failure_count == 0

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate MDC files from KayGraph docs")

    # Get script directory
    script_dir = Path(__file__).parent.absolute()

    # Default to KayGraph/docs directory relative to script location
    default_docs_dir = (script_dir.parent / "docs").as_posix()

    # Default rules directory - changed to .cursor/rules
    default_rules_dir = (script_dir.parent / ".cursor" / "rules").as_posix()

    parser.add_argument("--docs-dir",
                        default=default_docs_dir,
                        help="Path to KayGraph docs directory")
    parser.add_argument("--rules-dir",
                        default=default_rules_dir,
                        help="Output directory for MDC files")
    parser.add_argument("--dry-run",
                        action="store_true",
                        help="Show what would be created without creating files")

    args = parser.parse_args()

    try:
        success = generate_mdc_files(args.docs_dir, args.rules_dir, dry_run=args.dry_run)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)