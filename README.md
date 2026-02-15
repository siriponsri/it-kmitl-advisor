# IT KMITL Advisor Knowledge Graph

ระบบค้นหาอาจารย์ที่ปรึกษาตามความเชี่ยวชาญ พร้อม Knowledge Graph และ Analytics Dashboard

## 🚀 Quick Start

### 1. Setup

```bash
# Clone repository
git clone <your-repo-url>
cd km-graph

# Install dependencies
pip install -r requirements.txt

# Add your Scopus API key to .env
SCOPUS_API_KEY=your_api_key_here
```

### 2. Fetch Data (One-Time)

```bash
# Scrape professor list from IT KMITL
python fetch_professors.py

# Fetch research data from Scopus (takes 10-30 min)
python fetch_all_scopus_data.py
```

### 3. Run App

```bash
streamlit run app.py
```

---

## ✨ Features

### 📊 Summary & Analytics
- Overview metrics (professors, papers, citations)
- Top 15 professors by citations
- Research topics distribution
- Most cited papers

### 👤 Professor Profiles
- Interactive knowledge graphs
- Publications list with citations
- Research topics & expertise areas
- Links to IT KMITL and Scopus profiles

### 🔍 Filter by Topic
- Browse professors by research topic
- View papers grouped by topics
- Compare researchers in the same field

### 📚 All Professors
- Search by name or topic
- Sort by citations/papers
- Quick overview table

---

## 🎯 Key Advantages

✅ **Fast** - All data pre-cached, instant loading  
✅ **Efficient** - No API calls during app usage  
✅ **Offline** - Works without internet after initial fetch  
✅ **Analytics** - Built-in research analytics dashboard  
✅ **Clean Design** - Professional minimal interface  

---

## 🔄 Updating Data

```bash
# Re-run periodically (e.g., monthly or quarterly)
python fetch_professors.py          # Update professor list
python fetch_all_scopus_data.py     # Update research data
```

---

## 📁 Project Structure

```
├── app.py                         # Main Streamlit app
├── fetch_all_scopus_data.py       # Fetch & cache Scopus data
├── fetch_professors.py            # Scrape IT KMITL website
├── scopus_client.py               # Scopus API client
├── scraper.py                     # Web scraper
├── graph_builder.py               # Graph generator
├── config.py                      # Configuration
├── .env                           # API keys (not in git)
├── data/
│   ├── professors_basic.json      # Professor list
│   ├── professors_scopus_data.json # Research data (flat)
│   ├── professors_by_topics.json   # Research data (grouped)
│   └── graphs/                    # Pre-generated graphs
└── requirements.txt
```

---

## 🔑 Get Scopus API Key

1. Visit https://dev.elsevier.com
2. Create account → My API Key
3. Create new API Key (free tier available)
4. Add to `.env`:
   ```
   SCOPUS_API_KEY=your_key_here
   ```

---

## 💡 Use Cases

**Find Advisor by Research Area:**
- Use "Filter by Topic" page
- Select your research interest
- Browse professors and their papers

**Compare Researcher Impact:**
- Check "Summary & Analytics" 
- View Top Professors by Citations
- Analyze individual knowledge graphs

**Discover Papers:**
- Browse by topic on "Filter by Topic"
- View papers sorted by citations
- Click DOI links to read papers

---

## 🚀 Deployment

### Streamlit Cloud

1. Push to GitHub
2. Go to https://streamlit.io/cloud
3. Create new app → Select repository
4. Add Scopus API key in app secrets:
   ```toml
   SCOPUS_API_KEY = "your_key_here"
   ```
5. Make sure data files are committed or re-fetch on deployment

### Important Files to Commit
- All `.py` files
- `requirements.txt`
- `.env.example` (template)
- Optional: `data/*.json` (if you want pre-loaded data)
- Optional: `data/graphs/*.html` (if you want pre-generated graphs)

---

## 📊 Data

- **29 Professors** from IT KMITL
- **520+ Papers** from Scopus
- **3,600+ Citations** tracked
- Updated: February 2026

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Visualization:** PyVis, Plotly
- **Data:** Scopus API, Web Scraping (BeautifulSoup4)
- **Graph:** NetworkX

---

**Built by:** IT KMITL Students  
**License:** MIT
