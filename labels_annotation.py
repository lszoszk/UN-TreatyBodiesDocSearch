import json
import os

"""
# Function to remove all existing labels from paragraphs
def remove_existing_labels(paragraphs):
    for paragraph in paragraphs:
        if isinstance(paragraph, dict) and 'Labels' in paragraph:
            paragraph['Labels'] = []  # Clear existing labels
"""

# Define the mapping of keywords to labels
keyword_to_label = {
    "Refugees & asylum-seekers": ["refugee", "refugees", "asylum"],
    "Indigenous peoples": ["indigenous", "tribal", "aboriginal"],
    "Migrants": ["migrant", "migrants", "migrant workers", "migrant worker", "migratory", "migration"],
    "Women/girls": ["woman", "women", "girl", "girls", "gender", "female"],
    "Children": ["child", "children", "girl", "girls", "boys", "boy"],
    "Adolescents": ["adolescent", "adolescents", "youth", "young people", "young person", "young persons"],
    "Persons with disabilities": ["disability", "disabilities", "disabled", "handicap", "handicapped", "impairment", "impairments", "impair", "impairs", "impairing", "impairments"],
    "Persons in street situations": ["street", "homeless", "homelessness", "vagrant", "vagrancy", "test"]
}

# Function to annotate paragraphs based on keywords
def annotate_paragraphs(paragraphs):
    annotated_paragraphs = []
    for paragraph in paragraphs:
        if not isinstance(paragraph, dict):
            print(f"Expected a dictionary, but got {type(paragraph)}: {paragraph}")
            continue
        labels = []
        paragraph = {k.strip(): v for k, v in paragraph.items()}
        text_key = 'Text' if 'Text' in paragraph else 'text'
        text_content = paragraph.pop(text_key, None)
        if text_content:
            for label, keywords in keyword_to_label.items():
                if any(keyword.lower() in text_content.lower() for keyword in keywords):
                    labels.append(label)
        annotated_paragraph = paragraph.copy()
        annotated_paragraph['Text'] = text_content
        annotated_paragraph['Labels'] = labels
        annotated_paragraphs.append(annotated_paragraph)
    return annotated_paragraphs

# Specify the directories containing JSON files and for saving annotated files
json_dir = "/Users/zuzannakowalska/Desktop/CERD_GR"
annotated_json_dir = "/Users/zuzannakowalska/Desktop/CERD_annotated"

# Create the directory for annotated files if it doesn't exist
if not os.path.exists(annotated_json_dir):
    os.makedirs(annotated_json_dir)

# Read and annotate each JSON file in the directory
json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]

for json_file in json_files:
    file_path = os.path.join(json_dir, json_file)
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        paragraphs = json.load(f)
    annotated_paragraphs = annotate_paragraphs(paragraphs)
    new_file_path = os.path.join(annotated_json_dir, f"Annotated_{json_file}")
    with open(new_file_path, 'w', encoding='utf-8') as f:
        json.dump(annotated_paragraphs, f, ensure_ascii=False, indent=4)
