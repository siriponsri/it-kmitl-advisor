"""
Fetch All Scopus Data - Pre-cache Script
Fetches research data for all professors with Scopus IDs and saves to cache
Run this script periodically (e.g., once a month) to update the cache
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from scopus_client import ScopusClient
from graph_builder import KnowledgeGraphBuilder

# Load environment variables
load_dotenv()

SCOPUS_API_KEY = os.getenv('SCOPUS_API_KEY')
CACHE_DIR = Path(os.getenv('CACHE_DIRECTORY', 'data'))
BASIC_CACHE_FILE = CACHE_DIR / 'professors_basic.json'
SCOPUS_CACHE_FILE = CACHE_DIR / 'professors_scopus_data.json'
GRAPHS_DIR = CACHE_DIR / 'graphs'

# Create directories
CACHE_DIR.mkdir(exist_ok=True)
GRAPHS_DIR.mkdir(exist_ok=True)


def load_basic_professors():
    """Load basic professor data"""
    if not BASIC_CACHE_FILE.exists():
        print(f"❌ {BASIC_CACHE_FILE} not found!")
        print("Please run 'python fetch_professors.py' first to scrape professor data.")
        return []
    
    with open(BASIC_CACHE_FILE, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
        return cache_data.get('professors', [])


def fetch_all_scopus_data(api_key, professors, delay=2.0):
    """
    Fetch Scopus data for all professors with Scopus IDs
    
    Args:
        api_key: Scopus API key
        professors: List of professor dictionaries
        delay: Delay between API calls (seconds)
    
    Returns:
        Dictionary mapping scopus_id to complete data
    """
    if not api_key:
        print("❌ No API key found!")
        print("Please set SCOPUS_API_KEY in your .env file")
        return {}
    
    client = ScopusClient(api_key)
    
    # Test connection
    print("Testing Scopus API connection...")
    success, message = client.test_connection()
    
    if not success:
        print(f"❌ {message}")
        return {}
    
    print(f"✅ {message}")
    print()
    
    # Filter professors with Scopus IDs
    professors_with_scopus = [p for p in professors if p.get('scopus_id')]
    
    print(f"Found {len(professors_with_scopus)} professors with Scopus IDs")
    print(f"Delay between requests: {delay}s")
    print("=" * 70)
    print()
    
    scopus_data_cache = {}
    successful = 0
    failed = 0
    
    for i, professor in enumerate(professors_with_scopus, 1):
        name = professor.get('name', 'Unknown')
        scopus_id = professor.get('scopus_id')
        
        print(f"[{i}/{len(professors_with_scopus)}] Fetching data for {name}...")
        print(f"  Scopus ID: {scopus_id}")
        
        try:
            scopus_data = client.get_professor_complete_data(scopus_id, delay=0)
            
            if scopus_data:
                # Merge basic data with Scopus data
                complete_data = {
                    **professor,
                    'topics': scopus_data.get('topics', []),
                    'papers': scopus_data.get('papers', []),
                    'document_count': scopus_data.get('document_count', 0),
                    'citation_count': scopus_data.get('citation_count', 0),
                    'fetched_at': datetime.now().isoformat()
                }
                
                scopus_data_cache[scopus_id] = complete_data
                
                print(f"  ✅ Success!")
                print(f"     - Topics: {len(scopus_data.get('topics', []))}")
                print(f"     - Papers: {len(scopus_data.get('papers', []))}")
                print(f"     - Citations: {scopus_data.get('citation_count', 0)}")
                
                successful += 1
            else:
                print(f"  ⚠️  No data returned")
                failed += 1
        
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            failed += 1
        
        print()
        
        # Delay before next request
        if i < len(professors_with_scopus):
            time.sleep(delay)
    
    print("=" * 70)
    print(f"Summary: {successful} successful, {failed} failed")
    print()
    
    return scopus_data_cache


def save_scopus_cache(scopus_data_cache):
    """Save Scopus data cache to JSON"""
    cache_data = {
        'metadata': {
            'fetched_at': datetime.now().isoformat(),
            'professor_count': len(scopus_data_cache),
            'total_papers': sum(len(p.get('papers', [])) for p in scopus_data_cache.values()),
            'total_citations': sum(p.get('citation_count', 0) for p in scopus_data_cache.values())
        },
        'professors': scopus_data_cache
    }
    
    with open(SCOPUS_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved Scopus data cache to {SCOPUS_CACHE_FILE}")
    print(f"   - Professors: {len(scopus_data_cache)}")
    print(f"   - Total papers: {cache_data['metadata']['total_papers']}")
    print(f"   - Total citations: {cache_data['metadata']['total_citations']}")


def generate_all_graphs(scopus_data_cache):
    """Pre-generate knowledge graphs for all professors using topic_groups"""
    print()
    print("=" * 70)
    print("Generating Knowledge Graphs")
    print("=" * 70)
    print()
    
    # Load professors_by_topics.json for star schema (has topic_groups)
    topics_file = CACHE_DIR / 'professors_by_topics.json'
    if topics_file.exists():
        with open(topics_file, 'r', encoding='utf-8') as f:
            topics_data = json.load(f)
            professors_by_topics = topics_data.get('professors', {})
        print(f"✅ Loaded topic_groups data for star schema graphs")
    else:
        professors_by_topics = {}
        print(f"⚠️  professors_by_topics.json not found, using flat structure")
    
    builder = KnowledgeGraphBuilder()
    
    for i, (scopus_id, professor_data) in enumerate(scopus_data_cache.items(), 1):
        name = professor_data.get('name', 'Unknown')
        
        print(f"[{i}/{len(scopus_data_cache)}] Generating graph for {name}...")
        
        try:
            # Merge topic_groups from professors_by_topics if available
            if scopus_id in professors_by_topics:
                professor_data['topic_groups'] = professors_by_topics[scopus_id].get('topic_groups', {})
            
            graph_html = builder.build_professor_graph(professor_data)
            
            # Save graph
            graph_file = GRAPHS_DIR / f"{scopus_id}.html"
            with open(graph_file, 'w', encoding='utf-8') as f:
                f.write(graph_html)
            
            print(f"  ✅ Saved to {graph_file.name}")
        
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
        
    
    print()
    print(f"✅ Generated {len(scopus_data_cache)} knowledge graphs")
    print(f"   Saved to {GRAPHS_DIR}/")


def main():
    print("=" * 70)
    print("Scopus Data Pre-Cache Script")
    print("=" * 70)
    print()
    
    # Check API key
    if not SCOPUS_API_KEY:
        print("❌ SCOPUS_API_KEY not found in .env file!")
        print()
        print("Please create a .env file with your API key:")
        print("SCOPUS_API_KEY=your_api_key_here")
        print()
        print("Get your API key from: https://dev.elsevier.com")
        return
    
    # Load basic professor data
    print("Loading professor data from cache...")
    professors = load_basic_professors()
    
    if not professors:
        return
    
    print(f"✅ Loaded {len(professors)} professors")
    print()
    
    # Fetch Scopus data
    print("Starting Scopus data fetch...")
    print("This may take several minutes depending on the number of professors.")
    print()
    
    scopus_data_cache = fetch_all_scopus_data(SCOPUS_API_KEY, professors, delay=2.0)
    
    if not scopus_data_cache:
        print("❌ No data fetched. Exiting.")
        return
    
    # Save cache
    save_scopus_cache(scopus_data_cache)
    
    # Generate graphs
    generate_all_graphs(scopus_data_cache)
    
    print()
    print("=" * 70)
    print("✅ ALL DONE!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Run 'streamlit run app.py' to view the updated data")
    print("2. Re-run this script periodically to update the cache")


if __name__ == "__main__":
    main()
