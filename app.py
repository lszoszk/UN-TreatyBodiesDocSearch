from flask import Flask, render_template, request, send_file
import pandas as pd
import json
import os
import re
from collections import Counter
import io
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, RegexpTokenizer
from nltk import bigrams
from collections import defaultdict
import time
import pickle

app = Flask(__name__)

# Load the GC-info.json file
with open("GC-info.json", "r", encoding="utf-8") as file:
    gc_info = json.load(file)

#nltk.download('stopwords')
#nltk.download('wordnet')
#nltk.download('punkt')

# Load custom stopwords
def load_custom_stopwords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return set(line.strip().lower() for line in file if line.strip())

custom_stopwords_path = "custom_stopwords.txt"
custom_stopwords = load_custom_stopwords(custom_stopwords_path)

# Combine NLTK and custom stopwords
nltk_stopwords = set(stopwords.words('english'))
all_stopwords = nltk_stopwords.union(custom_stopwords)



# Utility function for text formatting
def format_text_for_display(text):
    if text is None:
        return ''  # or some default value
    # Replace patterns like '; (a)' with a line break and the pattern
    formatted_text = re.sub(r'; \(([a-zA-Z])\)', r'<br>; (\1)', text)
    return formatted_text

# Global variable to store the search results temporarily
grouped_results_global = None

# Global cache for storing search results
search_results_cache = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.template_filter('get_info_by_filepath')
def get_info_by_filepath(json_file, gc_info):
    return next((item for item in gc_info if item["File PATH"].endswith(json_file)), None)

def extract_treaty_bodies_from_filename(filename):
    # Known treaty body abbreviations
    known_treaty_bodies = ['CRC', 'CMW', 'ESCR', 'CAT', 'CEDAW']
    # Check if any known treaty body abbreviation is in the filename
    return [tb for tb in known_treaty_bodies if tb in filename]

@app.route('/search', methods=['POST'])
def search():

    raw_query = request.form['search_query'].strip().lower()
    selected_labels = request.form.getlist('labels[]')
    selected_labels = [label.lower() for label in selected_labels]

    # Retrieve the selected treaty body from the form
    selected_treaty_bodies = request.form.getlist('treatyBodies[]')

    # Extract n-grams in quotation marks and individual words
    ngrams = re.findall(r'"([^"]+)"', raw_query)
    words = re.findall(r'\b\w+\b', raw_query)
    query_terms = ngrams + [word for word in words if word not in ' '.join(ngrams)]

    # Split the query into AND and OR terms
    and_terms = [term for term in query_terms if ' or ' not in term]
    or_term_groups = [term.split(' or ') for term in query_terms if ' or ' in term]

    # Function to check if paragraph matches the query terms
    def matches_query(item_text, and_terms, or_term_groups):
        # Check for AND terms
        if any(term not in item_text for term in and_terms):
            return False

        # Check for OR term groups
        for or_terms in or_term_groups:
            if not any(term in item_text for term in or_terms):
                return False

        return True

    # Function to highlight keywords and n-grams
    def highlight_terms(text, terms):
        for term in terms:
            pattern = re.escape(term)
            text = re.sub(pattern, r'<span class="highlight">\g<0></span>', text, flags=re.IGNORECASE)
        return text

    json_dir = "json_data"
    grouped_results = {}
    total_hits = 0
    label_counter = Counter()
    all_text = ""  # Collect all text for word cloud
    committee_counter = defaultdict(int)  # Count the occurrences of each committee
    most_common_words = []
    most_common_bigrams = []

    for json_file in os.listdir(json_dir):
        if json_file.endswith('.json'):
            file_treaty_bodies = extract_treaty_bodies_from_filename(json_file)
            if selected_treaty_bodies and not any(tb in file_treaty_bodies for tb in selected_treaty_bodies):
                continue  # Skip this file if not in selected treaty bodies

            file_path = os.path.join(json_dir, json_file)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            paragraphs = []
            for item in data:
                item_text = item.get('Text', '').lower() if item.get('Text') else ''
                item_labels = [label.lower() for label in item.get('Labels', [])]

                query_match = matches_query(item_text, and_terms, or_term_groups)
                label_match = any(label in item_labels for label in selected_labels) if selected_labels else True

                if query_match and label_match:
                    total_hits += 1
                    paragraph_id = item.get('ID', 'Unknown')
                    highlighted_text = highlight_terms(item.get('Text', ''), query_terms)
                    formatted_text = format_text_for_display(highlighted_text)
                    item_with_highlight = dict(item, Text=formatted_text)
                    paragraphs.append((paragraph_id, item_with_highlight, len(item_labels)))

                    all_text += ' ' + item_text
                    for label in item_labels:
                        label_counter[label] += 1

            if paragraphs:
                additional_info = get_info_by_filepath(json_file, gc_info) or {}
                committee_name = additional_info.get('Committee', 'Unknown Committee')
                committee_counter[committee_name] += len(paragraphs)
                doc_name = additional_info.get('Name', 'Unknown Document')
                grouped_results[doc_name] = {
                    'link': additional_info.get('Link', '#'),
                    'total_count': len(paragraphs),
                    'paragraphs': paragraphs,
                    'committee': additional_info.get('Committee', 'Unknown Committee'),
                    'adoption_date': additional_info.get('Adoption Date', 'Unknown Date'),
                    'signature': additional_info.get('Signature', 'Unknown Signature')
                }

    sorted_results = sorted(grouped_results.items(), key=lambda x: x[1]['total_count'], reverse=True)
    total_docs = len(grouped_results)

    # Get the top 10 most frequent labels
    most_concerned_groups = label_counter.most_common(10)

    # Ensure the cache directory exists
    cache_dir = 'cache'
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    # Cache the search results using pickle
    search_key = str(time.time())  # Unique key for this search
    with open(f'cache/{search_key}.pkl', 'wb') as cache_file:
        pickle.dump(grouped_results, cache_file)

    # Calculate word frequencies for word cloud
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(all_text)
    word_freqs = Counter(word for word in words if word.isalpha() and word not in stop_words)

    # Text processing with custom stopwords
    tokenizer = RegexpTokenizer(r'\w+')
    words = tokenizer.tokenize(all_text.lower())
    filtered_words = [word for word in words if word.isalpha() and word not in all_stopwords]

    # Calculate word frequencies
    word_freqs = Counter(filtered_words)

    # Select the most common words and their counts, if available
    if filtered_words:
        most_common_words = word_freqs.most_common(20)

    # Only proceed with TF-IDF if there are words left after filtering
    if filtered_words:
        # Calculate word frequencies
        word_freqs = Counter(filtered_words)

        # Select the most common words and their counts
        most_common_words = word_freqs.most_common(20)

    # Calculate bigrams from the filtered words
    filtered_bigram_tuples = list(bigrams(filtered_words))
    bigram_freqs = Counter(filtered_bigram_tuples)
    most_common_bigrams = bigram_freqs.most_common(20)

    # Convert committee_counter to a list of tuples for easy template rendering
    committees_with_hits = [(committee, count) for committee, count in committee_counter.items()]

    return render_template('search_results.html',
                           results=sorted_results,
                           query=raw_query,
                           total_hits=total_hits,
                           total_docs=total_docs,
                           search_key=search_key,
                           selected_labels=selected_labels,
                           most_concerned_groups=most_concerned_groups,
                           most_common_words=most_common_words,
                           most_common_bigrams=most_common_bigrams,
                           committees_with_hits=committees_with_hits)

@app.route('/export_to_excel', methods=['POST'])
def export_to_excel():
    search_key = request.form.get('search_key')

    # Retrieve the cached results
    try:
        with open(f'cache/{search_key}.pkl', 'rb') as cache_file:
            grouped_results = pickle.load(cache_file)
    except (FileNotFoundError, pickle.UnpicklingError):
        return "No data to export or error in retrieving data"

    # Process the data and prepare rows for Excel file
    rows = []
    for doc_name, doc_info in grouped_results.items():
        for paragraph_id, paragraph_info, _ in doc_info['paragraphs']:
            # Clean HTML tags from the text
            clean_text = BeautifulSoup(paragraph_info['Text'], 'html.parser').get_text()

            row = {
                'Document Name': doc_name,
                'Paragraph ID': paragraph_id,
                'Text': clean_text,  # Use cleaned text
                'Labels': ', '.join(paragraph_info.get('Labels', [])),
                'Committee': doc_info['committee'],
                'Adoption Date': doc_info['adoption_date'],
                'Signature': doc_info['signature']
            }
            rows.append(row)

    # Create a DataFrame and save to an Excel file in memory
    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Search Results')
    output.seek(0)

    # Send the Excel file as a response
    return send_file(output, as_attachment=True, download_name="search_results.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

#if __name__ == '__main__': # This is for running the app locally and allowing external users to visit your localhost
#    app.run(host='0.0.0.0', debug=True)

if __name__ == '__main__': # This is for running the app locally
    app.run(debug=True)