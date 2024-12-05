from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
import PyPDF2
import json

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

def text_to_json(text):
    structured_data = {
        'header': ['I. Introduction', 'IV. Root causes of trafficking in women and girls'],
        'section': ['A. Socioeconomic injustice', 'B. Discrimination in migration and asylum regimes'],
        'paragraphs': ['1. Article 6 of the Convention on the Elimination of All Forms of Discrimination against Women sets out the legal obligation of States parties to take all appropriate measures, including legislation, to suppress all forms of trafficking in women and exploitation of prostitution of women. Despite the plethora of existing legal and policy frameworks to combat trafficking at the national, regional and international levels, women and girls continue to comprise the majority of detected victims of trafficking across the world, and perpetrators enjoy widespread impunity', '2. In the view of the Committee, the situation persists due to a lack of appreciation of the gender dimensions of trafficking overall and, in particular, of the trafficking of women and girls who are exposed to various types of exploitation, including sexual exploitation. A gender analysis of the crime reveals that its root causes lie in sexbased discrimination, including the failure to address the prevailing economic and patriarchal structures and the adverse and gender-differentiated impact of the labour, migration and asylum regimes of States parties that create the situations of vulnerability leading to women and girls being trafficked'],
        'footnotes': ['2 Susan J. Hassol and others, “(Un)Natural disasters: communicating linkages between extreme events and climate change”, WMO Bulletin, vol. 65, No. 2 (Geneva, World Meteorological Organization, 2016).', '3 United Nations Development Programme (UNDP), “Climate change and disaster risk reduction”, 23 March 2016.', '4 See Commission on the Status of Women, resolutions 56/2 and 58/2 on gender equality and the empowerment of women in natural disasters, adopted by consensus in March 2012 and March 2014.', '5 See, for example, general recommendation No. 27 (2010) on older women and the protection of their human rights.']
    }
    lines = text.split('\n')
    for line in lines:
        # Example heuristic: if a line is uppercase, consider it a header
        if line.isupper():
            structured_data['header'].append(line)

        # Example heuristic: if a line starts with a number, consider it a footnote
        elif line.strip().startswith("1.") or line.strip().startswith("2."):
            structured_data['footnotes'].append(line)

        # Otherwise, consider it a paragraph
        else:
            structured_data['paragraphs'].append(line)

    return json.dumps(structured_data, indent=4)

# Example usage
pdf_path = 'C:\\Users\\lszos\\Desktop\\UAM\\GC DATABASE\\CEDAW\\CEDAW-GR37-Climate.pdf'
pdf_text = extract_text_from_pdf(pdf_path)
pdf_json = text_to_json(pdf_text)  # Ensure this matches the name of your function
print(pdf_json)
