// ====================================================================
// YEAR ← JOURNAL (with paper count on journal nodes)
// ====================================================================

// Main Query: Show Year nodes with Journals pointing to them
// The count is shown as a property on the relationship or in the return
MATCH (p:Paper)-[:PUBLISHED_IN]->(j:Journal)
MATCH (p)-[:PUBLISHED_IN_YEAR]->(y:Year)
WITH y, j, COUNT(p) AS paperCount
RETURN y, j, paperCount AS count
ORDER BY y.value, paperCount DESC
LIMIT 100;

// Alternative: If you want to see it in table format with counts
MATCH (p:Paper)-[:PUBLISHED_IN]->(j:Journal)
MATCH (p)-[:PUBLISHED_IN_YEAR]->(y:Year)
WITH y.value AS Year, j.name AS Journal, COUNT(p) AS PaperCount
RETURN Year, Journal, PaperCount
ORDER BY Year, PaperCount DESC
LIMIT 100;

// For better visualization: Show only journals with significant papers
MATCH (p:Paper)-[:PUBLISHED_IN]->(j:Journal)
MATCH (p)-[:PUBLISHED_IN_YEAR]->(y:Year)
WITH y, j, COUNT(p) AS paperCount
WHERE paperCount >= 2  // Only show journals with 2+ papers
RETURN y, j, paperCount
ORDER BY y.value, paperCount DESC;

// To see the network: Year ← Journal (grouped by year)
MATCH (p:Paper)-[:PUBLISHED_IN]->(j:Journal)
MATCH (p)-[:PUBLISHED_IN_YEAR]->(y:Year)
WITH y, j, COUNT(p) AS count
RETURN y, COLLECT({journal: j, paperCount: count}) AS journals
ORDER BY y.value;
