import pandas as pd
from neo4j import GraphDatabase
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer
from itertools import combinations
import numpy as np

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "majorproject"

def fetch_author_paper_journal():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    query = """
    MATCH (a:Author)-[:WROTE]->(p:Paper)-[:PUBLISHED_IN]->(j:Journal)
    RETURN a.name AS author, p.title AS paper, j.name AS journal
    """
    with driver.session() as session:
        result = session.run(query)
        data = [r.data() for r in result]
    driver.close()
    return pd.DataFrame(data)

def build_feature_matrix(df):
    # Each author: set of papers and journals
    author_papers = df.groupby('author')['paper'].apply(set)
    author_journals = df.groupby('author')['journal'].apply(set)
    # One-hot encode papers and journals
    mlb_paper = MultiLabelBinarizer()
    mlb_journal = MultiLabelBinarizer()
    paper_matrix = mlb_paper.fit_transform(author_papers)
    journal_matrix = mlb_journal.fit_transform(author_journals)
    # Concatenate features
    feature_matrix = np.hstack([paper_matrix, journal_matrix])
    authors = author_papers.index.tolist()
    return feature_matrix, authors

def compute_similarity_table(feature_matrix, authors):
    # Cosine similarity
    cos_sim = cosine_similarity(feature_matrix)
    # Jaccard similarity (for binary vectors)
    def jaccard(u, v):
        intersection = np.logical_and(u, v).sum()
        union = np.logical_or(u, v).sum()
        return intersection / union if union > 0 else 0
    jac_sim = np.zeros_like(cos_sim)
    for i in range(len(authors)):
        for j in range(len(authors)):
            jac_sim[i, j] = jaccard(feature_matrix[i], feature_matrix[j])
    # Average similarity
    avg_sim = (cos_sim + jac_sim) / 2
    # Build table for possible future links (exclude existing coauthorships)
    pairs = list(combinations(range(len(authors)), 2))
    rows = []
    for i, j in pairs:
        rows.append({
            'author1': authors[i],
            'author2': authors[j],
            'cosine_similarity': cos_sim[i, j],
            'jaccard_similarity': jac_sim[i, j],
            'average_score': avg_sim[i, j]
        })
    return pd.DataFrame(rows)

def main():
    df = fetch_author_paper_journal()
    feature_matrix, authors = build_feature_matrix(df)
    sim_table = compute_similarity_table(feature_matrix, authors)
    sim_table = sim_table.sort_values('average_score', ascending=False)
    sim_table.to_csv('predicted_coauthorships.csv', index=False)
    print(sim_table.head(20))

if __name__ == "__main__":
    main()
