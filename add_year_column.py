import pandas as pd

# Read both CSV files
print("Reading research_csv.csv...")
df1 = pd.read_csv('research_csv.csv', encoding='ISO-8859-1')
print(f"Original columns: {df1.columns.tolist()}")
print(f"Total rows: {len(df1)}")

print("\nReading research_csv_2.csv...")
df2 = pd.read_csv('research_csv_2.csv', encoding='ISO-8859-1')
print(f"Columns in research_csv_2: {df2.columns.tolist()}")

# Add the Year column from df2 to df1
# Assuming the rows are in the same order
if len(df1) <= len(df2):
    df1['Year'] = df2['Year'][:len(df1)]
else:
    print("Warning: research_csv has more rows than research_csv_2!")
    df1['Year'] = df2['Year']

# Save the updated CSV
df1.to_csv('research_csv.csv', index=False, encoding='ISO-8859-1')

print("\n✓ Year column added successfully!")
print(f"Updated columns: {df1.columns.tolist()}")
print("\nFirst few rows with Year:")
print(df1[['Authors', 'Title', 'Year']].head())
