import csv
from neo4j import GraphDatabase

# Update these with your Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "majorproject"

CSV_PATH = "research_csv.csv"

def create_graph():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        with open(CSV_PATH, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row["Title"].strip()
                journal = row["Source title"].strip()
                doc_type = row["Document Type"].strip()
                authors = [a.strip() for a in row["Authors"].split(",") if a.strip()]

                # Create Journal node
                session.run(
                    "MERGE (j:Journal {name: $journal})",
                    journal=journal
                )
                # Create Paper node
                session.run(
                    "MERGE (p:Paper {title: $title}) SET p.document_type = $doc_type",
                    title=title, doc_type=doc_type
                )
                # Create relationship Paper-PUBLISHED_IN->Journal
                session.run(
                    "MATCH (p:Paper {title: $title}), (j:Journal {name: $journal}) "
                    "MERGE (p)-[:PUBLISHED_IN]->(j)",
                    title=title, journal=journal
                )
                # Create Author nodes and relationships
                for author in authors:
                    session.run(
                        "MERGE (a:Author {name: $author})",
                        author=author
                    )
                    session.run(
                        "MATCH (a:Author {name: $author}), (p:Paper {title: $title}) "
                        "MERGE (a)-[:WROTE]->(p)",
                        author=author, title=title
                    )
                # Create Coauthorship node for each paper
                session.run(
                    "MERGE (c:Coauthorship {title: $title, journal: $journal, document_type: $doc_type})",
                    title=title, journal=journal, doc_type=doc_type
                )
                # Connect each author to the Coauthorship node
                for author in authors:
                    session.run(
                        "MATCH (a:Author {name: $author}), (c:Coauthorship {title: $title}) "
                        "MERGE (a)-[:COAUTHORED]->(c)",
                        author=author, title=title
                    )
    driver.close()

if __name__ == "__main__":
    create_graph()
    print("Graph import complete.")
