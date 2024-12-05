import os
import json
from meilisearch import Client

# Initialize MeiliSearch client
meili_client = Client('http://127.0.0.1:7700')

# Ensure the index exists or create it
index_name = 'documents'
index = meili_client.index(index_name)
try:
    meili_client.create_index(uid=index_name)
except Exception as e:
    print(f"Index '{index_name}' already exists or cannot be created: {e}")

# Directory containing your JSON files
json_dir = "C:\\Users\\lszos\\PycharmProjects\\UN-Treaty-Body-Doc-Search\\json_meilisearch"

def generate_unique_id(file_name, doc_id):
    # Extract abbreviation from file name (e.g., CRC-GC11 from CRC-GC11.json)
    base_id = os.path.splitext(file_name)[0]
    # Combine with doc ID to create a unique identifier
    return f"{base_id}-{doc_id}"


def load_and_index_documents(json_dir, index):
    for json_file in os.listdir(json_dir):
        if json_file.endswith('.json'):
            file_path = os.path.join(json_dir, json_file)
            with open(file_path, 'r', encoding='utf-8') as file:
                documents = json.load(file)  # Load the JSON content

                # Modify each document to include a unique ID
                for doc in documents:
                    try:
                        # Convert ID to string and then try to strip it
                        doc_id = str(doc["ID"]).strip(".")  # Convert ID to string if it's not
                        unique_id = generate_unique_id(json_file, doc_id)
                        doc["meilisearch_id"] = unique_id  # Add unique ID to document
                    except KeyError:
                        print(f"Document in {json_file} is missing the 'ID' key. Skipping document.")
                        continue

                # Index the documents in MeiliSearch
                try:
                    # Note: The correct way to specify the primary key is at index creation or through the dashboard, not here.
                    index.add_documents(documents)  # Remove primaryKey argument
                    print(f"Successfully indexed documents from {json_file}")
                except Exception as e:
                    print(f"Error indexing documents from {json_file}: {e}")


# Call the function to load and index all documents
load_and_index_documents(json_dir, index)

# Get current searchable attributes
searchable_attributes = index.get_searchable_attributes()
print("Searchable attributes:", searchable_attributes)

update_status = meili_client.get_task('uid')
print(update_status)


# Search for a term in your documents
search_results = index.search('health')
print(search_results)
