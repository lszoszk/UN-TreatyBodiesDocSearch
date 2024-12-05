from flask import Flask, render_template, request, send_file, jsonify
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
from nltk.util import ngrams as nltk_ngrams
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

def get_all_committees():
    committees = set()
    for item in gc_info:
        if 'Committee' in item:
            [committees.add(committee.strip()) for committee in item['Committee'].split(',')]
    return sorted(committees)

def get_documents_for_committee(committee):
    documents = []
    for item in gc_info:
        committees = [x.strip() for x in item.get('Committee', '').split(',')]
        if committee in committees:
            file_name = os.path.basename(item.get('File PATH', ''))
            document_id, _ = os.path.splitext(file_name)
            documents.append({
                'name': item.get('Name', 'Unknown Document'),
                'id': document_id,
                'committee': ', '.join(committees)
            })
    return documents

def get_document_content(document_id):
    # Fetch additional details like title, signature, and date of adoption
    additional_info = next((item for item in gc_info if item["File PATH"].endswith(document_id + '.json')), None)
    title = additional_info.get('Name', 'Unknown Document') if additional_info else 'Unknown Document'
    signature = additional_info.get('Signature', 'Unknown Signature') if additional_info else 'Unknown Signature'
    adoption_year = additional_info.get('Adoption year', 'Unknown year') if additional_info else 'Unknown year'

    json_dir = "json_data"
    file_path = os.path.join(json_dir, document_id + '.json')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            paragraphs = [str(index + 1) + '. ' + (item.get('Text') or '') for index, item in enumerate(data)]
            return {
                'title': title,
                'signature': signature,
                'adoption_year': adoption_year,
                'paragraphs': paragraphs
            }
    else:
        return {'title': 'Document not found', 'paragraphs': []}

@app.route('/')
def index():
    return render_template('index.html')

@app.template_filter('get_info_by_filepath')
def get_info_by_filepath(json_file, gc_info):
    return next((item for item in gc_info if item["File PATH"].endswith(json_file)), None)

def extract_treaty_bodies_from_filename(filename):
    # Known treaty body abbreviations
    known_treaty_bodies = ['CRC', 'CMW', 'ESCR', 'CAT', 'CEDAW', 'CCPR']
    # Check if any known treaty body abbreviation is in the filename
    return [tb for tb in known_treaty_bodies if tb in filename]

@app.route('/search', methods=['GET'])
def search():
    raw_query = request.args.get('search_query', '').strip().lower()
    selected_labels = request.args.getlist('labels[]')
    selected_labels = [label.lower() for label in selected_labels]

    # Retrieve the selected treaty body from the form (query parameters)
    selected_treaty_bodies = request.args.getlist('treatyBodies[]')

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

@app.route('/corpus_viewer.html')

def corpus_viewer():
    committees = get_all_committees()  # Function to get all committees
    return render_template('corpus_viewer.html', committees=committees)

@app.route('/get_documents/<committee>')
def get_documents(committee):
    documents = get_documents_for_committee(committee)  # Function to get documents for a committee
    return jsonify(documents)

@app.route('/get_document/<document_id>')
def get_document(document_id):
    document_content = get_document_content(document_id)
    return jsonify(document_content)

@app.route('/about')
def about():
    return render_template('about.html')

with open("Neurorights.json", "r", encoding="utf-8") as file:
    neurorights_data = json.load(file)

# Load the Neurorights.json file
print(f"Neurorights data loaded: {len(neurorights_data)} items")
print(neurorights_data[0])  # Print the first item in the data

# Assuming this step happens when you load your data
for item in neurorights_data:
    item['Title_original'] = item['Title']
    item['Abstract_original'] = item['Abstract']

# Function to highlight search terms
def highlight_terms(text, terms):
    for term in terms:
        pattern = re.escape(term)
        text = re.sub(pattern, r'<span class="highlight">\g<0></span>', text, flags=re.IGNORECASE)
    return text

@app.route('/neurorights_search', methods=['GET'])
def neurorights_search():
    search_query = request.args.get('search_query', '').strip().lower()
    neurorights_filters = request.args.getlist('neurorights_filters')
    year_start = request.args.get('year_start', default=None, type=int)
    year_end = request.args.get('year_end', default=None, type=int)
    only_open_access = 'only_open_access' in request.args
    search_fields = request.args.getlist('search_fields') or ['default']
    page = request.args.get('page', default=1, type=int)
    # Get current page number
    per_page = 20  # Number of items per page

    ngrams = re.findall(r'"([^"]+)"', search_query)
    words = re.findall(r'\b\w+\b', search_query)
    query_terms = ngrams + [word for word in words if word not in ' '.join(ngrams)]

    authors_counter = Counter()
    keywords_counter = Counter()
    bigram_stopwords = {("springer", "nature"), ("rights", "reserved"), ("all", "rights")}
    bigrams_counter = Counter()
    filtered_results = []  # Store filtered items before pagination

    for item in neurorights_data:
        item_year = int(item.get('Year', 0))
        if year_start and year_end and not (year_start <= item_year <= year_end):
            continue
        if not matches_neurorights_filters(item, neurorights_filters):
            continue
        if not matches_search_query(item, query_terms, search_fields):
            continue
        if only_open_access and 'All Open Access' not in item.get('Open Access', ''):
            continue
        filtered_results.append(item)

    for item in filtered_results:
        authors_list = [author.strip() for author in item.get('Authors', '').split(';')]
        authors_counter.update(authors_list)
        keywords_list = item.get('Author Keywords', '').split(';')
        keywords_list = [keyword.strip() for keyword in keywords_list if len(keyword.strip()) >= 3]
        keywords_counter.update(keywords_list)

        # Combine text from title, abstract, and keywords
        combined_text = ' '.join([item.get('Title', ''), item.get('Abstract', ''), ' '.join(item.get('Author Keywords', '').split(';'))]).lower()
        # Tokenize and filter
        tokens = word_tokenize(combined_text)
        filtered_tokens = [token for token in tokens if token not in all_stopwords and len(token) > 1]
        # Generate and filter bigrams
        item_bigrams = list(nltk_ngrams(filtered_tokens, 2))
        filtered_bigrams = [bigram for bigram in item_bigrams if bigram not in bigram_stopwords]
        # Update counter with filtered bigrams
        bigrams_counter.update(filtered_bigrams)

    # Extract the 20 most common bigrams
    top_bigrams = bigrams_counter.most_common(20)
    # Format bigrams for display, including the count in brackets
    top_bigrams_str = [f"{' '.join(bigram)} ({count})" for bigram, count in top_bigrams]

    # Prepare analytics data for the top 20 authors and keywords
    top_authors = [(author, count) for author, count in authors_counter.most_common(20)]
    top_keywords = [(keyword, count) for keyword, count in keywords_counter.most_common(20)]

    # After filtering but before pagination
    total_filtered_results = len(filtered_results)

    # Pagination logic
    total_items = len(filtered_results)
    total_pages = (total_items + per_page - 1) // per_page  # Calculate total pages needed
    start = (page - 1) * per_page
    end = start + per_page
    paginated_items = filtered_results[start:end]  # Slice the filtered results for the current page

    search_results = []  # Will contain the items for the current page with highlighting
    for item in paginated_items:
        item_copy = item.copy()
        if 'Title_original' in item:
            item_copy['Title'] = highlight_terms(item['Title_original'], query_terms)
        if 'Abstract_original' in item:
            item_copy['Abstract'] = highlight_terms(item['Abstract_original'], query_terms)
        if 'Author Keywords' in item and query_terms:
            highlighted_keywords = []
            for keyword in item['Author Keywords'].split(';'):
                highlighted = highlight_terms(keyword.strip(), query_terms)
                highlighted_keywords.append(highlighted)
            item_copy['Author Keywords'] = '; '.join(highlighted_keywords)

        # Update authors and keywords counters
        authors_list = [author.strip() for author in item.get('Authors', '').split(';')]
        authors_counter.update(authors_list)
        keywords_list = item.get('Author Keywords', '').split(';')
        keywords_list = [keyword.strip() for keyword in keywords_list if len(keyword.strip()) >= 3]
        keywords_counter.update(keywords_list)
        search_results.append(item_copy)

    # Convert top authors and keywords to a string
    top_authors_str = '; '.join([f"{author} ({count})" for author, count in top_authors])
    top_keywords_str = '; '.join([f"{keyword} ({count})" for keyword, count in top_keywords])

    return render_template('neurorights_search.html', search_results=search_results, total_filtered_results=total_filtered_results,
                           search_query=search_query, top_bigrams=top_bigrams_str, top_authors=top_authors_str,
                           top_keywords=top_keywords_str, total_pages=total_pages, current_page=page)

def matches_neurorights_filters(item, neurorights_filters):
    if not neurorights_filters:
        return True  # No filter selected, so everything matches
    text_to_search = item.get('Title', '') + " " + item.get('Abstract', '') + " " + " ".join(item.get('Author Keywords', []))
    text_to_search = text_to_search.lower()
    return any(nf.lower() in text_to_search for nf in neurorights_filters)

def matches_search_query(item, query_terms, fields):
    if not query_terms:
        return True  # No query means match everything

    if not fields or fields == ['default']:
        fields = ['Title', 'Abstract', 'Keywords', 'Authors']  # If no fields are selected, search across all

    text_to_search = ""
    if 'Title' in fields:
        text_to_search += item.get('Title', '')
    if 'Abstract' in fields:
        text_to_search += " " + item.get('Abstract', '')
    if 'Keywords' in fields:
        text_to_search += " " + item.get('Author Keywords', '')
    if 'Authors' in fields:
        # Assuming 'Authors' is stored as a string of author names separated by semicolons.
        text_to_search += " " + item.get('Authors', '')

    text_to_search = text_to_search.lower()

    for term in query_terms:
        if term.startswith('"') and term.endswith('"'):  # Exact phrase match
            if term[1:-1].lower() not in text_to_search:
                return False
        else:  # Individual word match
            if term.lower() not in text_to_search:
                return False

    return True

#if __name__ == '__main__': # This is for running the app locally and allowing external users to visit your localhost
#    app.run(host='0.0.0.0', debug=True)

if __name__ == '__main__': # This is for running the app locally
    app.run(debug=True)