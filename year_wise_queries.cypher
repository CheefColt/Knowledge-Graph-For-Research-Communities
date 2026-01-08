// ====================================================================
// YEAR-WISE ANALYSIS - CYPHER QUERIES FOR NEO4J
// ====================================================================

// 1. Count papers per year (sorted by year)
MATCH (y:Year)<-[:PUBLISHED_IN_YEAR]-(p:Paper)
RETURN y.value AS Year, COUNT(p) AS NumberOfPapers
ORDER BY y.value;

// 2. Visualize year-wise publication network (limited to 100 papers)
MATCH (y:Year)<-[:PUBLISHED_IN_YEAR]-(p:Paper)
RETURN y, p
LIMIT 100;

// 3. Find most productive years (top 10)
MATCH (y:Year)<-[:PUBLISHED_IN_YEAR]-(p:Paper)
RETURN y.value AS Year, COUNT(p) AS Papers
ORDER BY Papers DESC
LIMIT 10;

// 4. Papers and authors count by year
MATCH (a:Author)-[:WROTE]->(p:Paper)-[:PUBLISHED_IN_YEAR]->(y:Year)
RETURN y.value AS Year, 
       COUNT(DISTINCT p) AS Papers, 
       COUNT(DISTINCT a) AS Authors
ORDER BY y.value;

// 5. Year-wise journal distribution
MATCH (p:Paper)-[:PUBLISHED_IN]->(j:Journal)
MATCH (p)-[:PUBLISHED_IN_YEAR]->(y:Year)
RETURN y.value AS Year, 
       j.name AS Journal, 
       COUNT(p) AS Papers
ORDER BY y.value, Papers DESC;

// 6. Top authors per year
MATCH (a:Author)-[:WROTE]->(p:Paper)-[:PUBLISHED_IN_YEAR]->(y:Year)
RETURN y.value AS Year, 
       a.name AS Author, 
       COUNT(p) AS Papers
ORDER BY y.value, Papers DESC;

// 7. Collaboration network for a specific year (e.g., 2024)
MATCH (a1:Author)-[:WROTE]->(p:Paper)-[:PUBLISHED_IN_YEAR]->(y:Year {value: '2024'})
MATCH (a2:Author)-[:WROTE]->(p)
WHERE a1 <> a2
RETURN a1, a2, p
LIMIT 100;

// 8. Year-wise document type distribution
MATCH (p:Paper)-[:HAS_TYPE]->(d:DocumentType)
MATCH (p)-[:PUBLISHED_IN_YEAR]->(y:Year)
RETURN y.value AS Year, 
       d.type AS DocumentType, 
       COUNT(p) AS Count
ORDER BY y.value, Count DESC;

// 9. All papers from a specific year with full details
MATCH (a:Author)-[:WROTE]->(p:Paper)-[:PUBLISHED_IN_YEAR]->(y:Year {value: '2024'})
MATCH (p)-[:PUBLISHED_IN]->(j:Journal)
RETURN p.title AS Title, 
       COLLECT(DISTINCT a.name) AS Authors, 
       j.name AS Journal, 
       y.value AS Year
LIMIT 50;

// 10. Year progression visualization (Years -> Papers -> Journals)
MATCH (y:Year)<-[:PUBLISHED_IN_YEAR]-(p:Paper)-[:PUBLISHED_IN]->(j:Journal)
RETURN y, p, j
LIMIT 200;

// 11. Most prolific journals per year
MATCH (p:Paper)-[:PUBLISHED_IN]->(j:Journal)
MATCH (p)-[:PUBLISHED_IN_YEAR]->(y:Year)
WITH y.value AS Year, j.name AS Journal, COUNT(p) AS Papers
WHERE Papers > 5
RETURN Year, Journal, Papers
ORDER BY Year, Papers DESC;

// 12. Research output trend (year-by-year comparison)
MATCH (p:Paper)-[:PUBLISHED_IN_YEAR]->(y:Year)
WITH y.value AS Year, COUNT(p) AS Papers
RETURN Year, Papers, 
       Papers - LAG(Papers) OVER (ORDER BY Year) AS ChangeFromPreviousYear
ORDER BY Year;
