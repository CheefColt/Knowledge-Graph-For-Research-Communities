// ====================================================================
// YEAR → COUNT NODES (Journal counts as node labels)
// ====================================================================

// Option 1: Create a view with count as the display name
// This query shows journals with their paper count as the main label
MATCH (j:Journal)-[r:PUBLISHED_IN_YEAR]->(y:Year)
WITH j, y, r.paperCount AS count
RETURN y, 
       {name: toString(count), fullName: j.name, count: count} AS countNode,
       count
ORDER BY y.value, count DESC
LIMIT 100;

// Option 2: Better visualization - shows Year with count nodes
// The count appears as the node, journal details available on click
MATCH (j:Journal)-[r:PUBLISHED_IN_YEAR]->(y:Year)
RETURN y.value AS Year, 
       r.paperCount AS Count,
       j.name AS JournalName
ORDER BY Year, Count DESC
LIMIT 100;

// Option 3: For graph visualization with counts as labels
// Use this in Neo4j Browser and style the nodes
MATCH (j:Journal)-[r:PUBLISHED_IN_YEAR]->(y:Year)
WITH y, j, r.paperCount AS paperCount
RETURN y, 
       {id: id(j), 
        label: toString(paperCount), 
        name: j.name, 
        count: paperCount} AS journal,
       paperCount
LIMIT 100;
