import streamlit as st
from io import StringIO, BytesIO
import PyPDF2
from docx import Document
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import networkx as nx
from textblob import TextBlob

st.set_page_config(page_title="Text Analysis", layout="wide")
st.title("📄 Text Analysis Tool")
st.caption("Upload a document and instantly generate a word cloud, frequency chart, bigrams or sentiment summary.")

with st.sidebar:
    st.header("Input & Options")
    file = st.file_uploader("Drop file or click to browse", type=["pdf", "docx", "txt"])

    if file is not None:
        with st.spinner("Processing..."):
            file_type = file.type
            text = ''
            if file_type == "text/plain":
                stringio = StringIO(file.getvalue().decode("utf-8"))
                text = stringio.read()
    
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = Document(file)
                text = "\n".join([para.text for para in doc.paragraphs])
    
            elif file_type == "application/pdf":
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
    
            st.markdown("---")
            st.subheader("Operation")
            operation = st.radio("Choose an analysis", ["☁️Word Cloud", "📊Word Frequency (Bar Chart)", "🔗Bigrams (Word Pairs)", "😄Sentiment Analysis"], index=0)
            if operation != "😄Sentiment Analysis":
                st.markdown("---")
                if st.checkbox('Remove Stopwords', value = True):
                    text = text.split()
                    text = [w for w in text if w.lower() not in ENGLISH_STOP_WORDS]
                    text = " ".join(text)
                if not st.checkbox("Case Sensitive"):
                    text = text.lower()
if file is not None:
    if not text.strip():
        st.error("No text found to generate Visualization. Try another file or disable stopword filtering.")
    else:
        with st.spinner("Processing..."):
            if operation == "☁️Word Cloud":
                plt.clf()
                image = WordCloud(width=800, height=400, background_color="white").generate(text)
                plt.imshow(image)
                plt.axis("off")
                st.pyplot(plt, use_container_width=True)
                buf = BytesIO()
                plt.savefig(buf, format="png")
                buf.seek(0) 
                st.download_button(
                    label="Download Plot as PNG",
                    data=buf,
                    file_name="plot.png",
                    mime="image/png"
                )
            elif operation == "📊Word Frequency (Bar Chart)":
                max_words = st.sidebar.slider("Max words", 1, 100, 10)
                text = text.split()
                text = Counter(text)
                text = dict(text.most_common(max_words))
                text = list(text.items())
                labels, values = zip(*text)
                plt.clf()
                plt.barh(labels, values)
                st.pyplot(plt, use_container_width=True)
                buf = BytesIO()
                plt.savefig(buf, format="png")
                buf.seek(0) 
                st.download_button(
                    label="Download Plot as PNG",
                    data=buf,
                    file_name="plot.png",
                    mime="image/png"
                )
            elif operation == "🔗Bigrams (Word Pairs)":
                max_bigrams = st.sidebar.slider("Max Bigrams", 1, 100, 10)
                text = text.split()
                bigrams = list(zip(text, text[1:]))
                bigrams = Counter(bigrams)
                bigrams = dict(bigrams.most_common(max_bigrams))
                G = nx.Graph()
                for (word1, word2), count in bigrams.items():
                    G.add_edge(word1, word2, weight=count)
                pos = nx.spring_layout(G, k=0.8)
                plt.clf()
                plt.figure(figsize=(8, 8))
                nx.draw(G, pos, with_labels=True, node_size=800, node_color="skyblue", font_size=8, font_weight="bold")
                edge_labels = nx.get_edge_attributes(G, 'weight')
                nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
                st.pyplot(plt, use_container_width=True)
                buf = BytesIO()
                plt.savefig(buf, format="png")
                buf.seek(0) 
                st.download_button(
                    label="Download Plot as PNG",
                    data=buf,
                    file_name="plot.png",
                    mime="image/png"
                )
            elif operation == "😄Sentiment Analysis":
                text = text.split("\n")
                sentiment = [TextBlob(line).sentiment.polarity for line in text if line.strip() != '']
                pos = neut = neg = 0
                for score in sentiment:
                    if score > 0.1:
                        pos += 1
                    elif score < -0.1:
                        neg += 1
                    else:
                        neut += 1
                plt.clf()
                plt.pie([pos, neut, neg], labels=["Positive", "Neutral", "Negative"], autopct='%1.1f%%', colors=["green", "gold", "red"])
                st.pyplot(plt, use_container_width=True)
                buf = BytesIO()
                plt.savefig(buf, format="png")
                buf.seek(0) 
                st.download_button(
                    label="Download Plot as PNG",
                    data=buf,
                    file_name="plot.png",
                    mime="image/png"
        
                )




