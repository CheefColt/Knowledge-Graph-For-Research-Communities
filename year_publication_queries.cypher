// ====================================================================
// YEAR-WISE PUBLICATION QUERIES WITH COUNTS
// ====================================================================

// 1. Show papers from a specific publication (journal) in a specific year
// Replace 'Journal Name' and '2024' with your values
MATCH (p:Paper)-[:PUBLISHED_IN]->(j:Journal {name: 'International Journal of Intelligent Systems and Applications in Engineering'})
MATCH (p)-[:PUBLISHED_IN_YEAR]->(y:Year {value: '2024'})
RETURN p.title AS PaperTitle, j.name AS Journal, y.value AS Year;

// 2. Count of papers per journal per year
MATCH (p:Paper)-[:PUBLISHED_IN]->(j:Journal)
MATCH (p)-[:PUBLISHED_IN_YEAR]->(y:Year)
RETURN y.value AS Year, j.name AS Journal, COUNT(p) AS PaperCount
ORDER BY y.value, PaperCount DESC;

// 3. Visualize Year -> Journal -> Papers (with count displayed)
// This shows the year connected to journals with paper count as a property
MATCH (p:Paper)-[:PUBLISHED_IN]->(j:Journal)
MATCH (p)-[:PUBLISHED_IN_YEAR]->(y:Year)
WITH y, j, COUNT(p) AS paperCount, COLLECT(p) AS papers
RETURN y, j, paperCount, papers
LIMIT 100;

// 4. Create virtual nodes showing Year -> Count -> Journal
// This creates a visual representation with count as intermediate info
MATCH (p:Paper)-[:PUBLISHED_IN]->(j:Journal)
MATCH (p)-[:PUBLISHED_IN_YEAR]->(y:Year)
WITH y, j, COUNT(p) AS count
RETURN y.value AS Year, 
       j.name AS Journal, 
       count AS NumberOfPapers
ORDER BY Year, NumberOfPapers DESC;

// 5. Show Year nodes with aggregated counts to Journals
// Creates a nice visualization: Year -> (count) -> Journal
MATCH (p:Paper)-[:PUBLISHED_IN]->(j:Journal)
MATCH (p)-[:PUBLISHED_IN_YEAR]->(y:Year)
WITH y, j, COUNT(p) AS paperCount
WHERE paperCount > 0
RETURN y, j, paperCount
ORDER BY y.value, paperCount DESC
LIMIT 50;

// 6. Papers in a specific journal for a specific year with full details
MATCH (a:Author)-[:WROTE]->(p:Paper)-[:PUBLISHED_IN]->(j:Journal {name: 'Journal of Molecular Structure'})
MATCH (p)-[:PUBLISHED_IN_YEAR]->(y:Year {value: '2024'})
RETURN p.title AS Title, 
       COLLECT(DISTINCT a.name) AS Authors, 
       j.name AS Journal, 
       y.value AS Year;

// 7. Top journals by year with paper counts (visual network)
MATCH (p:Paper)-[:PUBLISHED_IN]->(j:Journal)
MATCH (p)-[:PUBLISHED_IN_YEAR]->(y:Year)
WITH y, j, COUNT(p) AS count
WHERE count >= 3  // Only show journals with 3+ papers
RETURN y, j, count
ORDER BY y.value, count DESC;

// 8. All papers from a specific year grouped by journal
MATCH (p:Paper)-[:PUBLISHED_IN]->(j:Journal)
MATCH (p)-[:PUBLISHED_IN_YEAR]->(y:Year {value: '2024'})
WITH j, COLLECT(p.title) AS papers, COUNT(p) AS paperCount
RETURN j.name AS Journal, 
       paperCount AS TotalPapers, 
       papers AS PaperTitles
ORDER BY paperCount DESC;

// 9. Year-wise publication distribution (network view with counts)
MATCH (p:Paper)-[:PUBLISHED_IN]->(j:Journal)
MATCH (p)-[:PUBLISHED_IN_YEAR]->(y:Year)
WITH y, j, COUNT(p) AS paperCount
RETURN y, 
       COLLECT({journal: j.name, count: paperCount}) AS JournalsWithCounts
ORDER BY y.value;

// 10. Interactive query: Papers in Journal X during Year Y
// Modify the journal name and year as needed
MATCH (y:Year {value: '2024'})<-[:PUBLISHED_IN_YEAR]-(p:Paper)-[:PUBLISHED_IN]->(j:Journal)
WHERE j.name CONTAINS 'Journal'  // Use CONTAINS for partial matching
WITH y, j, COUNT(p) AS count, COLLECT(p.title) AS papers
RETURN y.value AS Year, 
       j.name AS Journal, 
       count AS PaperCount, 
       papers AS PaperTitles;

// 11. Visualization: Year -> Journal (edge label shows count)
// This creates a clean graph where relationships show the count
MATCH (p:Paper)-[:PUBLISHED_IN]->(j:Journal)
MATCH (p)-[:PUBLISHED_IN_YEAR]->(y:Year)
WITH y, j, COUNT(p) AS paperCount
WHERE paperCount > 2
CALL apoc.create.vRelationship(y, 'PUBLISHED_' + paperCount + '_PAPERS_IN', {count: paperCount}, j) 
YIELD rel
RETURN y, rel, j;
// Note: Above query requires APOC plugin. Use query #5 or #7 if APOC is not installed.

// 12. Simple version - Year and Journal with count as node property (no APOC needed)
MATCH (p:Paper)-[:PUBLISHED_IN]->(j:Journal)
MATCH (p)-[:PUBLISHED_IN_YEAR]->(y:Year)
WITH y, j, COUNT(p) AS paperCount
RETURN y, j, paperCount
LIMIT 100;
