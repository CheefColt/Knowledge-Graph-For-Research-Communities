# Research Collaboration Network Analysis

A knowledge graph-based system for analyzing academic research collaboration patterns using Neo4j, featuring community detection and ML-based link prediction for future coauthorship forecasting.

## Overview

This project analyzes research collaboration networks by:
- Constructing a knowledge graph of authors, papers, and journals in Neo4j
- Detecting research communities using the Louvain algorithm
- Predicting future collaborations using hybrid similarity metrics
- Computing comprehensive network analytics

## Dataset Requirements

Your CSV file should contain these columns:
- **Authors** (required): Comma-separated list of author names
- **Title** (required): Paper title
- **Source title** (required): Journal/venue name
- **Document Type** (optional): Publication type (defaults to 'Unknown')

Example format:
```csv
Authors,Title,Source title,Document Type
"Smith J., Jones A.",Analysis of Neural Networks,IEEE Transactions,Article
"Brown K., Lee M., Chen X.",Machine Learning Survey,ACM Computing Surveys,Review
```

## Prerequisites

- **Neo4j Database** (5.x or later) with Graph Data Science (GDS) library
- **Python 3.8+**

### Python Dependencies

```bash
pip install neo4j pandas scikit-learn numpy
```

## Scripts

### 1. KG_v2_neo4j.py - Graph Construction

**Purpose**: Import your research data into Neo4j as a knowledge graph

**Features**:
- Creates Author, Paper, Journal, DocumentType, and Coauthorship nodes
- Establishes WROTE, PUBLISHED_IN, HAS_TYPE, and COAUTHORED relationships
- Normalizes author names (titlecase, strip whitespace, remove trailing dots)
- Handles missing Document Type column gracefully

**Usage**:
```python
# Edit connection details in the script:
uri = "bolt://localhost:7687"
user = "neo4j"
password = "your_password"
csv_file = "your_data.csv"

# Run the script:
python KG_v2_neo4j.py
```

**Customization for Your Use Case**:
- Modify `clean_author()` function for different name normalization rules
- Add additional node properties by extending the MERGE statements
- Adjust relationship types to match your domain
- Handle additional CSV columns by adding them to the DataFrame processing

### 2. predict_coauthorship.py - Link Prediction

**Purpose**: Predict future research collaborations using similarity-based features

**Algorithm**:
1. Fetches author-paper-journal triples from Neo4j
2. Builds binary feature vectors (one-hot encoding of papers and journals)
3. Computes Cosine similarity (directional alignment) and Jaccard similarity (set overlap)
4. Averages both metrics for final prediction score
5. Generates top-N predicted collaboration pairs

**Usage**:
```python
# Edit connection details:
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "your_password"

# Run the script:
python predict_coauthorship.py
```

**Output**: `predicted_coauthorships.csv` with columns:
- Author1, Author2: Predicted collaboration pair
- Cosine_Similarity: Vector alignment score (0-1)
- Jaccard_Similarity: Set overlap score (0-1)
- Average_Similarity: Combined score

**Customization**:
- Adjust `TOP_N` variable to control number of predictions
- Add temporal features (year, citation count) to feature vectors
- Experiment with different similarity metrics (e.g., dot product, Manhattan distance)
- Filter by minimum threshold or specific research domains
- Use node embeddings (node2vec, GraphSAGE) instead of one-hot encoding

### 3. calculate_metrics.py - Network Analytics

**Purpose**: Compute comprehensive graph and prediction metrics

**Metrics Calculated**:
- **Graph Statistics**: Node counts, edge counts, density
- **Degree Analysis**: Mean, median, max degrees; distribution
- **Community Metrics**: Number of communities, modularity, size distribution
- **Prediction Analysis**: Similarity score distributions, top predictions
- **Network Topology**: Clustering, centrality measures

**Usage**:
```python
# Edit connection details:
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "your_password"

# Run the script:
python calculate_metrics.py
```

**Output**: 
- Console output with formatted metrics
- `calculated_metrics.txt` file with all results

**Customization**:
- Add custom Cypher queries for domain-specific metrics
- Compute temporal evolution metrics if year data available
- Calculate PageRank, betweenness centrality for author ranking
- Add citation-based metrics if citation data exists

### 4. clean.py - Data Preprocessing

**Purpose**: Clean and prepare raw CSV data before import

**Usage**:
```python
# Customize for your data cleaning needs
python clean.py
```

**Common Customizations**:
- Remove duplicates based on title or DOI
- Standardize author name formats
- Extract year from date fields
- Parse and clean venue names
- Handle special characters in titles
- Split multi-valued fields

## Complete Workflow

### Step 1: Prepare Your Data
```bash
# Clean your CSV if needed
python clean.py
```

### Step 2: Import to Neo4j
```bash
# Build the knowledge graph
python KG_v2_neo4j.py
```

### Step 3: Run Community Detection

Open Neo4j Browser and execute:

```cypher
// Create graph projection
CALL gds.graph.project(
    'coauthorGraph',
    'Author',
    {
        COAUTHORED: {
            type: 'COAUTHORED',
            orientation: 'UNDIRECTED'
        }
    }
)

// Run Louvain algorithm
CALL gds.louvain.stream('coauthorGraph')
YIELD nodeId, communityId
WITH gds.util.asNode(nodeId) AS author, communityId
RETURN author.name AS author_name, communityId
ORDER BY communityId, author_name

// Write communities back to graph
CALL gds.louvain.write('coauthorGraph', {
    writeProperty: 'community'
})

// Export to CSV (optional)
CALL apoc.export.csv.query(
    "MATCH (a:Author) RETURN a.name AS author, a.community AS community ORDER BY community",
    "community_detection_table.csv",
    {}
)
```

### Step 4: Predict Collaborations
```bash
python predict_coauthorship.py
```

### Step 5: Calculate Metrics
```bash
python calculate_metrics.py
```

## Adapting to Your Domain

### Healthcare/Clinical Research
- Add Patient, Treatment, Outcome nodes
- Track clinical trial collaborations
- Predict researcher-hospital partnerships

### Corporate/Patent Data
- Model Inventor, Patent, Company, Technology nodes
- Predict inventor collaborations
- Identify technology clusters

### Social Media/Citation Networks
- Add User, Post, Topic, Citation nodes
- Predict influencer collaborations
- Detect trending research topics

### Bioinformatics
- Model Gene, Protein, Disease, Researcher nodes
- Track protein-protein interaction networks
- Predict research team formations

## Neo4j Configuration

Ensure your Neo4j instance has:
1. **APOC plugin** (for CSV export): Download from Neo4j Desktop Plugin Manager
2. **GDS library** (for Louvain): Included in Neo4j Desktop or install separately
3. **Sufficient memory**: Configure `dbms.memory.heap.max_size` in neo4j.conf

## Troubleshooting

**Authentication Error**: Verify Neo4j password in scripts
**Memory Issues**: Reduce batch size or increase Neo4j heap memory
**Missing Column**: Script auto-adds 'Document Type' if missing
**Slow Performance**: Add indexes on frequently queried properties:
```cypher
CREATE INDEX author_name FOR (a:Author) ON (a.name);
CREATE INDEX paper_title FOR (p:Paper) ON (p.title);
CREATE INDEX journal_name FOR (j:Journal) ON (j.name);
```

## Output Files

- `community_detection_table.csv` - Author community assignments
- `predicted_coauthorships.csv` - Predicted collaboration pairs with scores
- `calculated_metrics.txt` - Comprehensive network statistics

## Performance Tips

1. **Batch Processing**: For large datasets (>10K papers), modify scripts to use batch MERGE operations
2. **Indexes**: Create indexes before import for faster MERGE operations
3. **Parallel Processing**: Use `multiprocessing` for feature vector computation
4. **Graph Projections**: Use native projections instead of Cypher projections for GDS algorithms

## Citation

If you use this code in your research, please cite:
```
[Your project name]
Research Collaboration Network Analysis and Link Prediction
GitHub: [your-repo-url]
```

## License

MIT License - Feel free to use and modify for your research projects.

## Contact

For questions or contributions, please open an issue on GitHub.
