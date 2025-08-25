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
    processed_data = '''
    1. The Initial Agreement – 18th March 2009

The first event recorded in the timeline took place on 18th March 2009, when an agreement was executed involving Venkatesh Developers and SR Developers. The legal documentation for this transaction was formalized under Document Number 791/2009.

This event marks the origin point of the contractual chain, setting the foundation for subsequent dealings. Typically, such transactions involve either the transfer of development rights, collaboration agreements, or initial sales deeds. The involvement of two developer entities indicates that the land or project under discussion was likely under joint development or being handed over for execution from one party to another.

2. Transfer to an Individual – 17th December 2009

Later in the same year, on 17th December 2009, a significant transfer occurred. The transaction involved SR Developers transferring rights or agreements to Mr. Vivek Vidyasagar. This was documented under Document Number 7983/2009.

This step shows the transition from a purely developer-to-developer arrangement into an arrangement where an individual buyer or investor entered the contractual chain. Mr. Vidyasagar became a key figure at this stage, representing the beginning of private ownership within the project. The entry of an individual often suggests that either units, flats, or portions of developed property were being allotted or that financial investment was being secured from a private buyer.

3. New Agreement with Developers – 25th January 2011

Roughly thirteen months later, on 25th January 2011, Mr. Vivek Vidyasagar entered into a new agreement with SR Developers. This agreement was officially recorded under Document Number 830/2011.

This transaction is interesting because it shows continuity of engagement between the same individual and the developers. The presence of multiple agreements between the same parties within a short span often indicates:

Modifications in the original terms (perhaps due to project delays or structural changes).

Additional purchases or transfers of rights.

Execution of a supplementary or rectification deed to correct or expand upon the earlier agreement.

This document effectively strengthened the legal relationship between Mr. Vidyasagar and SR Developers.

4. Branch Transaction – 28th January 2011

Only three days after the previous transaction, on 28th January 2011, another event was documented. Here, SR Developers transferred rights or executed a document in favor of Ms. Shweta Dhiren, which was also associated with Document Number 830/2011.

The use of the same document number suggests that this was not a completely new registration but rather a linked or supplementary record tied to the January 25th transaction. This might have involved co-ownership rights, joint purchasers being added, or subdivision of property share.

With Ms. Dhiren’s entry into the chain, the ownership and contractual complexity increased, possibly creating multiple stakeholders with legal claims over the same or subdivided assets.

5. Further Transfer – 7th December 2011

By the end of 2011, another major development occurred. On 7th December 2011, SR Developers executed a fresh agreement involving Mr. Vinayak Behere. The transaction was documented under Document Number 11658/2011.

This event marks a shift where another individual became a central stakeholder. Given the sequence of transactions, this could mean one of two things:

Mr. Vidyasagar or Ms. Dhiren’s interests were transferred or sold to Mr. Behere.

Alternatively, this could represent an additional unit or portion being sold, making Mr. Behere a new buyer within the same project.

The documentation at this stage suggests that the property or development was undergoing progressive sale and distribution among multiple private owners, all linked back to the original SR Developers.

6. Rental Agreement – 4th October 2014

Three years later, on 4th October 2014, Mr. Vinayak Behere entered into a Rental Agreement, which was formally registered under Document Number 8912/2014.

This step shows that Mr. Behere was not only holding ownership rights but also deriving economic benefit from the property by renting it out. Such an arrangement indicates that:

The project had reached a stage of usable completion.

Ownership had stabilized sufficiently for lease and rental activities to be formalized.

Mr. Behere, as a property holder, was leveraging his asset for regular income generation.

This rental agreement also reflects how property usage evolves over time—from development, to ownership transfer, to eventual utility in the form of rental accommodation.

7. Final Transaction in the Chain – 2nd July 2021

The final entry in the timeline took place on 2nd July 2021, when Mr. Vinayak Behere executed a transaction involving Mr. Amit K and Ms. Shravani P. This was registered under Document Number 8968/2021.

This event closes the transactional loop by showing a fresh transfer of rights from Behere to new individuals. The entry of Amit K and Shravani P signals either a resale of the property, a gift deed, or another form of title transfer.

By this point, the asset that originated under Venkatesh Developers in 2009 had passed through multiple owners, developers, and agreements, reflecting the lifecycle of many real estate projects in India. Over 12 years, the property transitioned across developers, private owners, rental use, and eventual resale to new stakeholders.

Broader Analysis of the Transaction Chain
1. Developer-to-Developer Transfers

The earliest part of the chain involved two developer entities, which usually happens when projects are either outsourced, jointly developed, or sold for completion. This ensures that land or development rights move from a holding developer to an executing one.

2. Entry of Individual Buyers

From 2009 onwards, individual buyers like Mr. Vidyasagar and Ms. Dhiren became part of the chain. This marks the monetization phase of the development, where property assets are liquidated into smaller saleable units.

3. Multiple Agreements in Short Succession

The quick succession of agreements in January 2011 suggests rapid transactions or corrections, a common feature in real estate when multiple stakeholders are involved or when ownership shares are being fine-tuned.

4. Long-Term Ownership and Rental

The entry of Mr. Behere in 2011 and his continued presence through a rental agreement in 2014 and a transfer in 2021 shows a long-term ownership stake. Behere’s involvement spans a full decade, indicating stability in the chain before eventual resale.

5. Resale and Conclusion

The final resale in 2021 demonstrates how property ownership typically evolves: initial development, multiple transactions, stabilization, usage, and eventual resale to new buyers.

Legal and Practical Implications

Audit Trail of Ownership – Every step in the timeline provides a clear documentary trail that establishes legal ownership across 12 years.

Potential for Disputes – With multiple transactions involving overlapping parties, there is always a possibility of title disputes if earlier agreements were not carefully structured.

Rental Income – The 2014 rental agreement highlights the property’s commercial utility beyond ownership.

Market Dynamics – The spread of transactions across 2009–2021 reflects the long gestation of real estate projects and the shifting priorities of owners (buying, holding, renting, reselling).
    '''
    
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