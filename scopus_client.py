"""
Scopus API client module
Fetches research topics and papers for professors
"""

import requests
from typing import List, Dict, Optional
import time
from config import MAX_PAPERS_PER_PROFESSOR


class ScopusClient:
    """Client for interacting with Scopus API"""
    
    def __init__(self, api_key: str):
        """
        Initialize Scopus client with API key
        
        Args:
            api_key: Scopus API key from dev.elsevier.com
        """
        self.api_key = api_key
        self.base_url = "https://api.elsevier.com/content"
        self.headers = {
            'X-ELS-APIKey': api_key,
            'Accept': 'application/json'
        }
    
    def get_author_data(self, author_id: str, max_papers: int = None) -> Optional[Dict]:
        """
        Get author basic information, topics, AND papers using Search API
        (Compatible with free API keys that don't have Author Retrieval access)
        
        Args:
            author_id: Scopus Author ID
            max_papers: Maximum papers to retrieve (default 25 for free API tier)
            
        Returns:
            Dictionary with author data including papers, or None
        """
        if max_papers is None:
            # Free API key limit is 25 results per query
            max_papers = 25
        
        try:
            # Use search API to get author's papers and aggregate data
            url = f"{self.base_url}/search/scopus"
            params = {
                'query': f'AU-ID({author_id})',
                'count': min(max_papers, 25),  # Cap at 25 for free API
                'sort': '-pubyear',  # Sort by year descending
                # Only request basic fields that are available with free API key
                'field': 'dc:title,prism:coverDate,prism:doi,citedby-count,dc:creator'
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 401:
                print(f"Warning: Unauthorized access for author {author_id}")
                return None
            
            if response.status_code != 200:
                print(f"HTTP Error {response.status_code} for author {author_id}")
                print(f"Response: {response.text[:300]}")  # Debug: show error message
                return None
            
            data = response.json()
            
            # Initialize author data
            author_data = {
                'name': '',
                'document_count': 0,
                'citation_count': 0,
                'topics': [],
                'papers': []  # Include papers in the same call
            }
            
            if 'search-results' in data and 'entry' in data['search-results']:
                entries = data['search-results']['entry']
                
                # Filter out error entries
                valid_entries = [e for e in entries if 'error' not in e]
                author_data['document_count'] = len(valid_entries)
                
                # Extract name from first valid entry
                if valid_entries:
                    first_entry = valid_entries[0]
                    if 'dc:creator' in first_entry:
                        author_data['name'] = first_entry['dc:creator']
                
                # Count total citations and build papers list
                total_citations = 0
                papers = []
                for entry in valid_entries:
                    cites = int(entry.get('citedby-count', 0))
                    total_citations += cites
                    
                    paper = {
                        'title': entry.get('dc:title', 'Untitled'),
                        'year': entry.get('prism:coverDate', '')[:4] if entry.get('prism:coverDate') else '',
                        'doi': entry.get('prism:doi', ''),
                        'citations': cites
                    }
                    papers.append(paper)
                
                author_data['citation_count'] = total_citations
                author_data['papers'] = papers
                
                # Extract topics from paper titles (simple keyword extraction)
                topics_keywords = self._extract_topics_from_titles(valid_entries)
                author_data['topics'] = topics_keywords
            
            return author_data if author_data['document_count'] > 0 else None
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Author ID {author_id} not found")
            elif e.response.status_code == 429:
                print(f"Rate limit exceeded for Scopus API")
            else:
                print(f"HTTP Error {e.response.status_code} for author {author_id}")
            return None
        except Exception as e:
            print(f"Error fetching author data for {author_id}: {e}")
            return None
    
    def get_professor_complete_data(self, author_id: str, delay: float = 0.5) -> Optional[Dict]:
        """
        Get complete data for a professor (author info + papers in one API call)
        
        Args:
            author_id: Scopus Author ID
            delay: Not used anymore but kept for compatibility
            
        Returns:
            Complete professor data dictionary
        """
        # Get author data (now includes papers in one call)
        author_data = self.get_author_data(author_id)
        
        if not author_data:
            return None
        
        # Add scopus_id to the data
        author_data['scopus_id'] = author_id
        
        return author_data
    
    def _extract_topics_from_titles(self, papers: List[Dict]) -> List[str]:
        """
        Extract common research topics from paper titles
        (Workaround for limited API access)
        
        Args:
            papers: List of paper dictionaries with 'dc:title' field
            
        Returns:
            List of common keywords/topics
        """
        # Common research keywords to look for
        research_keywords = [
            'Machine Learning', 'Deep Learning', 'Neural Network', 'Artificial Intelligence',
            'Computer Vision', 'Natural Language Processing', 'Data Mining', 'Big Data',
            'Cloud Computing', 'IoT', 'Internet of Things', 'Security', 'Cryptography',
            'Algorithm', 'Optimization', 'Database', 'Web', 'Mobile', 'Software Engineering',
            'Network', 'Distributed System', 'Blockchain', 'Robotics', 'Image Processing',
            'Classification', 'Clustering', 'Prediction', 'Recommendation', 'Pattern Recognition',
            'Genetic Algorithm', 'Fuzzy', 'Swarm Intelligence', 'Expert System',
            'Knowledge Management', 'Information Retrieval', 'Semantic',
        ]
        
        # Count occurrences in titles
        keyword_counts = {}
        for paper in papers:
            title = paper.get('dc:title', '').lower()
            for keyword in research_keywords:
                if keyword.lower() in title:
                    keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Return top keywords (found in at least 2 papers, or top 10)
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Get keywords that appear at least twice OR take top 10
        result = []
        for keyword, count in sorted_keywords:
            if count >= 2 or len(result) < 10:
                result.append(keyword)
            if len(result) >= 15:  # Limit to 15 topics
                break
        
        return result if result else ['Computer Science']  # Default topic
    
    def test_connection(self) -> tuple:
        """
        Test if API key is valid
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Try a simple search query (more permissive than author endpoint)
            url = f"{self.base_url}/search/scopus"
            params = {
                'query': 'TITLE(computer)',
                'count': 1
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            # Check status code
            if response.status_code == 200:
                return (True, "API key is valid")
            elif response.status_code == 401:
                return (False, f"Invalid API key or unauthorized access. Status: {response.status_code}")
            elif response.status_code == 429:
                return (False, "Rate limit exceeded - please wait and try again")
            else:
                return (False, f"HTTP Error {response.status_code}: {response.text[:100]}")
                
        except requests.exceptions.Timeout:
            return (False, "Connection timeout - please check your internet connection")
        except requests.exceptions.ConnectionError:
            return (False, "Connection error - please check your internet connection")
        except requests.exceptions.SSLError:
            return (False, "SSL certificate error - network security issue")
        except Exception as e:
            return (False, f"Unexpected error: {str(e)[:100]}")


# Test function
if __name__ == "__main__":
    # Test with a sample API key
    api_key = input("Enter your Scopus API Key: ")
    
    client = ScopusClient(api_key)
    
    print("Testing API connection...")
    success, message = client.test_connection()
    
    if success:
        print(f"✓ {message}")
        
        # Test with a sample author ID
        author_id = "6603566678"  # Example from PRD
        print(f"\nFetching data for author {author_id}...")
        
        data = client.get_professor_complete_data(author_id)
        
        if data:
            print(f"✓ Author: {data.get('name', 'N/A')}")
            print(f"✓ Topics: {len(data.get('topics', []))}")
            print(f"✓ Papers: {len(data.get('papers', []))}")
            print("\nSample paper:")
            if data.get('papers'):
                print(data['papers'][0])
    else:
        print(f"✗ {message}")
