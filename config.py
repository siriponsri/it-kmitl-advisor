"""
Configuration file for IT KMITL Advisor Knowledge Graph
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# URLs
IT_KMITL_STAFF_URL = "https://www.it.kmitl.ac.th/th/staffs/academic"
STAFF_PROFILE_PATTERN = r'/th/staffs/s/'

# Graph Visualization Settings
GRAPH_HEIGHT = "900px"
GRAPH_WIDTH = "100%"
GRAPH_BGCOLOR = "#f8fafc"  # Light gray background
GRAPH_FONT_COLOR = "#1e293b"  # Dark slate gray

# Node Colors (Clean professional palette matching reference)
NODE_COLORS = {
    "professor": "#f59e0b",  # Amber/Orange
    "topic": "#06b6d4",      # Cyan
    "paper": "#1e3a8a"       # Dark blue
}

# Node Sizes
NODE_SIZES = {
    "professor": 60,
    "topic": 45,
    "paper": 35
}

# Edge Colors
EDGE_COLORS = {
    "expertise": "#94a3b8",    # Light gray
    "authored": "#cbd5e1"      # Very light gray
}

# API Settings
MAX_PAPERS_PER_PROFESSOR = int(os.getenv('MAX_PAPERS_PER_PROFESSOR', 20))
