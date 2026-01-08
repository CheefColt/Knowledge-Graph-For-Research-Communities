import re
from neo4j import GraphDatabase
import pandas as pd

# Neo4j connection details
uri = "bolt://localhost:7687"
user = "neo4j"
password = "majorproject"

def create_count_nodes_for_visualization(uri, user, password):
    """
    Creates PublicationCount nodes that display the paper count
    The actual journal info is stored as properties
    """
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # First, delete any existing PublicationCount nodes
        print("Cleaning up old PublicationCount nodes...")
        session.run("MATCH (pc:PublicationCount) DETACH DELETE pc")
        
        # Create PublicationCount nodes with count as the display name
        query = """
        MATCH (j:Journal)-[r:PUBLISHED_IN_YEAR]->(y:Year)
        WITH j, y, r.paperCount AS count
        MERGE (pc:PublicationCount {
            id: j.name + '_' + y.value,
            displayName: toString(count),
            count: count,
            journalName: j.name,
            year: y.value
        })
        MERGE (pc)-[:IN_YEAR]->(y)
        SET pc.count = count
        RETURN pc.displayName AS Display, pc.journalName AS Journal, 
               pc.year AS Year, pc.count AS Count
        """
        
        result = session.run(query)
        
        print("\nCreated PublicationCount nodes:")
        count_created = 0
        for record in result:
            if count_created < 10:  # Show first 10 as examples
                print(f"  Display: {record['Display']} papers | Journal: {record['Journal']} | Year: {record['Year']}")
            count_created += 1
        
        print(f"\n✓ Created {count_created} PublicationCount nodes!")
        print("\nNow use this query in Neo4j Browser:")
        print("MATCH (pc:PublicationCount)-[:IN_YEAR]->(y:Year)")
        print("RETURN pc, y")
        print("LIMIT 100")
        print("\nThe nodes will show the count as the label!")
        print("Click on any node to see the full journal name in properties.")
    
    driver.close()

if __name__ == "__main__":
    create_count_nodes_for_visualization(uri, user, password)
