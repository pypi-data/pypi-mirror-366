"""
Batch processing example using KayGraph.

Demonstrates translating a README file into multiple languages
using BatchNode for sequential processing.
"""

import os
import logging
from typing import List, Tuple, Dict, Any
from kaygraph import BatchNode, Graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class TranslationBatchNode(BatchNode):
    """Translate text into multiple languages using batch processing."""
    
    def __init__(self, *args, **kwargs):
        # Enable retries for reliability
        super().__init__(max_retries=3, wait=1, *args, **kwargs)
    
    def prep(self, shared):
        """Prepare batch of translation tasks."""
        # Get the README content
        readme_path = shared.get("readme_path", "README.md")
        
        try:
            with open(readme_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            # Use default content if README not found
            content = """# KayGraph Batch Example

This is a demonstration of batch processing using KayGraph.
The framework provides powerful abstractions for processing multiple items efficiently.

## Features
- Sequential batch processing
- Automatic retry handling
- Progress tracking
- Result aggregation

## Usage
Run the example to translate this content into multiple languages.
"""
            self.logger.info("Using default README content")
        
        # Languages to translate to
        languages = shared.get("languages", [
            "Spanish",
            "French", 
            "German",
            "Italian",
            "Portuguese",
            "Japanese",
            "Korean",
            "Chinese"
        ])
        
        # Create batch items: (content, language) tuples
        batch_items = [(content, lang) for lang in languages]
        
        self.logger.info(f"Prepared {len(batch_items)} translation tasks")
        return batch_items
    
    def exec(self, item):
        """Execute translation for a single language."""
        content, language = item
        
        self.logger.info(f"Translating to {language}...")
        
        # Mock translation (replace with actual translation API)
        # In real implementation, you would call a translation service
        translations = {
            "Spanish": f"# Ejemplo de Lote KayGraph\n\nEsta es una demostración de procesamiento por lotes usando KayGraph...",
            "French": f"# Exemple de Lot KayGraph\n\nCeci est une démonstration du traitement par lots avec KayGraph...",
            "German": f"# KayGraph Batch-Beispiel\n\nDies ist eine Demonstration der Batch-Verarbeitung mit KayGraph...",
            "Italian": f"# Esempio Batch KayGraph\n\nQuesta è una dimostrazione dell'elaborazione batch con KayGraph...",
            "Portuguese": f"# Exemplo de Lote KayGraph\n\nEsta é uma demonstração de processamento em lote usando KayGraph...",
            "Japanese": f"# KayGraphバッチ例\n\nこれはKayGraphを使用したバッチ処理のデモンストレーションです...",
            "Korean": f"# KayGraph 배치 예제\n\n이것은 KayGraph를 사용한 배치 처리의 데모입니다...",
            "Chinese": f"# KayGraph批处理示例\n\n这是使用KayGraph进行批处理的演示..."
        }
        
        # Simulate translation delay
        import time
        time.sleep(0.5)
        
        # Get translation or create a placeholder
        if language in translations:
            translated = translations[language]
        else:
            # Generic translation placeholder
            translated = f"# KayGraph Batch Example [{language}]\n\n[Translated content for {language}]\n\n" + \
                        f"Original content would be translated to {language} here..."
        
        return {
            "language": language,
            "original": content[:100] + "...",  # First 100 chars
            "translated": translated,
            "char_count": len(translated)
        }
    
    def post(self, shared, prep_res, exec_res):
        """Save all translations and create summary."""
        # Create output directory
        output_dir = "translations"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save each translation
        total_chars = 0
        languages_processed = []
        
        for result in exec_res:
            language = result["language"]
            translated = result["translated"]
            
            # Save to file
            filename = f"{output_dir}/README_{language.lower()}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(translated)
            
            self.logger.info(f"Saved {language} translation to {filename}")
            
            total_chars += result["char_count"]
            languages_processed.append(language)
        
        # Create summary
        summary = {
            "languages_processed": languages_processed,
            "total_translations": len(languages_processed),
            "total_characters": total_chars,
            "average_chars_per_translation": total_chars / len(languages_processed) if languages_processed else 0,
            "output_directory": output_dir
        }
        
        # Save summary
        import json
        with open(f"{output_dir}/translation_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        shared["translation_summary"] = summary
        
        print(f"\n✅ Translation Summary:")
        print(f"  - Languages: {', '.join(languages_processed)}")
        print(f"  - Total translations: {summary['total_translations']}")
        print(f"  - Output directory: {output_dir}/")
        
        return None


def create_translation_graph():
    """Create a graph for batch translation."""
    translator = TranslationBatchNode(node_id="translator")
    return Graph(start=translator)


def main():
    """Run the batch translation example."""
    print("🌐 KayGraph Batch Translation Example")
    print("=" * 50)
    
    # Create graph
    graph = create_translation_graph()
    
    # Shared context
    shared = {
        "readme_path": "README.md",  # Will use default if not found
        "languages": [
            "Spanish",
            "French",
            "German",
            "Italian",
            "Portuguese",
            "Japanese",
            "Korean",
            "Chinese",
            "Russian",
            "Arabic"
        ]
    }
    
    print(f"Translating README into {len(shared['languages'])} languages...")
    print("This demonstrates sequential batch processing.\n")
    
    # Run the graph
    start_time = __import__('time').time()
    graph.run(shared)
    end_time = __import__('time').time()
    
    # Show results
    summary = shared.get("translation_summary", {})
    
    print(f"\n⏱️  Processing time: {end_time - start_time:.2f} seconds")
    print(f"📊 Average time per translation: {(end_time - start_time) / summary['total_translations']:.2f} seconds")
    
    print("\n💡 Note: For faster processing, see kaygraph-parallel-batch example!")


if __name__ == "__main__":
    main()