"""
Knowledge Graph Builder Module
Creates interactive network graphs using PyVis
"""

import networkx as nx
from pyvis.network import Network
from typing import Dict, List
from config import (
    NODE_COLORS, NODE_SIZES, EDGE_COLORS,
    GRAPH_HEIGHT, GRAPH_WIDTH, 
    GRAPH_BGCOLOR, GRAPH_FONT_COLOR
)


class KnowledgeGraphBuilder:
    """Builds interactive knowledge graphs for professor-topic-paper relationships"""
    
    def __init__(self):
        self.graph = nx.Graph()
        self.net = None
    
    def clear_graph(self):
        """Clear the current graph"""
        self.graph.clear()
        self.net = None
    
    def add_professor_node(self, professor_id: str, name: str, image_url: str = None):
        """
        Add a professor node to the graph
        
        Args:
            professor_id: Unique identifier for professor
            name: Professor's name
            image_url: URL to professor's image
        """
        self.graph.add_node(
            professor_id,
            label=name,
            node_type='professor',
            title=f"<b>{name}</b><br><span style='color:#666'>Click to view profile</span>",
            image=image_url,
            color={'background': NODE_COLORS['professor'], 'border': '#d97706', 'highlight': {'background': '#fbbf24', 'border': '#f59e0b'}},
            size=NODE_SIZES['professor'],
            shape='circularImage' if image_url else 'dot',
            borderWidth=4,
            borderWidthSelected=6,
            font={'size': 18, 'face': 'Arial, sans-serif', 'color': '#1e293b', 'background': 'rgba(255,255,255,0.9)', 'strokeWidth': 0, 'bold': True},
            margin=12,
            fixed=False,
            physics=False
        )
    
    def add_topic_node(self, topic_id: str, topic_name: str):
        """
        Add a topic/research area node to the graph
        
        Args:
            topic_id: Unique identifier for topic
            topic_name: Name of the research topic
        """
        self.graph.add_node(
            topic_id,
            label=topic_name,
            node_type='topic',
            title=f"<b>{topic_name}</b><br><span style='color:#666'>Research Area</span>",
            color={'background': NODE_COLORS['topic'], 'border': '#0891b2', 'highlight': {'background': '#22d3ee', 'border': '#06b6d4'}},
            size=NODE_SIZES['topic'],
            shape='dot',
            borderWidth=3,
            borderWidthSelected=5,
            font={'size': 16, 'face': 'Arial, sans-serif', 'color': '#ffffff', 'strokeWidth': 0, 'bold': True},
            margin=10,
            fixed=False,
            physics=False
        )
    
    def add_paper_node(self, paper_id: str, title: str, year: str = "", citations: int = 0, doi: str = ""):
        """
        Add a paper node to the graph
        
        Args:
            paper_id: Unique identifier for paper
            title: Paper title
            year: Publication year
            citations: Number of citations
        """
        # Truncate long titles for display
        display_title = title[:30] + "..." if len(title) > 30 else title
        
        # Size based on citations
        size = min(NODE_SIZES['paper'] + citations // 3, 50)
        
        # Create DOI link if available
        doi_link = f"https://doi.org/{doi}" if doi else None
        
        tooltip_link = f'<br><a href="{doi_link}" target="_blank" style="color:#3b82f6">View Paper</a>' if doi_link else ''
        tooltip = f"<div style='max-width:300px'><b>{title}</b><br><br>Year: {year}<br>Citations: {citations}{tooltip_link}</div>"
        
        self.graph.add_node(
            paper_id,
            label=display_title,
            node_type='paper',
            title=tooltip,
            color={'background': NODE_COLORS['paper'], 'border': '#1e40af', 'highlight': {'background': '#3b82f6', 'border': '#2563eb'}},
            size=size,
            shape='dot',
            borderWidth=2,
            borderWidthSelected=4,
            font={'size': 14, 'face': 'Arial, sans-serif', 'color': '#ffffff', 'strokeWidth': 0},
            margin=8,
            fixed=False,
            physics=False
        )
        
        # Add clickable link if DOI exists
        if doi_link:
            self.graph.nodes[paper_id]['url'] = doi_link
    
    def add_edge(self, source: str, target: str, edge_type: str = "", width: int = 1, color: str = None):
        """
        Add an edge between two nodes
        
        Args:
            source: Source node ID
            target: Target node ID
            edge_type: Type of relationship
            width: Edge width
            color: Edge color
        """
        if color is None:
            color = EDGE_COLORS.get(edge_type.lower(), '#94a3b8')
        
        self.graph.add_edge(
            source, 
            target, 
            title=edge_type,
            width=width,
            color={'color': color, 'opacity': 0.5},
            smooth={'enabled': True, 'type': 'continuous', 'roundness': 0.6}
        )
    
    def build_professor_graph(self, professor_data: Dict) -> str:
        """
        Build a complete graph for a professor with their topics and papers
        
        Args:
            professor_data: Dictionary containing professor's complete data
            
        Returns:
            HTML string of the interactive graph
        """
        self.clear_graph()
        
        prof_id = professor_data.get('scopus_id', 'prof_1')
        prof_name = professor_data.get('name', 'Unknown')
        prof_image = professor_data.get('image_url')
        
        # Add professor node (center)
        self.add_professor_node(prof_id, prof_name, prof_image)
        
        # Add topics and connect to professor
        topics = professor_data.get('topics', [])
        for i, topic in enumerate(topics):
            topic_id = f"topic_{prof_id}_{i}"
            self.add_topic_node(topic_id, topic)
            self.add_edge(prof_id, topic_id, "expertise", width=4, color=EDGE_COLORS['expertise'])
        
        # Add papers and connect to professor
        papers = professor_data.get('papers', [])
        for i, paper in enumerate(papers):
            paper_id = f"paper_{prof_id}_{i}"
            self.add_paper_node(
                paper_id,
                paper.get('title', 'Untitled'),
                paper.get('year', ''),
                paper.get('citations', 0),
                paper.get('doi', '')
            )
            self.add_edge(prof_id, paper_id, "authored", width=2, color=EDGE_COLORS['authored'])
        
        # Create PyVis network
        self.net = Network(
            height=GRAPH_HEIGHT,
            width=GRAPH_WIDTH,
            bgcolor=GRAPH_BGCOLOR,
            font_color=GRAPH_FONT_COLOR,
            notebook=False
        )
        
        # Copy NetworkX graph to PyVis
        self.net.from_nx(self.graph)
        
        # Add URL attributes to nodes for click handling
        for node_id in self.graph.nodes():
            node_data = self.graph.nodes[node_id]
            if 'url' in node_data and node_data['url']:
                # Get PyVis node and add url
                for n in self.net.nodes:
                    if n['id'] == node_id:
                        n['url'] = node_data['url']
                        # Add visual indication that it's clickable
                        n['title'] = node_data.get('title', '') + '<br><i style=\"color:#3b82f6\">Click to open</i>'
                        break
        
        # Configure layout and styling (no physics - fixed positions)
        self.net.set_options("""
        {
          "nodes": {
            "shadow": {
              "enabled": true,
              "color": "rgba(0,0,0,0.15)",
              "size": 12,
              "x": 3,
              "y": 3
            },
            "font": {
              "size": 16,
              "face": "Arial, sans-serif",
              "strokeWidth": 0,
              "align": "center"
            }
          },
          "edges": {
            "smooth": {
              "enabled": true,
              "type": "curvedCW",
              "roundness": 0.2
            },
            "color": {
              "inherit": false
            },
            "width": 2
          },
          "physics": {
            "enabled": false
          },
          "interaction": {
            "hover": true,
            "tooltipDelay": 100,
            "navigationButtons": true,
            "keyboard": {
              "enabled": true
            },
            "zoomView": true,
            "dragView": true,
            "dragNodes": true
          },
          "layout": {
            "randomSeed": 42,
            "improvedLayout": true,
            "hierarchical": {
              "enabled": true,
              "direction": "LR",
              "sortMethod": "directed",
              "nodeSpacing": 200,
              "levelSeparation": 250,
              "treeSpacing": 200,
              "blockShifting": true,
              "edgeMinimization": true,
              "parentCentralization": true
            }
          }
        }
        """)
        
        # Generate HTML with click handler
        html = self.net.generate_html()
        
        # Add JavaScript to handle clicks on nodes with URLs
        click_handler = '''
        <script type="text/javascript">
        network.on("click", function (params) {
            if (params.nodes.length > 0) {
                var nodeId = params.nodes[0];
                var node = nodes.get(nodeId);
                if (node && node.url) {
                    window.open(node.url, '_blank');
                }
            }
        });
        </script>
        '''
        
        html = html.replace('</body>', click_handler + '</body>')
        
        return html
