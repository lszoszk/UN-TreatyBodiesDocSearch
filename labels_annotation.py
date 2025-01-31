import json
import os
from json import JSONDecodeError  # Import JSONDecodeError for exception handling

# Define the mapping of keywords to labels
keyword_to_label = {
    "Refugees & asylum-seekers": [" refugee ", " refugees ", " asylum ", " asylum-seeker ", " asylum-seekers "],
    "Indigenous peoples": [" indigenous ", " tribal ", " aboriginal "],
    "Migrants": [" migrant ", " migrants ", " migrant workers ", " migrant worker ", " migratory ", " migration "],
    "Women/girls": [" woman ", " women ", " girl ", " girls ", " gender ", " female "],
    "Children": [" child ", " children ", " girl ", " girls ", " boys ", " boy ", " juvenile ", " juveniles "],
    "Adolescents": [" adolescent ", " adolescents ", " youth ", " young people ", " young person ", " young persons "],
    "Persons with disabilities": [" disability ", " disabilities ", " disabled ", " handicap ", " handicapped ", " impairment ", " impairments "],
    "Persons in street situations": [" street ", " homeless ", " homelessness ", " vagrant ", " vagrancy "],
    "LGBTI+": [" lgbti ", " lgbtiq ", " lgbtq ", " lesbian ", " gay ", " bisexual ", " transgender ", " intersex ", " queer "],
    "Roma, Gypsies, Sinti and Travellers": [" roma ", " gypsy ", " gypsies ", " sinti ", " travellers ", " traveller "],
    "Persons living with HIV/AIDS": [" hiv ", " aids ", " living with hiv ",  "hiv-positive ", " aids patient ", " HIV infection "],
    "Persons living in rural/remote areas": [" rural ", " remote ", " countryside ", " villages ", " village "],
    "Persons living in poverty": [" poverty ", " poor ", " low-income ", " low income ", " underprivileged "],
    "Persons deprived of their liberty": [" prison ", " imprisoned ", " incarcerated ", " detained ", " detention ", " custody ", " jail ", " confinement "],
    "Persons affected by natural disasters": [" natural disaster ", " flood ", " earthquake ", " hurricane ", " tsunami ", " cyclone ", " tornado ", " wildfire "],
    "Non-citizens and stateless": [" non-citizen ", " noncitizen ", " stateless ", " foreigner ", " expatriate ", " expat "],
    "Persons affected by armed conflict": [" armed conflict ", " war ", " military conflict ", " combat ", " battle ", " post-conflict ", " conflict context ", " conflict situation "],
    "Internally displaced persons": [" internally displaced ", " displaced persons ", " displacement ", " displaced "],
    "Children in alternative care": [" alternative care ", " foster care ", " institutional care ", " child protection ", " child care ", " orphanage ", " orphanages ", " juvenile institutions "]
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
json_dir = # Add the path to the directory containing JSON files
annotated_json_dir = # Add the path to the directory for saving annotated JSON files

# Create the directory for annotated files if it doesn't exist
if not os.path.exists(annotated_json_dir):
    os.makedirs(annotated_json_dir)

# Read and annotate each JSON file in the directory
json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]

for json_file in json_files:
    file_path = os.path.join(json_dir, json_file)
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            paragraphs = json.load(f)
    except JSONDecodeError as e:
        print(f"Error decoding JSON file {json_file}: {e}")
        continue  # Skip to the next file if decoding fails

    annotated_paragraphs = annotate_paragraphs(paragraphs)
    new_file_path = os.path.join(annotated_json_dir, f"{json_file}")
    with open(new_file_path, 'w', encoding='utf-8') as f:
        json.dump(annotated_paragraphs, f, ensure_ascii=False, indent=4)