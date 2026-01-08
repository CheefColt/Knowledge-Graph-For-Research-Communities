import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import json
import math

# Read the CSV file
csv_file = "research_csv.csv"
df = pd.read_csv(csv_file, encoding='ISO-8859-1')

print(f"Loaded {len(df)} papers from {csv_file}\n")

# Create a graph: Year -> Count nodes (where count represents paper count)
G = nx.DiGraph()

# Dictionary to store publication-year-paper counts
pub_year_counts = defaultdict(lambda: defaultdict(int))

# Process each paper
for index, row in df.iterrows():
    journal = str(row['Source title']).strip()
    year = str(row['Year']).strip()
    
    # Count papers per publication per year
    pub_year_counts[year][journal] += 1

# Create nodes and edges
count_node_details = []

for year in sorted(pub_year_counts.keys()):
    year_node = f"Year_{year}"
    G.add_node(year_node, node_type='year', label=year, display=year)
    
    # For each publication in this year, create a count node
    for pub, count in pub_year_counts[year].items():
        # Create unique count node
        count_node = f"Count_{year}_{pub[:30]}"  # Unique identifier
        
        # Add node with count as the display label
        G.add_node(count_node, 
                   node_type='count', 
                   label=str(count),  # Display the count
                   display=str(count),
                   publication=pub,
                   year=year,
                   paper_count=count)
        
        # Edge from count to year
        G.add_edge(count_node, year_node)
        
        count_node_details.append({
            'Year': year,
            'Count': count,
            'Publication': pub
        })

print("=" * 80)
print("YEAR-WISE PUBLICATION COUNTS (Neo4j Style)")
print("=" * 80)

# Show summary for each year
for year in sorted(pub_year_counts.keys()):
    total_papers = sum(pub_year_counts[year].values())
    total_pubs = len(pub_year_counts[year])
    print(f"\n{year}: {total_papers} papers across {total_pubs} publications")
    
    # Show top counts
    top_counts = sorted(pub_year_counts[year].values(), reverse=True)[:5]
    print(f"  Top paper counts: {', '.join(map(str, top_counts))}")

# Create visualization similar to Neo4j
print("\n" + "=" * 80)
print("CREATING NEO4J-STYLE VISUALIZATION...")
print("=" * 80)

# Filter to show specific years including 2024
top_years_by_count = sorted(pub_year_counts.keys(), 
                            key=lambda y: sum(pub_year_counts[y].values()), 
                            reverse=True)[:5]
# Add 2024 if not already in top 5
if '2024' not in top_years_by_count:
    top_years = top_years_by_count + ['2024']
else:
    top_years = top_years_by_count

print(f"Visualizing {len(top_years)} years: {', '.join(sorted(top_years, reverse=True))}")

# Create subgraph with more counts per year
nodes_to_show = set()
for year in top_years:
    year_node = f"Year_{year}"
    nodes_to_show.add(year_node)
    
    # Get all count nodes for this year
    count_nodes = [n for n in G.nodes() if G.nodes[n].get('year') == year]
    
    # Take top 20 by count for each year (increased from 10)
    sorted_counts = sorted(count_nodes, 
                          key=lambda n: G.nodes[n].get('paper_count', 0), 
                          reverse=True)[:20]
    nodes_to_show.update(sorted_counts)

G_viz = G.subgraph(nodes_to_show).copy()

# Create layout - Original circular style with years in center
plt.figure(figsize=(20, 20), facecolor='#1a1a1a')
ax = plt.gca()
ax.set_facecolor('#1a1a1a')

# Manual positioning: years in center circle, counts around them
pos = {}
year_nodes_list = [n for n in G_viz.nodes() if G_viz.nodes[n].get('node_type') == 'year']
count_nodes_list = [n for n in G_viz.nodes() if G_viz.nodes[n].get('node_type') == 'count']

# Sort years chronologically
year_nodes_sorted = sorted(year_nodes_list, key=lambda n: G_viz.nodes[n]['label'])

# Position year nodes in the center (arranged in a circle)
num_years = len(year_nodes_sorted)
year_radius = 2.5
for i, year_node in enumerate(year_nodes_sorted):
    angle = 2 * math.pi * i / num_years
    x = year_radius * math.cos(angle)
    y = year_radius * math.sin(angle)
    pos[year_node] = (x, y)

# Position count nodes in circles around their respective years
for year_node in year_nodes_sorted:
    # Get count nodes connected to this year
    year_counts = [n for n in count_nodes_list if G_viz.has_edge(n, year_node)]
    
    # Arrange in a circle around the year node
    year_x, year_y = pos[year_node]
    radius = 5.5  # Distance from year to count nodes
    num_counts = len(year_counts)
    
    for i, count_node in enumerate(year_counts):
        # Calculate angle for circular arrangement
        angle = 2 * math.pi * i / num_counts
        x = year_x + radius * math.cos(angle)
        y = year_y + radius * math.sin(angle)
        pos[count_node] = (x, y)
        x = year_x + radius * math.cos(angle)
        y = year_y + radius * math.sin(angle)
        pos[count_node] = (x, y)

# Separate nodes
year_nodes = [n for n in G_viz.nodes() if G_viz.nodes[n].get('node_type') == 'year']
count_nodes = [n for n in G_viz.nodes() if G_viz.nodes[n].get('node_type') == 'count']

# Color palette for different years
year_color_map = {}
color_palette = ['#42A5F5', '#66BB6A', '#EC407A', '#AB47BC', '#FFA726', '#26C6DA']
for i, year_node in enumerate(year_nodes_sorted):
    year = G_viz.nodes[year_node]['label']
    year_color_map[year] = color_palette[i % len(color_palette)]

# Draw edges with better styling
nx.draw_networkx_edges(G_viz, pos, 
                       edge_color='#555555',
                       arrows=True,
                       arrowsize=12,
                       width=1.0,
                       alpha=0.25,
                       connectionstyle='arc3,rad=0',
                       node_size=100)

# Draw count nodes with distinct colors per year for better grouping
count_node_sizes = []
count_node_colors = []

for node in count_nodes:
    paper_count = G_viz.nodes[node].get('paper_count', 1)
    year = G_viz.nodes[node].get('year')
    
    # Size based on paper count
    count_node_sizes.append(paper_count * 60 + 300)
    
    # Color based on year (not count)
    base_color = year_color_map.get(year, '#66BB6A')
    count_node_colors.append(base_color)

nx.draw_networkx_nodes(G_viz, pos,
                       nodelist=count_nodes,
                       node_color=count_node_colors,
                       node_size=count_node_sizes,
                       node_shape='o',
                       edgecolors='white',
                       linewidths=1.5,
                       alpha=0.9)

# Draw year nodes with same color as their count nodes
year_node_colors = []
year_node_edge_colors = []
for year_node in year_nodes:
    year = G_viz.nodes[year_node]['label']
    color = year_color_map.get(year, '#FFA726')
    year_node_colors.append(color)
    # Darker version for edge
    year_node_edge_colors.append(color)

nx.draw_networkx_nodes(G_viz, pos,
                       nodelist=year_nodes,
                       node_color=year_node_colors,
                       node_size=4000,
                       node_shape='o',
                       edgecolors=year_node_edge_colors,
                       linewidths=3,
                       alpha=1.0)

# Draw labels - ONLY show the count number for count nodes
year_labels = {n: G_viz.nodes[n]['display'] for n in year_nodes}
count_labels = {n: G_viz.nodes[n]['label'] for n in count_nodes}  # Just the number

nx.draw_networkx_labels(G_viz, pos, year_labels,
                        font_size=16,
                        font_weight='bold',
                        font_color='black',
                        font_family='Arial')

nx.draw_networkx_labels(G_viz, pos, count_labels,
                        font_size=8,
                        font_weight='bold',
                        font_color='white',
                        font_family='Arial')

plt.title('Year-wise Publication Counts\n' +
          f'Showing {len(top_years)} years (2019-2024) with top 20 publications each\n' +
          'Count nodes show paper count | Node size = paper count',
          fontsize=18, fontweight='bold', color='white', pad=20)

plt.axis('off')
plt.tight_layout()

# Save
plt.savefig('neo4j_style_year_counts.png', dpi=300, bbox_inches='tight', facecolor='#1a1a1a')
print("✓ Neo4j-style visualization saved to 'neo4j_style_year_counts.png'")

# Create an interactive HTML version with publication details
print("\n" + "=" * 80)
print("CREATING INTERACTIVE HTML VISUALIZATION...")
print("=" * 80)

# Save node details for reference
detail_df = pd.DataFrame(count_node_details)
detail_df = detail_df.sort_values(['Year', 'Count'], ascending=[True, False])
detail_df.to_csv('count_node_details.csv', index=False, encoding='utf-8')
print("✓ Count node details saved to 'count_node_details.csv'")

# Create a simple HTML with table
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Year-wise Publication Counts</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1e1e1e; color: white; }
        h1 { color: #FFE4B5; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #555; padding: 12px; text-align: left; }
        th { background-color: #333; font-weight: bold; }
        tr:hover { background-color: #2b2b2b; }
        .year-section { margin-top: 30px; border-top: 2px solid #FFE4B5; padding-top: 20px; }
        .count { font-size: 24px; font-weight: bold; color: #4CAF50; }
        .pub { color: #ccc; }
    </style>
</head>
<body>
    <h1>📊 Year-wise Publication Counts (Neo4j Style)</h1>
    <p>Each count represents the number of papers in a publication for that year.</p>
"""

for year in sorted(pub_year_counts.keys(), reverse=True):
    html_content += f'<div class="year-section"><h2>📅 Year: {year}</h2><table>'
    html_content += '<tr><th>Count</th><th>Publication</th></tr>'
    
    sorted_pubs = sorted(pub_year_counts[year].items(), key=lambda x: x[1], reverse=True)
    
    for pub, count in sorted_pubs:
        html_content += f'<tr><td class="count">{count}</td><td class="pub">{pub}</td></tr>'
    
    html_content += '</table></div>'

html_content += """
</body>
</html>
"""

with open('year_publication_counts.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✓ Interactive HTML saved to 'year_publication_counts.html'")

plt.show()

print("\n" + "=" * 80)
print("VISUALIZATION COMPLETE!")
print("=" * 80)
print("Generated files:")
print("  1. neo4j_style_year_counts.png - Neo4j-style network graph")
print("  2. count_node_details.csv - Full details for all count nodes")
print("  3. year_publication_counts.html - Interactive table view")
print("\nIn the graph:")
print("  - Year nodes (beige/orange) show the year")
print("  - Count nodes (green) show ONLY the paper count")
print("  - Node size = number of papers")
print("  - Check count_node_details.csv to see which publication each count represents")
