# UN Treaty Bodies Search and Analysis App

<a href="https://zenodo.org/doi/10.5281/zenodo.10495719"><img src="https://zenodo.org/badge/741047917.svg" alt="DOI"></a>

This Flask application, also available at <a href="https://lszoszk.pythonanywhere.com/">lszoszk.pythonanywhere.com</a>, is designed to perform in-depth analysis and search through a collection of the General Comments/Recommendations adopted by the UN Treaty Bodies. It offers functionalities such as keyword searching, concerned groups filtering, analysis of collocations and export search results to Excel.  🇺🇳 🔍📊📄

## Description

The app processes JSON data, enabling users to search through the General Comments/Recommendations (paragraph-level search) based on keywords, concerned groups/persons labels, and Treaty Bodies. It features an advanced text analysis pipeline using NLTK for tokenization, term frequencies, bigram extraction, and custom stopwords processing. The application also provide a search-within-search functionality, which allows for a more advanced filtering of search results.

## Getting Started

### Dependencies

- Python 3.6+
- Flask
- Pandas
- NLTK
- BeautifulSoup
- `GC-info.json` file for the app's document metadata

### Installation

1. Clone the repository:
   ```
   git clone [URL of this repository]
   ```
2. Navigate to the project directory:
   ```
   cd [project_name]
   ```

### Executing Program

1. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
2. Run the Flask application:
   ```
   python app.py
   ```
3. Access the application through a web browser at `localhost:5000`.

## Features

- **Advanced Search** 🔍: A robust search functionality that allows users to filter relevant paragraphs from the documents based on keyword, concerned groups/persons (e.g., children, women, indigenous peoples), and by the UN Treaty Bodies (e.g., Committee on the Rights of the Child, Committee on Economic, Social and Cultural Rights).
- **Text Analysis** 📊: Text processing capabilities, leveraging the NLTK for word frequencies, bigram analysis, custom UN-related stopwords list, and search within search results functionality.
- **Custom Labels and Stopwords** 🏷️: Ability to define and use custom labels (e.g., concerned groups, human rights issues) and custom stopwords for text analysis.
- **Interactive Results** 💡: Highlights search terms and displays results interactively.
- **Data Export** 📁: Export search results to Excel format for further analysis.

## Screenshots
![search.png](img%2Fsearch.png)
<em>Main page with search functionality.</em>


![search_results.png](img%2Fsearch_results.png)
<em>Search results. You can visit the source document (OHCHR website) and copy it to a clipboard with automatically generated references.</em>


![analytical_dashboard.png](img%2Fanalytical_dashboard.png)
<em>Analytical dashboard. Insert a query in "Narrow your search" to run an additional, dynamic search within your search results.</em>


![dark_mode.png](img%2Fdark_mode.png)
<em>Dark mode of the application.</em>

## Help

If you encounter any issues, please check if all dependencies are correctly installed and the `GC-info.json` file is properly formatted and located in the root directory of the project.

## Author

[Łukasz Szoszkiewicz](https://lszoszk.github.io/)

E-mail: [l.szoszkiewicz@amu.edu.pl](mailto:l.szoszkiewicz@amu.edu.pl)

## Version History

* 0.1
    * Initial Release (8 January 2024) - includes General Comments adopted by the Committee on the Rights of the Child and the Committee on Economic, Social and Cultural Rights.

## License

This project is licensed under the <a href="https://choosealicense.com/licenses/mit/">MIT License</a> - see the LICENSE.md file for details

## Acknowledgments

* [Flask](https://flask.palletsprojects.com/)
* [Natural Language Toolkit (NLTK)](https://www.nltk.org/)
* [Pandas](https://pandas.pydata.org/)