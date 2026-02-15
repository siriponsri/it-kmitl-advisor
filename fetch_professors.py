"""
Fetch IT KMITL Professor Data
Script to scrape professor information from IT KMITL website and save as cache
Run this script once to fetch and cache professor data
"""

import json
import csv
from datetime import datetime
from scraper import ITKMITLScraper
from pathlib import Path


def save_to_json(data, filename='data/professors_basic.json'):
    """Save professor data to JSON file"""
    Path('data').mkdir(exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved to {filename}")


def save_to_csv(data, filename='data/professors_basic.csv'):
    """Save professor data to CSV file"""
    Path('data').mkdir(exist_ok=True)
    
    if not data:
        print("No data to save")
        return
    
    fieldnames = ['name', 'thai_name', 'scopus_id', 'scopus_url', 'image_url', 'profile_url']
    
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for prof in data:
            writer.writerow({
                'name': prof.get('name', ''),
                'thai_name': prof.get('thai_name', ''),
                'scopus_id': prof.get('scopus_id', ''),
                'scopus_url': prof.get('scopus_url', ''),
                'image_url': prof.get('image_url', ''),
                'profile_url': prof.get('profile_url', '')
            })
    
    print(f"✓ Saved to {filename}")


def main():
    """Main function to fetch and save professor data"""
    print("=" * 70)
    print("IT KMITL Professor Data Fetcher")
    print("=" * 70)
    print()
    
    # Initialize scraper
    print("Initializing web scraper...")
    scraper = ITKMITLScraper()
    print()
    
    # Scrape professor data
    print("Fetching professor data from IT KMITL website...")
    print("This may take a few minutes...")
    print()
    
    professors = scraper.scrape_all_professors(delay=1.0)
    
    if not professors:
        print("ERROR: Failed to fetch professor data")
        print("Please check your internet connection and try again")
        return
    
    print()
    print("-" * 70)
    print("SUMMARY")
    print("-" * 70)
    print(f"Total professors found: {len(professors)}")
    print(f"With Scopus ID: {sum(1 for p in professors if p.get('scopus_id'))}")
    print(f"Without Scopus ID: {sum(1 for p in professors if not p.get('scopus_id'))}")
    print()
    
    # Add metadata
    cache_data = {
        'fetched_at': datetime.now().isoformat(),
        'source': 'https://www.it.kmitl.ac.th/th/staffs/academic',
        'count': len(professors),
        'professors': professors
    }
    
    # Save to JSON
    print("Saving data...")
    save_to_json(cache_data, 'data/professors_basic.json')
    
    # Save to CSV (simplified version)
    save_to_csv(professors, 'data/professors_basic.csv')
    
    print()
    print("-" * 70)
    print("SUCCESS!")
    print("-" * 70)
    print()
    print("Files created:")
    print("  - data/professors_basic.json (complete data)")
    print("  - data/professors_basic.csv (table format)")
    print()
    print("Next steps:")
    print("  1. Run: streamlit run app.py")
    print("  2. The app will load cached professor data")
    print("  3. Enter your Scopus API key")
    print("  4. Select a professor to view their knowledge graph")
    print()
    
    # Show sample
    if professors:
        print("Sample data (first professor):")
        print("-" * 70)
        sample = professors[0]
        print(f"Name: {sample.get('name', 'N/A')}")
        print(f"Scopus ID: {sample.get('scopus_id', 'Not found')}")
        print(f"Profile URL: {sample.get('profile_url', 'N/A')}")
        print(f"Image URL: {sample.get('image_url', 'N/A')}")
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")
