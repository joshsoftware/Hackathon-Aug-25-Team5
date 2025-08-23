import re
import json
import pandas as pd
import nltk
from datetime import datetime
import spacy

class DataPreprocessor:
    def __init__(self):
        """Initialize the data preprocessor with required models"""
        # Download required NLTK data
        try:
            nltk.download("punkt_tab")
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            nltk.download("punkt_tab")
        
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Please install spaCy English model: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def load_raw_data(self, file_path):
        """Load raw historical land data from text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                raw_text = file.read()
            print(f"Successfully loaded data from {file_path}")
            return raw_text
        except FileNotFoundError:
            print(f"File {file_path} not found!")
            return None
    
    def clean_text(self, text):
        """Clean and normalize the historical text data"""
        if not text:
            return ""
        
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep periods, commas, and hyphens
        text = re.sub(r'[^\w\s\.,\-\(\)]', '', text)
        
        # Fix common OCR errors in historical documents
        ocr_fixes = {
            r'\baud\b': 'and',
            r'\btbe\b': 'the',
            r'\boi\b': 'of',
            r'\btlie\b': 'the',
            r'\bmcres\b': 'acres',
        }
        
        for error, correction in ocr_fixes.items():
            text = re.sub(error, correction, text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def chunk_text(self, text, max_chunk_size=1000, overlap=100):
        """Split large text into smaller chunks for processing"""
        sentences = nltk.sent_tokenize(text)
        chunks = []
        current_chunk = ""
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            if current_size + sentence_size > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                
                # Add overlap
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
                current_size = len(current_chunk)
            else:
                current_chunk += " " + sentence
                current_size += sentence_size
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def extract_metadata(self, text):
        """Extract basic metadata from the text"""
        metadata = {
            'total_length': len(text),
            'word_count': len(text.split()),
            'sentence_count': len(nltk.sent_tokenize(text)),
            'processing_date': datetime.now().isoformat()
        }
        return metadata
    
    def save_processed_data(self, data, file_path):
        """Save processed data to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            print(f"Data saved to {file_path}")
            return True
        except Exception as e:
            print(f"Error saving data: {str(e)}")
            return False

def main():
    """Test the preprocessing functionality"""
    preprocessor = DataPreprocessor()
    
    # Load sample data
    raw_data = preprocessor.load_raw_data('data/raw/historical_land_data.txt')
    
    if raw_data:
        # Clean the text
        cleaned_data = preprocessor.clean_text(raw_data)
        
        # Create chunks
        chunks = preprocessor.chunk_text(cleaned_data)
        
        # Extract metadata
        metadata = preprocessor.extract_metadata(cleaned_data)
        
        # Prepare processed data
        processed_data = {
            'original_text': raw_data[:500] + "...",  # Store first 500 chars
            'cleaned_text': cleaned_data,
            'chunks': chunks,
            'metadata': metadata,
            'chunk_count': len(chunks)
        }
        
        # Save processed data
        preprocessor.save_processed_data(processed_data, 'data/processed/cleaned_data.json')
        
        print(f"Processing complete!")
        print(f"Total chunks created: {len(chunks)}")
        print(f"Average chunk size: {sum(len(chunk) for chunk in chunks) / len(chunks):.0f} characters")

if __name__ == "__main__":
    main()