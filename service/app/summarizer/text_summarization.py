import json
import torch
from transformers import BartTokenizer, BartForConditionalGeneration, pipeline
from datetime import datetime
import pandas as pd

class LandDataSummarizer:
    def __init__(self, model_name="facebook/bart-large-cnn"):
        """Initialize BART model for summarization"""
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Initialize the summarization pipeline
        self.summarizer = pipeline(
            "summarization",
            model=model_name,
            tokenizer=model_name,
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Also load tokenizer separately for custom processing
        self.tokenizer = BartTokenizer.from_pretrained(model_name)
        self.model = BartForConditionalGeneration.from_pretrained(model_name)
        self.model.to(self.device)
    
    def load_processed_data(self, file_path):
        """Load processed data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            print(f"Loaded processed data from {file_path}")
            return data
        except FileNotFoundError:
            print(f"File {file_path} not found!")
            return None
    
    def summarize_chunk(self, text, max_length=150, min_length=50):
        """Summarize a single chunk of text"""
        try:
            # Check if text is long enough to summarize
            if len(text.split()) < 20:
                return text  # Return original if too short
            
            summary = self.summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
                truncation=True
            )
            
            return summary[0]['summary_text']
        except Exception as e:
            print(f"Error summarizing chunk: {str(e)}")
            return text[:200] + "..."  # Fallback to truncation
    
    def create_extractive_summary(self, chunks, top_k=5):
        """Create extractive summary by selecting most important chunks"""
        # Simple scoring based on keyword frequency
        land_keywords = [
            'acre', 'acres', 'land', 'property', 'deed', 'owner', 'ownership',
            'boundary', 'parcel', 'lot', 'section', 'township', 'county',
            'purchase', 'sale', 'transfer', 'grant', 'patent'
        ]
        
        chunk_scores = []
        for i, chunk in enumerate(chunks):
            score = sum(chunk.lower().count(keyword) for keyword in land_keywords)
            score += chunk.count('$')  # Money indicators
            score += len([word for word in chunk.split() if word.isdigit()])  # Numbers
            chunk_scores.append((score, i, chunk))
        
        # Sort by score and take top k
        top_chunks = sorted(chunk_scores, key=lambda x: x[0], reverse=True)[:top_k]
        top_chunks = sorted(top_chunks, key=lambda x: x[1])  # Maintain original order
        
        return [chunk[2] for chunk in top_chunks]
    
    def generate_comprehensive_summary(self, processed_data):
        """Generate multiple types of summaries"""
        chunks = processed_data['chunks']
        
        summaries = {
            'processing_info': {
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model_name,
                'total_chunks': len(chunks),
                'device': str(self.device)
            },
            'chunk_summaries': [],
            'extractive_summary': [],
            'overall_summary': "",
            'key_statistics': {}
        }
        
        print("Generating chunk summaries...")
        # Summarize each chunk
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}")
            chunk_summary = self.summarize_chunk(chunk)
            summaries['chunk_summaries'].append({
                'chunk_id': i,
                'original_length': len(chunk),
                'summary_length': len(chunk_summary),
                'summary': chunk_summary
            })
        
        print("Creating extractive summary...")
        # Create extractive summary
        important_chunks = self.create_extractive_summary(chunks)
        summaries['extractive_summary'] = [
            self.summarize_chunk(chunk, max_length=100, min_length=30) 
            for chunk in important_chunks
        ]
        
        print("Generating overall summary...")
        # Create overall summary from chunk summaries
        all_summaries = " ".join([cs['summary'] for cs in summaries['chunk_summaries']])
        if len(all_summaries.split()) > 50:
            overall = self.summarize_chunk(all_summaries, max_length=200, min_length=80)
            summaries['overall_summary'] = overall
        else:
            summaries['overall_summary'] = all_summaries
        
        # Calculate statistics
        summaries['key_statistics'] = {
            'total_original_words': sum(cs['original_length'] for cs in summaries['chunk_summaries']),
            'total_summary_words': sum(cs['summary_length'] for cs in summaries['chunk_summaries']),
            'compression_ratio': round(
                sum(cs['summary_length'] for cs in summaries['chunk_summaries']) /
                sum(cs['original_length'] for cs in summaries['chunk_summaries']), 3
            )
        }
        
        return summaries
    
    def save_summaries(self, summaries, file_path):
        """Save summaries to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(summaries, file, indent=2, ensure_ascii=False)
            print(f"Summaries saved to {file_path}")
            return True
        except Exception as e:
            print(f"Error saving summaries: {str(e)}")
            return False
    
    def create_summary_report(self, summaries):
        """Create a readable summary report"""
        report = []
        report.append("=" * 60)
        report.append("HISTORICAL LAND DATA SUMMARY REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {summaries['processing_info']['timestamp']}")
        report.append(f"Model: {summaries['processing_info']['model_used']}")
        report.append(f"Total chunks processed: {summaries['processing_info']['total_chunks']}")
        report.append("")
        
        report.append("OVERALL SUMMARY:")
        report.append("-" * 20)
        report.append(summaries['overall_summary'])
        report.append("")
        
        report.append("KEY EXTRACTIVE POINTS:")
        report.append("-" * 25)
        for i, point in enumerate(summaries['extractive_summary'], 1):
            report.append(f"{i}. {point}")
        report.append("")
        
        report.append("STATISTICS:")
        report.append("-" * 15)
        stats = summaries['key_statistics']
        report.append(f"Compression ratio: {stats['compression_ratio']} (lower means more compressed)")
        report.append(f"Original total words: {stats['total_original_words']}")
        report.append(f"Summarized total words: {stats['total_summary_words']}")
        
        return "\n".join(report)

def main():
    """Test the summarization functionality"""
    summarizer = LandDataSummarizer()
    
    # Load processed data
    processed_data = summarizer.load_processed_data('data/processed/cleaned_data.json')
    
    if processed_data:
        # Generate summaries
        summaries = summarizer.generate_comprehensive_summary(processed_data)
        
        # Save summaries
        summarizer.save_summaries(summaries, 'data/summaries/summaries.json')
        
        # Create and save report
        report = summarizer.create_summary_report(summaries)
        
        with open('outputs/reports/summary_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("Summarization complete!")
        print("\nQuick Summary:")
        print(summaries['overall_summary'])

if __name__ == "__main__":
    main()