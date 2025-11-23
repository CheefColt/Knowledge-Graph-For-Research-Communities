import pandas as pd
import numpy as np
from neo4j import GraphDatabase
from collections import Counter
import os

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "majorproject"

def fetch_graph_metrics():
    """Fetch comprehensive graph metrics from Neo4j"""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    metrics = {}
    
    with driver.session() as session:
        # Basic node counts
        print("Fetching node counts...")
        metrics['author_count'] = session.run("MATCH (a:Author) RETURN count(a) AS cnt").single()['cnt']
        metrics['paper_count'] = session.run("MATCH (p:Paper) RETURN count(p) AS cnt").single()['cnt']
        metrics['journal_count'] = session.run("MATCH (j:Journal) RETURN count(j) AS cnt").single()['cnt']
        
        # Check if Coauthorship nodes exist
        try:
            metrics['coauthorship_count'] = session.run("MATCH (c:Coauthorship) RETURN count(c) AS cnt").single()['cnt']
        except:
            metrics['coauthorship_count'] = 0
        
        # Relationship counts
        print("Fetching relationship counts...")
        metrics['wrote_count'] = session.run("MATCH ()-[r:WROTE]->() RETURN count(r) AS cnt").single()['cnt']
        metrics['published_in_count'] = session.run("MATCH ()-[r:PUBLISHED_IN]->() RETURN count(r) AS cnt").single()['cnt']
        
        try:
            metrics['coauthored_count'] = session.run("MATCH ()-[r:COAUTHORED]->() RETURN count(r) AS cnt").single()['cnt']
        except:
            metrics['coauthored_count'] = 0
        
        # Author degree statistics (papers per author)
        print("Calculating author degree statistics...")
        result = session.run("""
            MATCH (a:Author)-[:WROTE]->(p:Paper)
            RETURN a.name AS author, count(p) AS papers
        """)
        author_papers = [r['papers'] for r in result]
        
        metrics['mean_author_degree'] = np.mean(author_papers) if author_papers else 0
        metrics['median_author_degree'] = np.median(author_papers) if author_papers else 0
        metrics['max_author_degree'] = max(author_papers) if author_papers else 0
        
        # Top 10 authors by paper count
        print("Fetching top authors...")
        result = session.run("""
            MATCH (a:Author)-[:WROTE]->(p:Paper)
            RETURN a.name AS author, count(p) AS papers, a.communityId AS community
            ORDER BY papers DESC
            LIMIT 10
        """)
        metrics['top_authors'] = [dict(r) for r in result]
        
        # Community statistics
        print("Calculating community statistics...")
        result = session.run("""
            MATCH (a:Author)
            WHERE a.communityId IS NOT NULL
            RETURN a.communityId AS community, count(a) AS size
            ORDER BY size DESC
        """)
        communities = [r['size'] for r in result]
        
        if communities:
            metrics['num_communities'] = len(communities)
            metrics['largest_community'] = max(communities)
            metrics['median_community_size'] = int(np.median(communities))
            metrics['mean_community_size'] = np.mean(communities)
            metrics['singleton_communities'] = sum(1 for s in communities if s == 1)
            metrics['large_communities'] = sum(1 for s in communities if s > 10)
        else:
            metrics['num_communities'] = 0
            metrics['largest_community'] = 0
            metrics['median_community_size'] = 0
            metrics['mean_community_size'] = 0
            metrics['singleton_communities'] = 0
            metrics['large_communities'] = 0
        
        # Top 5 communities
        result = session.run("""
            MATCH (a:Author)
            WHERE a.communityId IS NOT NULL
            RETURN a.communityId AS community, count(a) AS size
            ORDER BY size DESC
            LIMIT 5
        """)
        metrics['top_communities'] = [dict(r) for r in result]
        
        # Network density (for author collaboration network)
        print("Calculating network density...")
        n = metrics['author_count']
        if metrics['coauthored_count'] > 0:
            # Density = 2*edges / (n*(n-1)) for undirected graph
            metrics['network_density'] = (2 * metrics['coauthored_count']) / (n * (n - 1)) if n > 1 else 0
        else:
            # Approximate using WROTE relationships
            metrics['network_density'] = 0.0  # Would need COAUTHOR edges
        
        # Try to get modularity if available from GDS
        try:
            result = session.run("""
                CALL gds.graph.exists('authorGraph') YIELD exists
                RETURN exists
            """)
            if result.single()['exists']:
                # Try to get stored modularity
                print("Graph projection exists, but modularity not directly accessible without re-running")
                metrics['modularity'] = None
            else:
                metrics['modularity'] = None
        except:
            metrics['modularity'] = None
    
    driver.close()
    return metrics

def analyze_csv_data():
    """Analyze CSV files for additional metrics"""
    csv_metrics = {}
    
    # Analyze research_csv.csv
    if os.path.exists('research_csv.csv'):
        print("\nAnalyzing research_csv.csv...")
        df = pd.read_csv('research_csv.csv', encoding='utf-8')
        
        # Authors per paper
        authors_per_paper = df['Authors'].str.split(',').apply(len)
        csv_metrics['mean_authors_per_paper'] = authors_per_paper.mean()
        csv_metrics['median_authors_per_paper'] = authors_per_paper.median()
        csv_metrics['max_authors_per_paper'] = authors_per_paper.max()
        csv_metrics['min_authors_per_paper'] = authors_per_paper.min()
    
    # Analyze predicted_coauthorships.csv
    if os.path.exists('predicted_coauthorships.csv'):
        print("Analyzing predicted_coauthorships.csv...")
        df_pred = pd.read_csv('predicted_coauthorships.csv')
        
        csv_metrics['total_author_pairs'] = len(df_pred)
        csv_metrics['cosine_mean'] = df_pred['cosine_similarity'].mean()
        csv_metrics['cosine_std'] = df_pred['cosine_similarity'].std()
        csv_metrics['cosine_min'] = df_pred['cosine_similarity'].min()
        csv_metrics['cosine_max'] = df_pred['cosine_similarity'].max()
        
        csv_metrics['jaccard_mean'] = df_pred['jaccard_similarity'].mean()
        csv_metrics['jaccard_std'] = df_pred['jaccard_similarity'].std()
        csv_metrics['jaccard_min'] = df_pred['jaccard_similarity'].min()
        csv_metrics['jaccard_max'] = df_pred['jaccard_similarity'].max()
        
        csv_metrics['avg_score_mean'] = df_pred['average_score'].mean()
        csv_metrics['avg_score_std'] = df_pred['average_score'].std()
        csv_metrics['avg_score_min'] = df_pred['average_score'].min()
        csv_metrics['avg_score_max'] = df_pred['average_score'].max()
        
        # Top predictions
        top_preds = df_pred.nlargest(10, 'average_score')
        csv_metrics['top_predictions'] = top_preds.to_dict('records')
        
        # High scoring pairs (> 0.7)
        csv_metrics['high_score_pairs'] = len(df_pred[df_pred['average_score'] > 0.7])
    
    # Analyze community_detection_table.csv
    if os.path.exists('community_detection_table.csv'):
        print("Analyzing community_detection_table.csv...")
        df_comm = pd.read_csv('community_detection_table.csv')
        
        # Community size distribution
        comm_sizes = df_comm.groupby('a.communityId').size()
        csv_metrics['community_sizes_from_csv'] = {
            'count': len(comm_sizes),
            'mean': comm_sizes.mean(),
            'median': comm_sizes.median(),
            'max': comm_sizes.max(),
            'min': comm_sizes.min()
        }
    
    return csv_metrics

def print_results(metrics, csv_metrics):
    """Print all metrics in a formatted way"""
    print("\n" + "="*60)
    print("GRAPH METRICS (from Neo4j)")
    print("="*60)
    
    print("\n1. DATASET STATISTICS & GRAPH CONSTRUCTION")
    print(f"   - Author nodes: {metrics['author_count']}")
    print(f"   - Paper nodes: {metrics['paper_count']}")
    print(f"   - Journal nodes: {metrics['journal_count']}")
    print(f"   - Coauthorship nodes: {metrics['coauthorship_count']}")
    print(f"   - WROTE relationships: {metrics['wrote_count']}")
    print(f"   - PUBLISHED_IN relationships: {metrics['published_in_count']}")
    print(f"   - COAUTHORED relationships: {metrics['coauthored_count']}")
    
    if 'mean_authors_per_paper' in csv_metrics:
        print(f"\n   Authors per paper:")
        print(f"   - Mean: {csv_metrics['mean_authors_per_paper']:.2f}")
        print(f"   - Median: {csv_metrics['median_authors_per_paper']:.1f}")
        print(f"   - Range: {csv_metrics['min_authors_per_paper']}-{csv_metrics['max_authors_per_paper']}")
    
    print("\n2. COMMUNITY DETECTION RESULTS")
    print(f"   - Number of communities: {metrics['num_communities']}")
    print(f"   - Largest community size: {metrics['largest_community']}")
    print(f"   - Median community size: {metrics['median_community_size']}")
    print(f"   - Mean community size: {metrics['mean_community_size']:.2f}")
    print(f"   - Singleton communities: {metrics['singleton_communities']}")
    print(f"   - Communities with >10 members: {metrics['large_communities']}")
    if metrics['modularity']:
        print(f"   - Modularity score: {metrics['modularity']:.4f}")
    
    print("\n   Top 5 communities by size:")
    for comm in metrics['top_communities']:
        print(f"   - Community {comm['community']}: {comm['size']} members")
    
    print("\n3. NETWORK STRUCTURE & TOPOLOGY")
    print(f"   - Mean author degree (papers per author): {metrics['mean_author_degree']:.2f}")
    print(f"   - Median author degree: {metrics['median_author_degree']:.1f}")
    print(f"   - Max author degree: {metrics['max_author_degree']}")
    if metrics['network_density'] > 0:
        print(f"   - Network density: {metrics['network_density']:.6f}")
    
    print("\n   Top 10 most prolific authors:")
    for i, author in enumerate(metrics['top_authors'], 1):
        comm = author['community'] if author['community'] is not None else 'N/A'
        print(f"   {i}. {author['author']}: {author['papers']} papers (Community: {comm})")
    
    if 'total_author_pairs' in csv_metrics:
        print("\n4. LINK PREDICTION PERFORMANCE")
        print(f"   - Total author pairs evaluated: {csv_metrics['total_author_pairs']:,}")
        print(f"\n   Cosine similarity:")
        print(f"   - Mean: {csv_metrics['cosine_mean']:.4f}")
        print(f"   - Std: {csv_metrics['cosine_std']:.4f}")
        print(f"   - Range: [{csv_metrics['cosine_min']:.4f}, {csv_metrics['cosine_max']:.4f}]")
        
        print(f"\n   Jaccard similarity:")
        print(f"   - Mean: {csv_metrics['jaccard_mean']:.4f}")
        print(f"   - Std: {csv_metrics['jaccard_std']:.4f}")
        print(f"   - Range: [{csv_metrics['jaccard_min']:.4f}, {csv_metrics['jaccard_max']:.4f}]")
        
        print(f"\n   Average (hybrid) score:")
        print(f"   - Mean: {csv_metrics['avg_score_mean']:.4f}")
        print(f"   - Std: {csv_metrics['avg_score_std']:.4f}")
        print(f"   - Range: [{csv_metrics['avg_score_min']:.4f}, {csv_metrics['avg_score_max']:.4f}]")
        
        print(f"\n   High-scoring pairs (>0.7): {csv_metrics['high_score_pairs']}")
        
        print("\n   Top 10 predicted collaborations:")
        for i, pred in enumerate(csv_metrics['top_predictions'], 1):
            print(f"   {i}. {pred['author1']} <-> {pred['author2']}")
            print(f"      Cosine: {pred['cosine_similarity']:.4f}, Jaccard: {pred['jaccard_similarity']:.4f}, Avg: {pred['average_score']:.4f}")

def save_to_file(metrics, csv_metrics):
    """Save metrics to a text file"""
    with open('calculated_metrics.txt', 'w', encoding='utf-8') as f:
        f.write("COMPLETE METRICS REPORT\n")
        f.write("="*60 + "\n\n")
        
        f.write("GRAPH STATISTICS:\n")
        f.write(f"Author nodes: {metrics['author_count']}\n")
        f.write(f"Paper nodes: {metrics['paper_count']}\n")
        f.write(f"Journal nodes: {metrics['journal_count']}\n")
        f.write(f"Coauthorship nodes: {metrics['coauthorship_count']}\n")
        f.write(f"WROTE relationships: {metrics['wrote_count']}\n")
        f.write(f"PUBLISHED_IN relationships: {metrics['published_in_count']}\n")
        f.write(f"COAUTHORED relationships: {metrics['coauthored_count']}\n\n")
        
        if 'mean_authors_per_paper' in csv_metrics:
            f.write(f"Mean authors per paper: {csv_metrics['mean_authors_per_paper']:.2f}\n")
            f.write(f"Median authors per paper: {csv_metrics['median_authors_per_paper']:.1f}\n\n")
        
        f.write("COMMUNITY STATISTICS:\n")
        f.write(f"Number of communities: {metrics['num_communities']}\n")
        f.write(f"Largest community: {metrics['largest_community']}\n")
        f.write(f"Mean community size: {metrics['mean_community_size']:.2f}\n\n")
        
        if 'total_author_pairs' in csv_metrics:
            f.write("LINK PREDICTION METRICS:\n")
            f.write(f"Total pairs: {csv_metrics['total_author_pairs']}\n")
            f.write(f"Cosine mean: {csv_metrics['cosine_mean']:.4f}\n")
            f.write(f"Jaccard mean: {csv_metrics['jaccard_mean']:.4f}\n")
            f.write(f"Average score mean: {csv_metrics['avg_score_mean']:.4f}\n")
    
    print(f"\nMetrics saved to: calculated_metrics.txt")

if __name__ == "__main__":
    try:
        print("Starting metric calculation...")
        print("This may take a few minutes depending on graph size.\n")
        
        # Fetch from Neo4j
        metrics = fetch_graph_metrics()
        
        # Analyze CSVs
        csv_metrics = analyze_csv_data()
        
        # Print results
        print_results(metrics, csv_metrics)
        
        # Save to file
        save_to_file(metrics, csv_metrics)
        
        print("\n" + "="*60)
        print("Calculation complete!")
        print("="*60)
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure:")
        print("1. Neo4j is running")
        print("2. Database credentials are correct")
        print("3. Graph has been imported")
        print("4. CSV files exist in the current directory")
