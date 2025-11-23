import re
from neo4j import GraphDatabase
import pandas as pd

# Neo4j connection details
uri = "bolt://localhost:7687"
user = "neo4j"
password = "majorproject"
csv_file = "research_csv.csv"

def clean_author(author):
    author = author.strip()
    author = re.sub(r'\s+', ' ', author)
    author = author.rstrip('.')
    author = author.title()
    return author

def import_csv_to_neo4j(uri, user, password, csv_file):
    # Read CSV, handle missing Document Type column
    try:
        df = pd.read_csv(csv_file, encoding='ISO-8859-1', usecols=['Authors', 'Title', 'Source title', 'Document Type'])
    except Exception as e:
        print('Error reading with usecols:', e)
        df = pd.read_csv(csv_file, encoding='ISO-8859-1')
        # Add Document Type column if it doesn't exist
        if 'Document Type' not in df.columns:
            df['Document Type'] = 'Unknown'
    print('DataFrame columns:', df.columns)

    # Use exact column names from DataFrame
    author_col = 'Authors'

    # Print a few sample authors for debugging
    print('Sample parsed authors:')
    for i in range(min(5, len(df))):
        authors_field = str(df.iloc[i][author_col])
        if authors_field.startswith('"') and authors_field.endswith('"'):
            authors_field = authors_field[1:-1]
        print('Raw authors_field:', repr(authors_field))
    # Split by comma (since authors are separated by commas)
    authors = [a.strip() for a in authors_field.split(",") if a.strip()]
    print(authors)

    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        for index, row in df.iterrows():
            authors_field = str(row[author_col])
            if authors_field.startswith('"') and authors_field.endswith('"'):
                authors_field = authors_field[1:-1]
            authors = [a.strip() for a in authors_field.split(",") if a.strip()]
            title = str(row['Title']).replace("'", "\\'")
            journal = str(row['Source title']).replace("'", "\\'")
            doc_type = str(row['Document Type']).replace("'", "\\'")

            # Create Paper node
            session.run(f"MERGE (p:Paper {{title: '{title}'}})")

            # Create Journal node
            session.run(f"MERGE (j:Journal {{name: '{journal}'}})")

            # Create DocumentType node
            session.run(f"MERGE (d:DocumentType {{type: '{doc_type}'}})")

            # Link Paper to Journal
            session.run(f"""
                MATCH (p:Paper {{title: '{title}'}})
                MATCH (j:Journal {{name: '{journal}'}})
                MERGE (p)-[:PUBLISHED_IN]->(j)
            """)

            # Link Paper to DocumentType
            session.run(f"""
                MATCH (p:Paper {{title: '{title}'}})
                MATCH (d:DocumentType {{type: '{doc_type}'}})
                MERGE (p)-[:HAS_TYPE]->(d)
            """)

            # Create Author nodes and link to Paper
            for author in authors:
                author = clean_author(author.replace("'", "\\'"))
                if author:
                    session.run(f"MERGE (a:Author {{name: '{author}'}})")
                    session.run(f"""
                        MATCH (a:Author {{name: '{author}'}})
                        MATCH (p:Paper {{title: '{title}'}})
                        MERGE (a)-[:WROTE]->(p)
                    """)

    driver.close()

if __name__ == "__main__":
    import_csv_to_neo4j(uri, user, password, csv_file)