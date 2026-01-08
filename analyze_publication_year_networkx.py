import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import json

# Read the CSV file
csv_file = "research_csv.csv"
df = pd.read_csv(csv_file, encoding='ISO-8859-1')

print(f"Loaded {len(df)} papers from {csv_file}")
print(f"Columns: {df.columns.tolist()}\n")

# Create a bipartite graph: Publications and Years
G = nx.Graph()

# Dictionary to store publication-year-paper counts
pub_year_counts = defaultdict(lambda: defaultdict(int))
publication_papers = defaultdict(lambda: defaultdict(list))

# Process each paper
for index, row in df.iterrows():
    journal = str(row['Source title']).strip()
    year = str(row['Year']).strip()
    title = str(row['Title']).strip()
    
    # Count papers per publication per year
    pub_year_counts[year][journal] += 1
    publication_papers[year][journal].append(title)
    
    # Add nodes and edges to the graph
    year_node = f"Year_{year}"
    pub_node = f"Pub_{journal}"
    
    G.add_node(year_node, node_type='year', label=year)
    G.add_node(pub_node, node_type='publication', label=journal)
    
    # Edge weight = number of papers
    if G.has_edge(year_node, pub_node):
        G[year_node][pub_node]['weight'] += 1
    else:
        G.add_edge(year_node, pub_node, weight=1)

print("=" * 80)
print("YEAR-WISE PUBLICATION COUNTS")
print("=" * 80)

# Display results in a structured format
for year in sorted(pub_year_counts.keys()):
    print(f"\n📅 YEAR: {year}")
    print("-" * 80)
    
    # Sort publications by paper count (descending)
    sorted_pubs = sorted(pub_year_counts[year].items(), 
                         key=lambda x: x[1], 
                         reverse=True)
    
    total_papers = sum(count for _, count in sorted_pubs)
    print(f"Total Papers in {year}: {total_papers}")
    print(f"Total Publications: {len(sorted_pubs)}")
    print()
    
    # Show top publications
    print("Top Publications:")
    for i, (pub, count) in enumerate(sorted_pubs[:10], 1):
        # Truncate long publication names
        pub_display = pub if len(pub) <= 60 else pub[:57] + "..."
        print(f"  {i:2d}. [{count:3d} papers] {pub_display}")
    
    if len(sorted_pubs) > 10:
        print(f"  ... and {len(sorted_pubs) - 10} more publications")

print("\n" + "=" * 80)
print("GRAPH STATISTICS")
print("=" * 80)
print(f"Total Nodes: {G.number_of_nodes()}")
print(f"  - Year Nodes: {sum(1 for n, d in G.nodes(data=True) if d.get('node_type') == 'year')}")
print(f"  - Publication Nodes: {sum(1 for n, d in G.nodes(data=True) if d.get('node_type') == 'publication')}")
print(f"Total Edges (Year-Publication connections): {G.number_of_edges()}")

# Save detailed data to JSON
output_data = {
    'year_publication_counts': dict(pub_year_counts),
    'summary': {
        'total_years': len(pub_year_counts),
        'total_unique_publications': len(set(pub for year_data in pub_year_counts.values() for pub in year_data.keys())),
        'total_papers': len(df)
    }
}

with open('publication_year_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print("\n✓ Detailed data saved to 'publication_year_analysis.json'")

# Create a summary CSV
summary_rows = []
for year in sorted(pub_year_counts.keys()):
    for pub, count in pub_year_counts[year].items():
        summary_rows.append({
            'Year': year,
            'Publication': pub,
            'PaperCount': count
        })

summary_df = pd.DataFrame(summary_rows)
summary_df = summary_df.sort_values(['Year', 'PaperCount'], ascending=[True, False])
summary_df.to_csv('publication_year_summary.csv', index=False, encoding='utf-8')

print("✓ Summary saved to 'publication_year_summary.csv'")

# Visualize the top connections
print("\n" + "=" * 80)
print("CREATING VISUALIZATION...")
print("=" * 80)

# Get top N years and publications for visualization
top_years = sorted(pub_year_counts.keys(), 
                   key=lambda y: sum(pub_year_counts[y].values()), 
                   reverse=True)[:5]

# Create subgraph with top years
nodes_to_keep = set()
for year in top_years:
    year_node = f"Year_{year}"
    nodes_to_keep.add(year_node)
    
    # Add top 10 publications for this year
    top_pubs = sorted(pub_year_counts[year].items(), 
                     key=lambda x: x[1], 
                     reverse=True)[:10]
    
    for pub, _ in top_pubs:
        nodes_to_keep.add(f"Pub_{pub}")

G_viz = G.subgraph(nodes_to_keep).copy()

# Create visualization
plt.figure(figsize=(20, 14))

# Separate nodes by type for positioning
year_nodes = [n for n, d in G_viz.nodes(data=True) if d.get('node_type') == 'year']
pub_nodes = [n for n, d in G_viz.nodes(data=True) if d.get('node_type') == 'publication']

# Create bipartite layout
pos = {}
year_spacing = 1.0 / (len(year_nodes) + 1)
pub_spacing = 1.0 / (len(pub_nodes) + 1)

for i, node in enumerate(year_nodes, 1):
    pos[node] = (0.2, i * year_spacing)

for i, node in enumerate(pub_nodes, 1):
    pos[node] = (0.8, i * pub_spacing)

# Draw edges with width based on paper count
edges = G_viz.edges()
weights = [G_viz[u][v]['weight'] for u, v in edges]
max_weight = max(weights) if weights else 1

nx.draw_networkx_edges(G_viz, pos, 
                       width=[w/max_weight * 5 for w in weights],
                       alpha=0.3, 
                       edge_color='gray')

# Draw year nodes
nx.draw_networkx_nodes(G_viz, pos, 
                       nodelist=year_nodes,
                       node_color='lightblue',
                       node_size=3000,
                       node_shape='s')

# Draw publication nodes with size based on paper count
pub_node_sizes = []
for node in pub_nodes:
    # Get total papers for this publication across all years
    pub_name = G_viz.nodes[node]['label']
    total = sum(pub_year_counts[year].get(pub_name, 0) for year in pub_year_counts)
    pub_node_sizes.append(total * 100)

nx.draw_networkx_nodes(G_viz, pos,
                       nodelist=pub_nodes,
                       node_color='lightcoral',
                       node_size=pub_node_sizes,
                       node_shape='o',
                       alpha=0.7)

# Add labels
year_labels = {n: G_viz.nodes[n]['label'] for n in year_nodes}
pub_labels = {}
for n in pub_nodes:
    label = G_viz.nodes[n]['label']
    # Truncate long names for visualization
    pub_labels[n] = label if len(label) <= 30 else label[:27] + "..."

nx.draw_networkx_labels(G_viz, pos, year_labels, 
                        font_size=14, font_weight='bold')
nx.draw_networkx_labels(G_viz, pos, pub_labels, 
                        font_size=8)

# Add edge labels showing paper counts
edge_labels = {(u, v): G_viz[u][v]['weight'] for u, v in G_viz.edges()}
nx.draw_networkx_edge_labels(G_viz, pos, edge_labels, 
                             font_size=7, font_color='red')

plt.title('Year-wise Publication Network\n(Node size = paper count, Edge width = papers per year)', 
          fontsize=16, fontweight='bold')
plt.axis('off')
plt.tight_layout()

# Save the plot
plt.savefig('publication_year_network.png', dpi=300, bbox_inches='tight')
print("✓ Network visualization saved to 'publication_year_network.png'")

plt.show()

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE!")
print("=" * 80)
print("Generated files:")
print("  1. publication_year_analysis.json - Detailed data")
print("  2. publication_year_summary.csv - Summary table")
print("  3. publication_year_network.png - Network visualization")
