import os
import sys
from datetime import datetime
import argparse

# Import only needed modules
from data_preprocessing import DataPreprocessor
from text_summarization import LandDataSummarizer

class SimpleLandSummarizer:
    def __init__(self):
        """Initialize the simplified summarization pipeline"""
        self.preprocessor = DataPreprocessor()
        self.summarizer = LandDataSummarizer()
        
        # Create only necessary directories
        self.create_directories()
    
    def create_directories(self):
        """Create necessary project directories"""
        directories = [
            'data/raw',
            'data/processed',
            'data/summaries',
            'outputs/reports'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        print("Project directories created/verified.")
    
    def run_summarization_pipeline(self, input_file):
        """Run the simplified summarization pipeline"""
        
        print("="*60)
        print("HISTORICAL LAND DATA SUMMARIZATION")
        print("="*60)
        print(f"Start time: {datetime.now()}")
        print(f"Input file: {input_file}")
        print()
        
        try:
            # Step 1: Data Preprocessing
            print("STEP 1: Data Preprocessing")
            print("-" * 30)
            
            raw_data = self.preprocessor.load_raw_data(input_file)
            if not raw_data:
                print("❌ Failed to load raw data. Exiting.")
                return False
            
            cleaned_data = self.preprocessor.clean_text(raw_data)
            chunks = self.preprocessor.chunk_text(cleaned_data)
            metadata = self.preprocessor.extract_metadata(cleaned_data)
            
            processed_data = {
                'original_text': raw_data[:500] + "..." if len(raw_data) > 500 else raw_data,
                'cleaned_text': cleaned_data,
                'chunks': chunks,
                'metadata': metadata,
                'chunk_count': len(chunks)
            }
            
            self.preprocessor.save_processed_data(processed_data, 'data/processed/cleaned_data.json')
            print(f"✓ Preprocessing complete. Created {len(chunks)} chunks.")
            print()
            
            # Step 2: Text Summarization
            print("STEP 2: Text Summarization with BART")
            print("-" * 40)
            
            summaries = self.summarizer.generate_comprehensive_summary(processed_data)
            self.summarizer.save_summaries(summaries, 'data/summaries/summaries.json')
            
            # Create and save text report
            report = self.summarizer.create_summary_report(summaries)
            with open('outputs/reports/summary_report.txt', 'w', encoding='utf-8') as f:
                f.write(report)
            
            print("✓ Summarization complete.")
            print(f"✓ Compression ratio: {summaries['key_statistics'].get('compression_ratio', 'N/A')}")
            print()
            
            # Display the summary directly
            print("="*60)
            print("📝 SUMMARY RESULTS")
            print("="*60)
            print()
            
            print("🔥 OVERALL SUMMARY:")
            print("-" * 20)
            print(summaries.get('overall_summary', 'No summary available'))
            print()
            
            print("🔑 KEY EXTRACTIVE POINTS:")
            print("-" * 25)
            extractive_summary = summaries.get('extractive_summary', [])
            if extractive_summary:
                for i, point in enumerate(extractive_summary, 1):
                    print(f"{i}. {point}")
            else:
                print("No extractive summary available")
            print()
            
            print("📊 STATISTICS:")
            print("-" * 15)
            stats = summaries.get('key_statistics', {})
            if stats:
                for key, value in stats.items():
                    formatted_key = key.replace('_', ' ').title()
                    print(f"  • {formatted_key}: {value}")
            else:
                print("No statistics available")
            print()
            
            print("="*60)
            print("✅ SUMMARIZATION COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"End time: {datetime.now()}")
            print()
            print("📁 Generated Files:")
            print("  • data/processed/cleaned_data.json - Preprocessed data")
            print("  • data/summaries/summaries.json - Generated summaries")
            print("  • outputs/reports/summary_report.txt - Detailed text report")
            print()
            print("💡 Check outputs/reports/summary_report.txt for a detailed formatted report!")
            
            return True
            
        except Exception as e:
            print(f"❌ Pipeline failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_quick_summary(self, input_file):
        """Just print a quick summary without saving files"""
        try:
            print("Loading and processing text...")
            raw_data = self.preprocessor.load_raw_data(input_file)
            if not raw_data:
                print("❌ Failed to load raw data.")
                return False
            
            cleaned_data = self.preprocessor.clean_text(raw_data)
            chunks = self.preprocessor.chunk_text(cleaned_data)
            
            processed_data = {
                'cleaned_text': cleaned_data,
                'chunks': chunks,
                'chunk_count': len(chunks)
            }
            
            print("Generating summary...")
            summaries = self.summarizer.generate_comprehensive_summary(processed_data)
            
            print("\n" + "="*50)
            print("📝 QUICK SUMMARY")
            print("="*50)
            print(summaries.get('overall_summary', 'No summary available'))
            print("="*50)
            
            return True
            
        except Exception as e:
            print(f"❌ Quick summary failed: {str(e)}")
            return False

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Historical Land Data Summarization Pipeline')
    parser.add_argument('--input', '-i', required=True, help='Input text file path')
    parser.add_argument('--quick', '-q', action='store_true', help='Quick summary only (no file saving)')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = SimpleLandSummarizer()
    
    if args.quick:
        # Run quick summary without saving files
        success = pipeline.print_quick_summary(args.input)
    else:
        # Run complete summarization pipeline
        success = pipeline.run_summarization_pipeline(args.input)
    
    if success:
        print("✅ Operation completed successfully!")
        return 0
    else:
        print("❌ Operation failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())