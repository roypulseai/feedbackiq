import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from transformers import pipeline
from bertopic import BERTopic

st.set_page_config(page_title="FeedbackIQ", layout="wide")

st.markdown("""
<style>
    .block-container { padding: 1.5rem 2rem !important; }
    .stApp { background: #f8f9fa; }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #eaeaea;
        border-radius: 8px;
        padding: 0.75rem 1rem;
    }
    .stButton > button { border-radius: 6px; font-weight: 500; }
    .data-preview { border: 1px solid #eaeaea; border-radius: 8px; overflow: hidden; }
    .step-indicator {
        display: flex; gap: 1rem; margin: 1.5rem 0;
    }
    .step {
        flex: 1; background: white; border: 1px solid #eaeaea;
        border-radius: 8px; padding: 1.25rem; text-align: center;
    }
    .step .num {
        display: inline-flex; align-items: center; justify-content: center;
        width: 28px; height: 28px; border-radius: 50%;
        background: #1a1a2e; color: white; font-size: 0.85rem; font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .step h4 { margin: 0.25rem 0; font-size: 1rem; color: #1a1a2e; }
    .step p { margin: 0; font-size: 0.8rem; color: #888; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_models():
    sentiment_model = pipeline(
        "text-classification", 
        model="lxyuan/distilbert-base-multilingual-cased-sentiments-student"
    )
    topic_model = BERTopic(language="multilingual")
    return sentiment_model, topic_model

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "topic_info" not in st.session_state:
    st.session_state.topic_info = pd.DataFrame()

st.markdown("<h1 style='margin-bottom:0.25rem'>FeedbackIQ</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#666; margin-top:0; margin-bottom:1.5rem'>Multilingual sentiment and topic analysis for user feedback</p>", unsafe_allow_html=True)

# --- Sidebar: Data Ingestion ---
with st.sidebar:
    st.markdown("<p style='font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; color:#999; margin-bottom:0.25rem'>Data Source</p>", unsafe_allow_html=True)
    data_source = st.radio("input_method", ["CSV Upload", "PostgreSQL Connection"], label_visibility="collapsed")

    if data_source == "CSV Upload":
        uploaded_file = st.file_uploader("Upload CSV File", type=["csv"], label_visibility="collapsed")
        if uploaded_file:
            new_df = pd.read_csv(uploaded_file)
            st.session_state.df = new_df
            st.session_state.analyzed = False
            st.session_state.topic_info = pd.DataFrame()
            st.success(f"Loaded {len(new_df)} rows")

    elif data_source == "PostgreSQL Connection":
        db_uri = st.text_input("Database URI", type="password", placeholder="postgresql://user:pass@host:5432/db")
        query = st.text_area("SQL Query", value="SELECT * FROM feedback LIMIT 1000;", height=100)
        if st.button("Execute Query", use_container_width=True):
            try:
                engine = create_engine(db_uri)
                with engine.connect() as conn:
                    new_df = pd.read_sql(text(query), conn)
                st.session_state.df = new_df
                st.session_state.analyzed = False
                st.session_state.topic_info = pd.DataFrame()
                st.success(f"Loaded {len(new_df)} rows")
            except Exception as e:
                st.error(f"Connection error: {e}")

# --- Main Content ---
df = st.session_state.df

if df.empty:
    st.markdown("""
    <div class="step-indicator">
        <div class="step">
            <div class="num">1</div>
            <h4>Load Data</h4>
            <p>Upload a CSV or connect to a PostgreSQL database using the sidebar.</p>
        </div>
        <div class="step">
            <div class="num">2</div>
            <h4>Select Column</h4>
            <p>Pick the text column containing user feedback to analyze.</p>
        </div>
        <div class="step">
            <div class="num">3</div>
            <h4>Analyze & Explore</h4>
            <p>Run NLP analysis, then explore sentiment and topic results.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    with st.expander("Data Preview", expanded=not st.session_state.analyzed):
        st.dataframe(df.head(10), use_container_width=True)
        st.caption(f"{len(df)} rows x {len(df.columns)} columns")

    text_column = st.selectbox("Select the feedback text column", df.columns, key="text_col")

    col1, col2 = st.columns([1, 5])
    with col1:
        run_btn = st.button("Run Analysis", type="primary", use_container_width=True)

    if run_btn and text_column:
        documents = df[text_column].dropna().astype(str).tolist()

        if not documents:
            st.warning("The selected column contains no text data.")
        else:
            sentiment_analyzer, topic_model = load_models()

            with st.status("Analyzing feedback...", expanded=True) as status:
                st.write("Running sentiment classification...")
                sentiment_results = sentiment_analyzer(documents, truncation=True, max_length=512, batch_size=8)

                st.write("Discovering topics...")
                topics, _ = topic_model.fit_transform(documents)

                topic_info = topic_model.get_topic_info()
                status.update(label="Analysis complete", state="complete", expanded=False)

            df.loc[df[text_column].notna(), "Sentiment"] = [r["label"].title() for r in sentiment_results]
            df.loc[df[text_column].notna(), "Confidence"] = [round(r["score"], 3) for r in sentiment_results]
            df.loc[df[text_column].notna(), "Topic_ID"] = topics
            topic_mapping = dict(zip(topic_info["Topic"], topic_info["Name"]))
            df["Topic_Name"] = df["Topic_ID"].map(topic_mapping)

            st.session_state.df = df
            st.session_state.topic_info = topic_info
            st.session_state.analyzed = True

    if st.session_state.analyzed and "Sentiment" in df.columns:
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Entries", len(df))
        with m2:
            dominant = df["Sentiment"].value_counts().idxmax()
            st.metric("Dominant Sentiment", dominant)
        with m3:
            n_topics = df["Topic_ID"].nunique()
            n_topics = n_topics - 1 if -1 in df["Topic_ID"].values else n_topics
            st.metric("Topics Found", n_topics)
        with m4:
            avg_conf = df["Confidence"].mean()
            st.metric("Avg Confidence", f"{avg_conf:.1%}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Sentiment Distribution**")
            sentiment_counts = df["Sentiment"].value_counts()
            st.bar_chart(sentiment_counts)
        with col2:
            st.markdown("**Top Topics**")
            topic_info_valid = st.session_state.topic_info
            topic_info_valid = topic_info_valid[topic_info_valid["Topic"] != -1].head(10)

            if not topic_info_valid.empty:
                st.bar_chart(topic_info_valid.set_index("Name")["Count"])
            else:
                st.info("No distinct topics found. Try providing more diverse feedback data.")

        st.markdown("**Detailed Results**")
        display_cols = [text_column, "Sentiment", "Confidence", "Topic_Name"]
        display_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(df[display_cols], use_container_width=True)

        csv_export = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Results as CSV",
            data=csv_export,
            file_name="feedbackiq_results.csv",
            mime="text/csv",
            use_container_width=True,
        )
