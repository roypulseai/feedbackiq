from transformers import pipeline
from bertopic import BERTopic

print("Pre-loading multilingual NLP models for FeedbackIQ...")
pipeline("text-classification", model="lxyuan/distilbert-base-multilingual-cased-sentiments-student")
BERTopic(language="multilingual")
print("Models successfully cached!")
