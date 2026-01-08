import re
from neo4j import GraphDatabase
import pandas as pd

# Neo4j connection details
uri = "bolt://localhost:7687"
user = "neo4j"
password = "majorproject"

def create_journal_year_relationships(uri, user, password):
    """
    Creates relationships from Journal nodes to Year nodes
    with a count property showing number of papers
    """
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Create PUBLISHED_IN_YEAR relationships from Journal to Year with paper count
        query = """
        MATCH (j:Journal)<-[:PUBLISHED_IN]-(p:Paper)-[:PUBLISHED_IN_YEAR]->(y:Year)
        WITH j, y, COUNT(p) AS paperCount
        MERGE (j)-[r:PUBLISHED_IN_YEAR]->(y)
        SET r.paperCount = paperCount
        RETURN j.name AS Journal, y.value AS Year, paperCount
        """
        
        result = session.run(query)
        
        print("Created Journal->Year relationships with paper counts:")
        for record in result:
            print(f"  {record['Journal']} -> {record['Year']}: {record['paperCount']} papers")
    
    driver.close()
    print("\n✓ Journal-Year relationships created successfully!")

if __name__ == "__main__":
    create_journal_year_relationships(uri, user, password)
