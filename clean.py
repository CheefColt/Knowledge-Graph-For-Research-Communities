import pandas as pd
import re
from shutil import copy2

def clean_authors(author_string):
    """
    Clean author names by merging names with their initials
    Handles multi-letter initials like P.V.N., R.P., etc.
    """
    if pd.isna(author_string):
        return author_string
    
    # Split by comma and strip whitespace
    parts = [part.strip() for part in author_string.split(',')]
    
    cleaned_authors = []
    i = 0
    
    while i < len(parts):
        current_part = parts[i]
        
        # Check if next part exists and looks like initials
        # Pattern for initials: one or more letters followed by dots (like S., R.P., P.V.N.)
        if (i + 1 < len(parts) and 
            re.match(r'^[A-Z]+(\.?[A-Z]*)*\.?$', parts[i + 1].strip())):
            
            # Merge name with initials
            initials = parts[i + 1].strip()
            # Ensure it ends with a dot if it doesn't already
            if not initials.endswith('.'):
                initials += '.'
            cleaned_authors.append(f"{current_part} {initials}")
            i += 2  # Skip the next part since we've used it
        else:
            cleaned_authors.append(current_part)
            i += 1
    
    return ', '.join(cleaned_authors)
import re

def clean_author(author):
    author = author.strip()
    # Remove extra spaces
    author = re.sub(r'\s+', ' ', author)
    # Optionally, merge initials with names (customize as needed)
    # Example: "Samuel T.S.A." or "Samuel" → "Samuel T.S.A."
    # You may need a mapping or fuzzy matching for best results
    return author

# Main execution
def main():
    # Replace 'your_file.csv' with your actual CSV filename
    filename = 'scopus Publications(2_3_24).csv'
    
    try:
        # Create backup first
        backup_filename = f'{filename}.backup'
        copy2(filename, backup_filename)
        print(f"✅ Backup created: {backup_filename}")
        
        # Load the CSV file
        print(f"📖 Loading {filename}...")
        df = pd.read_csv(filename)
        
        # Check if Authors column exists
        if 'Authors' not in df.columns:
            print("❌ Error: 'Authors' column not found in the CSV file.")
            print("Available columns:", list(df.columns))
            return
        
        # Show sample of original data
        print("\n📋 Sample of original data:")
        print(df['Authors'].head(3).to_string())
        
        # Clean the Authors column
        print("\n🔧 Cleaning authors data...")
        df['Authors'] = df['Authors'].apply(lambda author: clean_author(clean_authors(author)))
        
        # Show sample of cleaned data
        print("\n✨ Sample of cleaned data:")
        print(df['Authors'].head(3).to_string())
        
        # Save back to the original file
        df.to_csv(filename, index=False)
        print(f"\n✅ Original file {filename} has been updated with cleaned data!")
        
        # Test with your specific example
        test_string = "Punyasamudram, S., Puthalapattu, R.P., Bathinapatla, A., Mulpuri, R., Kanchi, S., Kumar, P.V.N."
        print("\n🧪 Test example:")
        print("Original:", test_string)
        print("Cleaned: ", clean_authors(test_string))
        
    except FileNotFoundError:
        print(f"❌ Error: File '{filename}' not found.")
        print("Please make sure the CSV file exists and update the filename in the script.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()