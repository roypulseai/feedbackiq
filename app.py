import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from transformers import pipeline
from bertopic import BERTopic

st.set_page_config(page_title="FeedbackIQ", layout="wide")

@st.cache_resource
def load_models():
    sentiment_model = pipeline(
        "text-classification", 
        model="lxyuan/distilbert-base-multilingual-cased-sentiments-student"
    )
    topic_model = BERTopic(language="multilingual")
    return sentiment_model, topic_model

sentiment_analyzer, topic_model = load_models()

st.title("FeedbackIQ")
st.write("Multilingual sentiment analysis and topic modeling for user feedback.")

# --- Data Ingestion ---
st.sidebar.header("1. Data Source")
data_source = st.sidebar.radio("Select Input Method", ["CSV Upload", "PostgreSQL Connection"])

df = pd.DataFrame()

if data_source == "CSV Upload":
    uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success("CSV loaded successfully!")

elif data_source == "PostgreSQL Connection":
    db_uri = st.sidebar.text_input("Database URI", type="password")
    query = st.sidebar.text_area("SQL Query", value="SELECT * FROM feedback_table LIMIT 1000;")
    
    if st.sidebar.button("Execute Query"):
        try:
            engine = create_engine(db_uri)
            with engine.connect() as conn:
                df = pd.read_sql(text(query), conn)
            st.sidebar.success(f"Loaded {len(df)} rows!")
        except Exception as e:
            st.sidebar.error(f"Connection error: {e}")

# --- NLP Processing & Dashboard ---
if not df.empty:
    text_column = st.selectbox("Select the column containing the feedback text:", df.columns)
    
    if st.button("Run NLP Analysis"):
        with st.spinner("Processing text..."):
            documents = df[text_column].dropna().astype(str).tolist()
            
            try:
                sentiment_results = sentiment_analyzer(documents, truncation=True, max_length=512, batch_size=8)
                df.loc[df[text_column].notna(), 'Sentiment'] = [res['label'].title() for res in sentiment_results]
                df.loc[df[text_column].notna(), 'Confidence'] = [round(res['score'], 3) for res in sentiment_results]
                
                topics, _ = topic_model.fit_transform(documents)
                df.loc[df[text_column].notna(), 'Topic_ID'] = topics
                
                topic_info = topic_model.get_topic_info()
                topic_mapping = dict(zip(topic_info['Topic'], topic_info['Name']))
                df['Topic_Name'] = df['Topic_ID'].map(topic_mapping)
                
                st.success("Analysis Complete!")
                
                st.divider()
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Sentiment Distribution**")
                    sentiment_counts = df['Sentiment'].value_counts().reset_index()
                    sentiment_counts.columns = ['Sentiment', 'Count']
                    st.bar_chart(sentiment_counts, x='Sentiment', y='Count')
                with col2:
                    st.write("**Top Topics Discovered**")
                    valid_topics = topic_info[topic_info['Topic'] != -1].head(10)
                    if not valid_topics.empty:
                        st.bar_chart(valid_topics, x='Name', y='Count')
                    else:
                        st.write("No distinct topics found.")

                st.write("**Detailed Feedback Table**")
                st.dataframe(df[[text_column, 'Sentiment', 'Confidence', 'Topic_Name']], use_container_width=True)
                
                csv_export = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download Results as CSV", data=csv_export, file_name='analyzed_feedback.csv', mime='text/csv')
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
else:
    st.info("Load data via the sidebar to begin.")
