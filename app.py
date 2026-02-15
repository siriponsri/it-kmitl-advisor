"""
IT KMITL Advisor Knowledge Graph - Main Streamlit Application (Cache-Based)
Interactive dashboard with pre-cached research data and analytics
"""

import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
import streamlit.components.v1 as components
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="IT KMITL Advisor Finder",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: #1e40af;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 400;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .professor-card {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    .stat-box {
        background-color: #f1f5f9;
        padding: 1rem;
        border-radius: 6px;
        text-align: center;
        border: 1px solid #cbd5e1;
    }
    .stButton>button {
        background-color: #1e40af;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1e3a8a;
    }
    .topic-badge {
        display: inline-block;
        background-color: #cbd5e1;
        color: #1e3a8a;
        padding: 0.3rem 0.8rem;
        border-radius: 16px;
        margin: 0.2rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'professors_data' not in st.session_state:
    st.session_state.professors_data = {}
if 'metadata' not in st.session_state:
    st.session_state.metadata = {}

CACHE_DIR = Path(os.getenv('CACHE_DIRECTORY', 'data'))
SCOPUS_CACHE_FILE = CACHE_DIR / 'professors_scopus_data.json'
TOPICS_CACHE_FILE = CACHE_DIR / 'professors_by_topics.json'
GRAPHS_DIR = CACHE_DIR / 'graphs'


def get_paper_count(professor_data):
    """Get paper count from either format (papers array or topic_groups)"""
    if 'papers' in professor_data:
        return len(professor_data['papers'])
    elif 'topic_groups' in professor_data:
        total = 0
        for papers_list in professor_data['topic_groups'].values():
            total += len(papers_list)
        return total
    return 0


def get_all_papers(professor_data):
    """Get all papers from either format (papers array or topic_groups)"""
    if 'papers' in professor_data:
        return professor_data['papers']
    elif 'topic_groups' in professor_data:
        all_papers = []
        for papers_list in professor_data['topic_groups'].values():
            all_papers.extend(papers_list)
        return all_papers
    return []


def load_scopus_cache():
    """Load pre-cached Scopus data - prioritize topic-grouped version"""
    # Try to load topic-grouped version first
    if TOPICS_CACHE_FILE.exists():
        with open(TOPICS_CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
            return cache_data.get('professors', {}), cache_data.get('metadata', {})
    
    # Fallback to original format
    if SCOPUS_CACHE_FILE.exists():
        with open(SCOPUS_CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
            return cache_data.get('professors', {}), cache_data.get('metadata', {})
    
    return None, None


def load_professor_graph(scopus_id):
    """Load pre-generated graph HTML"""
    graph_file = GRAPHS_DIR / f"{scopus_id}.html"
    
    if graph_file.exists():
        with open(graph_file, 'r', encoding='utf-8') as f:
            return f.read()
    return None


# Header
st.markdown('<div class="main-header">IT KMITL Advisor Finder</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Knowledge Graph System | ระบบค้นหาอาจารย์ที่ปรึกษาตามความเชี่ยวชาญ</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Navigation")
    
    # Load data button
    if st.button("⬇ Load Data", width="stretch"):
        professors_data, metadata = load_scopus_cache()
        
        if professors_data:
            st.session_state.professors_data = professors_data
            st.session_state.metadata = metadata
            st.session_state.data_loaded = True
            st.success(f"Loaded {len(professors_data)} professors")
        else:
            st.error("No cached data found!")
            st.info("""
            Please run this command first:
            ```
            python fetch_all_scopus_data.py
            ```
            """)
    
    if st.session_state.data_loaded:
        st.markdown("---")
        
        # Show cache info
        st.subheader("Cache Info")
        fetched_at = st.session_state.metadata.get('fetched_at', 'Unknown')
        if fetched_at != 'Unknown':
            try:
                dt = datetime.fromisoformat(fetched_at)
                st.write(f"**Updated:** {dt.strftime('%Y-%m-%d %H:%M')}")
            except:
                st.write(f"**Updated:** {fetched_at}")
        
        st.write(f"**Professors:** {st.session_state.metadata.get('professor_count', 0)}")
        st.write(f"**Total Papers:** {st.session_state.metadata.get('total_papers', 0)}")
        st.write(f"**Total Citations:** {st.session_state.metadata.get('total_citations', 0)}")
        
        st.markdown("---")
        
        # Page selection
        page = st.radio(
            "Choose Page:",
            ["■ Summary & Analytics", "● Professor Profile", "▤ All Professors", "◆ Filter by Topic"],
            label_visibility="collapsed"
        )
    else:
        page = None
        st.info("Click 'Load Data' to begin")


# Main content
if not st.session_state.data_loaded:
    st.info("← Click 'Load Data' in the sidebar to start")
    
    st.markdown("### Quick Start:")
    st.markdown("""
    1. **First Time Setup:**
       ```bash
       # Add your Scopus API key to .env file
       SCOPUS_API_KEY=your_key_here
       
       # Fetch all professor data (run once, or periodically to update)
       python fetch_professors.py
       python fetch_all_scopus_data.py
       ```
    
    2. **Using the App:**
       - Click "Load Data" in the sidebar
       - Explore Summary & Analytics page
       - Browse individual professor profiles
    
    3. **Updating Data:**
       - Re-run `fetch_all_scopus_data.py` periodically (e.g., monthly)
       - All graphs are pre-generated for fast loading
    """)

elif page == "■ Summary & Analytics":
    st.markdown('<div class="main-header">Research Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">IT KMITL Faculty Research Overview</div>', unsafe_allow_html=True)
    
    professors = st.session_state.professors_data
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_papers = sum(get_paper_count(p) for p in professors.values())
    total_citations = sum(p.get('citation_count', 0) for p in professors.values())
    avg_citations = total_citations / len(professors) if professors else 0
    
    with col1:
        st.metric("Total Professors", len(professors))
    with col2:
        st.metric("Total Papers", total_papers)
    with col3:
        st.metric("Total Citations", f"{total_citations:,}")
    with col4:
        st.metric("Avg Citations/Prof", f"{avg_citations:.0f}")
    
    st.markdown("---")
    
    # Top professors chart
    st.subheader("Top 15 Professors by Citations")
    
    prof_list = []
    for scopus_id, prof in professors.items():
        prof_list.append({
            'Name': prof.get('name', 'Unknown'),
            'Citations': prof.get('citation_count', 0),
            'Papers': get_paper_count(prof),
            'Topics': len(prof.get('topics', [])),
            'Scopus ID': scopus_id
        })
    
    df_profs = pd.DataFrame(prof_list)
    df_profs = df_profs.sort_values('Citations', ascending=False)
    
    # Bar chart
    fig_profs = px.bar(
        df_profs.head(15),
        x='Citations',
        y='Name',
        orientation='h',
        title='',
        color='Citations',
        color_continuous_scale='Blues',
        text='Citations'
    )
    fig_profs.update_layout(
        height=500,
        showlegend=False,
        xaxis_title="Citations",
        yaxis_title="",
        font=dict(size=13),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig_profs.update_traces(texttemplate='%{text}', textposition='outside')
    fig_profs.update_yaxes(autorange="reversed")
    
    st.plotly_chart(fig_profs, width='stretch')
    
    st.markdown("---")
    
    # Research topics
    st.subheader("Research Topics Distribution")
    
    topic_count = {}
    topic_professors = {}
    
    for scopus_id, prof in professors.items():
        name = prof.get('name', 'Unknown')
        for topic in prof.get('topics', []):
            if topic not in topic_count:
                topic_count[topic] = 0
                topic_professors[topic] = []
            topic_count[topic] += 1
            topic_professors[topic].append(name)
    
    topic_data = [{'Topic': topic, 'Count': count} for topic, count in topic_count.items()]
    df_topics = pd.DataFrame(topic_data)
    
    if not df_topics.empty:
        df_topics = df_topics.sort_values('Count', ascending=False)
    
    if not df_topics.empty:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Bar chart for topics
            fig_topics = px.bar(
                df_topics.head(15),
                x='Count',
                y='Topic',
                orientation='h',
                title='Top 15 Research Topics',
                color='Count',
                color_continuous_scale='Greens',
                text='Count'
            )
            fig_topics.update_layout(
                height=500,
                showlegend=False,
                xaxis_title="Number of Professors",
                yaxis_title="",
                font=dict(size=12),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            fig_topics.update_traces(texttemplate='%{text}', textposition='outside')
            fig_topics.update_yaxes(autorange="reversed")
            
            st.plotly_chart(fig_topics, width='stretch')
        
        with col2:
            # Pie chart for top 10
            fig_pie = px.pie(
                df_topics.head(10),
                values='Count',
                names='Topic',
                title='Top 10 Topics Distribution',
                hole=0.4
            )
            fig_pie.update_layout(
                height=500,
                font=dict(size=12),
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", y=0.5)
            )
            
            st.plotly_chart(fig_pie, width='stretch')
    else:
        st.info("No research topics found in the data")
    
    st.markdown("---")
    
    # Most cited papers
    st.subheader("Top 20 Most Cited Papers")
    
    all_papers = []
    for scopus_id, prof in professors.items():
        prof_name = prof.get('name', 'Unknown')
        for paper in get_all_papers(prof):
            all_papers.append({
                'Professor': prof_name,
                'Title': paper.get('title', 'Untitled'),
                'Year': paper.get('year', ''),
                'Citations': paper.get('citations', 0)
            })
    
    df_papers = pd.DataFrame(all_papers)
    df_papers = df_papers.sort_values('Citations', ascending=False)
    
    # Bar chart for papers
    df_papers_top = df_papers.head(20).copy()
    df_papers_top['Short_Title'] = df_papers_top['Title'].apply(lambda x: x[:60] + '...' if len(x) > 60 else x)
    
    fig_papers = px.bar(
        df_papers_top,
        x='Citations',
        y='Short_Title',
        orientation='h',
        title='',
        color='Citations',
        color_continuous_scale='Purples',
        text='Citations',
        hover_data=['Professor', 'Year', 'Title']
    )
    fig_papers.update_layout(
        height=600,
        showlegend=False,
        xaxis_title="Citations",
        yaxis_title="",
        font=dict(size=11),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig_papers.update_traces(texttemplate='%{text}', textposition='outside')
    fig_papers.update_yaxes(autorange="reversed")
    
    st.plotly_chart(fig_papers, width='stretch')

elif page == "● Professor Profile":
    st.header("Professor Profile")
    
    professors = st.session_state.professors_data
    
    # Professor selection
    prof_names = sorted([p.get('name', 'Unknown') for p in professors.values()])
    
    selected_name = st.selectbox("Select a professor:", prof_names)
    
    # Find professor data
    selected_prof = None
    selected_scopus_id = None
    
    for scopus_id, prof in professors.items():
        if prof.get('name') == selected_name:
            selected_prof = prof
            selected_scopus_id = scopus_id
            break
    
    if selected_prof:
        # Profile header
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if selected_prof.get('image_url'):
                try:
                    st.image(selected_prof['image_url'], width=180)
                except:
                    st.info("No image")
        
        with col2:
            st.markdown(f"### {selected_prof['name']}")
            
            if selected_prof.get('thai_name'):
                st.markdown(f"**ชื่อภาษาไทย:** {selected_prof['thai_name']}")
            
            if selected_prof.get('profile_url'):
                st.markdown(f"[🔗 IT KMITL Profile]({selected_prof['profile_url']})")
            
            if selected_prof.get('scopus_url'):
                st.markdown(f"[🔗 Scopus Profile]({selected_prof['scopus_url']})")
            
            # Quick stats
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Papers", get_paper_count(selected_prof))
            with col_b:
                st.metric("Citations", selected_prof.get('citation_count', 0))
            with col_c:
                st.metric("Topics", len(selected_prof.get('topics', [])))
        
        st.markdown("---")
        
        # Tabs
        tab1, tab2, tab3 = st.tabs(["📊 Knowledge Graph", "📚 Publications", "🔬 Research Topics"])
        
        with tab1:
            st.subheader(f"Knowledge Graph: {selected_prof['name']}")
            
            # Load pre-generated graph
            graph_html = load_professor_graph(selected_scopus_id)
            
            if graph_html:
                components.html(graph_html, height=850, scrolling=False)
                st.info("💡 **Tip:** Drag nodes, scroll to zoom, hover for details")
            else:
                st.warning("Graph not found. Run `fetch_all_scopus_data.py` to generate graphs.")
        
        with tab2:
            st.subheader("Publication List")
            
            papers = get_all_papers(selected_prof)
            
            if papers:
                df_papers = pd.DataFrame(papers)
                
                if 'year' in df_papers.columns:
                    df_papers = df_papers.sort_values('year', ascending=False)
                
                st.dataframe(
                    df_papers[['title', 'year', 'citations']],
                    width="stretch",
                    hide_index=True
                )
                
                # Summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Papers", len(papers))
                with col2:
                    total_cites = sum(p.get('citations', 0) for p in papers)
                    st.metric("Total Citations", total_cites)
                with col3:
                    avg_cites = total_cites / len(papers) if papers else 0
                    st.metric("Avg Citations", f"{avg_cites:.1f}")
            else:
                st.info("No publications found")
        
        with tab3:
            st.subheader("Research Topics")
            
            topics = selected_prof.get('topics', [])
            
            if topics:
                st.markdown("### Areas of Expertise:")
                
                # Display as badges
                html_badges = " ".join([f'<span class="topic-badge">{topic}</span>' for topic in topics])
                st.markdown(html_badges, unsafe_allow_html=True)
                
                st.markdown(f"<br>**Total Topics:** {len(topics)}", unsafe_allow_html=True)
            else:
                st.info("No research topics found")

elif page == "▤ All Professors":
    st.header("All Professors")
    
    professors = st.session_state.professors_data
    
    # Search/filter
    search = st.text_input("🔍 Search by name or topic:")
    
    # Create list
    prof_list = []
    for scopus_id, prof in professors.items():
        prof_list.append({
            'Name': prof.get('name', 'Unknown'),
            'Topics': ', '.join(prof.get('topics', [])[:3]),
            'Papers': get_paper_count(prof),
            'Citations': prof.get('citation_count', 0),
            'Scopus ID': scopus_id
        })
    
    df = pd.DataFrame(prof_list)
    
    # Filter
    if search:
        mask = df['Name'].str.contains(search, case=False, na=False) | \
               df['Topics'].str.contains(search, case=False, na=False)
        df = df[mask]
    
    # Sort
    sort_by = st.selectbox("Sort by:", ['Name', 'Citations', 'Papers'])
    df = df.sort_values(sort_by, ascending=(sort_by == 'Name'))
    
    # Display
    st.dataframe(
        df[['Name', 'Topics', 'Papers', 'Citations']],
        width="stretch",
        hide_index=True
    )
    
    st.write(f"Showing {len(df)} professors")

elif page == "◆ Filter by Topic":
    st.header("Filter Professors by Research Topic")
    st.markdown("เลือก Topic เพื่อดูอาจารย์และงานวิจัยในสาขานั้นๆ")
    
    professors = st.session_state.professors_data
    
    # Collect all topics
    all_topics = {}
    for scopus_id, prof in professors.items():
        for topic in prof.get('topics', []):
            if topic not in all_topics:
                all_topics[topic] = []
            all_topics[topic].append({
                'scopus_id': scopus_id,
                'name': prof.get('name', 'Unknown'),
                'thai_name': prof.get('thai_name', ''),
                'citation_count': prof.get('citation_count', 0),
                'paper_count': get_paper_count(prof),
                'prof_data': prof
            })
    
    # Sort topics by number of professors
    sorted_topics = sorted(all_topics.items(), key=lambda x: len(x[1]), reverse=True)
    
    # Topic selector
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_topic = st.selectbox(
            "Select Research Topic:",
            options=[topic for topic, _ in sorted_topics],
            format_func=lambda x: f"{x} ({len(all_topics[x])} professors)"
        )
    
    with col2:
        st.metric("Professors", len(all_topics[selected_topic]))
    
    if selected_topic:
        st.markdown("---")
        
        # Sort professors by citations
        professors_in_topic = sorted(
            all_topics[selected_topic], 
            key=lambda x: x['citation_count'], 
            reverse=True
        )
        
        st.subheader(f"{selected_topic}")
        st.write(f"Found {len(professors_in_topic)} professors researching in this topic")
        
        # Display each professor
        for idx, prof_info in enumerate(professors_in_topic, 1):
            prof_name = prof_info['name']
            thai_name = prof_info['thai_name']
            paper_count = prof_info['paper_count']
            citations = prof_info['citation_count']
            scopus_id = prof_info['scopus_id']
            prof_data = prof_info['prof_data']
            
            # H1 Row: Professor Name (expandable)
            with st.expander(
                f"**{idx}. {prof_name}** | {thai_name} | {paper_count} papers | {citations} citations",
                expanded=False
            ):
                # Profile info
                col_a, col_b = st.columns([1, 3])
                
                with col_a:
                    if prof_data.get('image_url'):
                        try:
                            st.image(prof_data['image_url'], width=150)
                        except:
                            pass
                
                with col_b:
                    st.markdown(f"### {prof_name}")
                    if thai_name:
                        st.markdown(f"**ชื่อภาษาไทย:** {thai_name}")
                    
                    if prof_data.get('profile_url'):
                        st.markdown(f"[IT KMITL Profile]({prof_data['profile_url']})")
                    if prof_data.get('scopus_url'):
                        st.markdown(f"[Scopus Profile]({prof_data['scopus_url']})")
                    
                    # Quick stats
                    col_x, col_y, col_z = st.columns(3)
                    with col_x:
                        st.metric("Papers", paper_count)
                    with col_y:
                        st.metric("Citations", citations)
                    with col_z:
                        st.metric("Topics", len(prof_data.get('topics', [])))
                
                st.markdown("---")
                
                # H2 Row: Papers (expandable by topic if topic_groups exists)
                all_papers = get_all_papers(prof_data)
                
                # Filter papers related to selected topic
                if 'topic_groups' in prof_data and selected_topic in prof_data['topic_groups']:
                    topic_papers = prof_data['topic_groups'][selected_topic]
                    st.markdown(f"#### Papers in {selected_topic} ({len(topic_papers)})")
                    
                    # Show papers in this topic
                    for paper_idx, paper in enumerate(topic_papers, 1):
                        paper_title = paper.get('title', 'Untitled')
                        paper_year = paper.get('year', 'N/A')
                        paper_citations = paper.get('citations', 0)
                        paper_doi = paper.get('doi', '')
                        
                        st.markdown(f"""
                        **{paper_idx}. {paper_title}**  
                        Year: {paper_year} | Citations: {paper_citations}  
                        {f'[DOI](https://doi.org/{paper_doi})' if paper_doi else ''}
                        """)
                        st.markdown("---")
                    
                    # Show other papers if exists
                    other_topics = {k: v for k, v in prof_data.get('topic_groups', {}).items() if k != selected_topic}
                    if other_topics:
                        with st.expander(f"View papers in other topics ({sum(len(v) for v in other_topics.values())} papers)"):
                            for other_topic, papers_list in other_topics.items():
                                st.markdown(f"**{other_topic}** ({len(papers_list)} papers)")
                                for p_idx, p in enumerate(papers_list, 1):
                                    st.markdown(f"- {p.get('title', 'Untitled')} ({p.get('year', 'N/A')})")
                else:
                    # Flat structure - show all papers
                    st.markdown(f"#### All Papers ({len(all_papers)})")
                    
                    # Filter papers that mention the topic in title
                    related_papers = [p for p in all_papers if selected_topic.lower() in p.get('title', '').lower()]
                    other_papers = [p for p in all_papers if selected_topic.lower() not in p.get('title', '').lower()]
                    
                    if related_papers:
                        st.markdown(f"**Related to {selected_topic}:** ({len(related_papers)})")
                        for paper_idx, paper in enumerate(related_papers, 1):
                            paper_title = paper.get('title', 'Untitled')
                            paper_year = paper.get('year', 'N/A')
                            paper_citations = paper.get('citations', 0)
                            paper_doi = paper.get('doi', '')
                            
                            st.markdown(f"""
                            **{paper_idx}. {paper_title}**  
                            Year: {paper_year} | Citations: {paper_citations}  
                            {f'[DOI](https://doi.org/{paper_doi})' if paper_doi else ''}
                            """)
                            st.markdown("---")
                    
                    if other_papers:
                        with st.expander(f"View other papers ({len(other_papers)} papers)"):
                            for p_idx, p in enumerate(other_papers, 1):
                                st.markdown(f"- {p.get('title', 'Untitled')} ({p.get('year', 'N/A')})")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>IT KMITL Advisor Knowledge Graph | Built with Streamlit & Scopus API</p>
    <p>Data source: <a href='https://www.it.kmitl.ac.th/th/staffs/academic'>IT KMITL Staff Directory</a> & <a href='https://www.scopus.com/'>Scopus</a></p>
</div>
""", unsafe_allow_html=True)
