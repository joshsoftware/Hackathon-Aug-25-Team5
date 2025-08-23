import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
from datetime import datetime
import numpy as np
from wordcloud import WordCloud
import folium

class LandDataVisualizer:
    def __init__(self):
        """Initialize the visualizer with styling"""
        # Set matplotlib and seaborn styling
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create output directory
        import os
        os.makedirs('outputs/charts', exist_ok=True)
    
    def load_entities(self, file_path):
        """Load extracted entities from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            print(f"Loaded entities from {file_path}")
            return data
        except FileNotFoundError:
            print(f"File {file_path} not found!")
            return None
    
    def create_entity_distribution_chart(self, entities_data):
        """Create bar chart showing distribution of entity types"""
        if 'named_entities' not in entities_data:
            return None
        
        # Count entities by type
        entity_counts = {}
        for entity_type, entities in entities_data['named_entities'].items():
            entity_counts[entity_type] = len(entities)
        
        if not entity_counts:
            return None
        
        # Create plotly bar chart
        fig = px.bar(
            x=list(entity_counts.keys()),
            y=list(entity_counts.values()),
            title="Distribution of Named Entities in Historical Land Data",
            labels={'x': 'Entity Type', 'y': 'Count'},
            color=list(entity_counts.values()),
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(
            showlegend=False,
            xaxis_tickangle=-45,
            height=500
        )
        
        fig.write_html('outputs/charts/entity_distribution.html')
        fig.write_image('outputs/charts/entity_distribution.png', width=800, height=500)
        
        return fig
    
    def create_acreage_analysis(self, entities_data):
        """Create visualization for acreage data"""
        land_data = entities_data.get('land_specific', {})
        acreage_data = land_data.get('acreage', [])
        
        if not acreage_data:
            return None
        
        # Extract numerical values
        acreages = []
        for item in acreage_data:
            try:
                value = float(item['value'])
                acreages.append(value)
            except ValueError:
                continue
        
        if not acreages:
            return None
        
        # Create subplot with multiple charts
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Acreage Distribution', 'Acreage Histogram', 
                          'Box Plot', 'Cumulative Distribution'),
            specs=[[{"type": "scatter"}, {"type": "histogram"}],
                   [{"type": "box"}, {"type": "scatter"}]]
        )
        
        # Scatter plot
        fig.add_trace(
            go.Scatter(x=list(range(len(acreages))), y=acreages, 
                      mode='markers+lines', name='Acreage Values'),
            row=1, col=1
        )
        
        # Histogram
        fig.add_trace(
            go.Histogram(x=acreages, name='Acreage Frequency', nbinsx=10),
            row=1, col=2
        )
        
        # Box plot
        fig.add_trace(
            go.Box(y=acreages, name='Acreage Distribution'),
            row=2, col=1
        )
        
        # Cumulative distribution
        sorted_acreages = sorted(acreages)
        cumulative_pct = np.arange(1, len(sorted_acreages) + 1) / len(sorted_acreages) * 100
        fig.add_trace(
            go.Scatter(x=sorted_acreages, y=cumulative_pct, 
                      mode='lines', name='Cumulative %'),
            row=2, col=2
        )
        
        fig.update_layout(height=800, title_text="Acreage Analysis Dashboard")
        fig.write_html('outputs/charts/acreage_analysis.html')
        
        return fig
    
    def create_money_timeline(self, entities_data):
        """Create timeline visualization for monetary transactions"""
        land_data = entities_data.get('land_specific', {})
        money_data = land_data.get('money', [])
        date_data = land_data.get('dates', [])
        
        if not money_data:
            return None
        
        # Extract money values
        amounts = []
        for item in money_data:
            try:
                amount = float(item['value'].replace(',', ''))
                amounts.append(amount)
            except ValueError:
                continue
        
        # Create simple timeline if we don't have proper dates
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=list(range(len(amounts))),
            y=amounts,
            mode='markers+lines',
            marker=dict(size=10, color=amounts, colorscale='viridis'),
            name='Transaction Amounts',
            text=[f'${amt:,.2f}' for amt in amounts],
            hovertemplate='Transaction %{x}<br>Amount: %{text}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Historical Land Transaction Amounts",
            xaxis_title="Transaction Sequence",
            yaxis_title="Amount ($)",
            height=500
        )
        
        fig.write_html('outputs/charts/money_timeline.html')
        return fig
    
    def create_ownership_network(self, entities_data):
        """Create network graph showing ownership relationships"""
        ownership_data = entities_data.get('ownership_info', {})
        
        # Create network graph
        G = nx.Graph()
        
        # Add nodes and edges from ownership data
        for grantor in ownership_data.get('grantors', []):
            for grantee in ownership_data.get('grantees', []):
                G.add_edge(grantor, grantee, relationship='transfer')
        
        # Add owner nodes
        for owner in ownership_data.get('owners', []):
            G.add_node(owner, node_type='owner')
        
        if len(G.nodes()) == 0:
            return None
        
        # Create layout
        pos = nx.spring_layout(G)
        
        # Extract edges
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        # Create edge trace
        edge_trace = go.Scatter(x=edge_x, y=edge_y,
                               line=dict(width=2, color='#888'),
                               hoverinfo='none',
                               mode='lines')
        
        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
        
        node_trace = go.Scatter(x=node_x, y=node_y,
                               mode='markers+text',
                               text=node_text,
                               textposition="middle center",
                               hoverinfo='text',
                               marker=dict(size=20,
                                         color='lightblue',
                                         line=dict(width=2, color='black')))
        
        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title='Land Ownership Network',
                           titlefont_size=16,
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[ dict(
                               text="Connections show land transfers between parties",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002 ) ],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                           ))
        
        fig.write_html('outputs/charts/ownership_network.html')
        return fig
    
    def create_word_cloud(self, summaries_data):
        """Create word cloud from the summarized text"""
        # Combine all summary text
        all_text = ""
        if 'overall_summary' in summaries_data:
            all_text += summaries_data['overall_summary'] + " "
        
        for summary in summaries_data.get('extractive_summary', []):
            all_text += summary + " "
        
        if not all_text.strip():
            return None
        
        # Create word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            colormap='viridis',
            max_words=100,
            relative_scaling=0.5,
            stopwords={'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        ).generate(all_text)
        
        # Create matplotlib figure
        plt.figure(figsize=(12, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Most Common Terms in Historical Land Data', fontsize=16, fontweight='bold')
        plt.tight_layout(pad=0)
        plt.savefig('outputs/charts/wordcloud.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return wordcloud
    
    def create_geographical_visualization(self, entities_data):
        """Create map visualization for geographical data"""
        geo_data = entities_data.get('geographical_info', {})
        
        # Sample coordinates for demonstration (you'd need actual coordinates)
        sample_locations = [
            {'name': 'Sample County A', 'lat': 40.7128, 'lon': -74.0060, 'type': 'county'},
            {'name': 'Sample County B', 'lat': 41.8781, 'lon': -87.6298, 'type': 'county'},
            {'name': 'Sample Township', 'lat': 42.3601, 'lon': -71.0589, 'type': 'township'},
        ]
        
        # Create base map
        m = folium.Map(location=[40.0, -85.0], zoom_start=5)
        
        # Add markers for each location
        for location in sample_locations:
            folium.Marker(
                [location['lat'], location['lon']],
                popup=f"{location['name']} ({location['type']})",
                tooltip=location['name'],
                icon=folium.Icon(color='green' if location['type'] == 'county' else 'blue')
            ).add_to(m)
        
        # Save map
        m.save('outputs/charts/geographical_map.html')
        return m
    
    def create_comprehensive_dashboard(self, entities_data, summaries_data):
        """Create a comprehensive HTML dashboard"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Historical Land Data Analysis Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; }
                .header { text-align: center; color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 20px; }
                .section { margin: 20px 0; padding: 15px; border-left: 4px solid #4CAF50; }
                .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
                .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 8px; text-align: center; }
                .chart-container { margin: 20px 0; text-align: center; }
                .summary-box { background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Historical Land Data Analysis Dashboard</h1>
                    <p>Generated on: {timestamp}</p>
                </div>
                
                <div class="section">
                    <h2>📊 Key Statistics</h2>
                    <div class="stats-grid">
                        {stats_cards}
                    </div>
                </div>
                
                <div class="section">
                    <h2>📝 Executive Summary</h2>
                    <div class="summary-box">
                        <p>{overall_summary}</p>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🔑 Key Points</h2>
                    <ul>
                        {key_points}
                    </ul>
                </div>
                
                <div class="section">
                    <h2>📈 Interactive Charts</h2>
                    <p>The following interactive charts have been generated:</p>
                    <ul>
                        <li><a href="entity_distribution.html">Entity Distribution Chart</a></li>
                        <li><a href="acreage_analysis.html">Acreage Analysis Dashboard</a></li>
                        <li><a href="money_timeline.html">Money Timeline</a></li>
                        <li><a href="ownership_network.html">Ownership Network</a></li>
                        <li><a href="geographical_map.html">Geographical Map</a></li>
                    </ul>
                </div>
                
                <div class="chart-container">
                    <h3>Word Cloud</h3>
                    <img src="wordcloud.png" alt="Word Cloud" style="max-width: 100%; height: auto;">
                </div>
            </div>
        </body>
        </html>
        """
        
        # Prepare statistics cards
        stats = entities_data.get('aggregated_stats', {})
        stats_cards = ""
        for key, value in stats.items():
            formatted_key = key.replace('_', ' ').title()
            if isinstance(value, float):
                formatted_value = f"{value:.2f}"
            elif isinstance(value, int) and value > 1000:
                formatted_value = f"{value:,}"
            else:
                formatted_value = str(value)
            
            stats_cards += f"""
            <div class="stat-card">
                <h3>{formatted_value}</h3>
                <p>{formatted_key}</p>
            </div>
            """
        
        # Prepare key points
        key_points = ""
        for point in summaries_data.get('extractive_summary', [])[:5]:
            key_points += f"<li>{point}</li>"
        
        # Fill template
        html_content = html_template.format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            stats_cards=stats_cards,
            overall_summary=summaries_data.get('overall_summary', 'No summary available'),
            key_points=key_points
        )
        
        # Save dashboard
        with open('outputs/charts/dashboard.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_content
    
    def generate_all_visualizations(self, entities_file, summaries_file):
        """Generate all visualizations and dashboard"""
        # Load data
        entities_data = self.load_entities(entities_file)
        
        try:
            with open(summaries_file, 'r', encoding='utf-8') as f:
                summaries_data = json.load(f)
        except FileNotFoundError:
            print(f"Summaries file {summaries_file} not found!")
            summaries_data = {}
        
        if not entities_data:
            print("No entities data available for visualization")
            return
        
        print("Creating visualizations...")
        
        # Generate all charts
        self.create_entity_distribution_chart(entities_data)
        print("✓ Entity distribution chart created")
        
        self.create_acreage_analysis(entities_data)
        print("✓ Acreage analysis created")
        
        self.create_money_timeline(entities_data)
        print("✓ Money timeline created")
        
        self.create_ownership_network(entities_data)
        print("✓ Ownership network created")
        
        self.create_word_cloud(summaries_data)
        print("✓ Word cloud created")
        
        self.create_geographical_visualization(entities_data)
        print("✓ Geographical map created")
        
        self.create_comprehensive_dashboard(entities_data, summaries_data)
        print("✓ Comprehensive dashboard created")
        
        print("\nAll visualizations completed!")
        print("Check the 'outputs/charts/' directory for all generated files.")
        print("Open 'dashboard.html' for a comprehensive overview.")

def main():
    """Test the visualization functionality"""
    visualizer = LandDataVisualizer()
    
    # Generate all visualizations
    visualizer.generate_all_visualizations(
        'data/processed/extracted_entities.json',
        'data/summaries/summaries.json'
    )

if __name__ == "__main__":
    main()