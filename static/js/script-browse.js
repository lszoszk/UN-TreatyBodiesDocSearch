document.addEventListener('DOMContentLoaded', function() {
    var sidebarToggle = document.querySelector('.sidebar-toggle');
    var sidebar = document.querySelector('.sidebar');
    var documentViewer = document.querySelector('.document-viewer');

    // Toggle sidebar
    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('active');
    });

    // Load default documents (e.g., General Comments from the CRC)
    function loadDefaultDocuments() {
        loadDocuments('CRC'); // Replace 'CRC' with the actual default committee identifier
    }

    loadDefaultDocuments();

});

    function sortDocuments(documents) {
    return documents.sort((a, b) => {
        const aMatch = a.name.match(/General Comment No\. (\d+)/);
        const bMatch = b.name.match(/General Comment No\. (\d+)/);
        const aNumber = aMatch ? parseInt(aMatch[1]) : -1;
        const bNumber = bMatch ? parseInt(bMatch[1]) : -1;
        return bNumber - aNumber; // Sort in descending order of GC number
    });
}

function loadDocuments(committee, viewFirstDocument = false) {
    if (!committee) return; // Do nothing if no committee is selected
    fetch('/get_documents/' + encodeURIComponent(committee))
        .then(response => response.json())
        .then(documents => {
            const sortedDocuments = sortDocuments(documents);
            const docListDiv = document.querySelector('.document-list');
            docListDiv.innerHTML = ''; // Clear existing list

            sortedDocuments.forEach(doc => {
                const docLink = document.createElement('a');
                docLink.href = '#';
                docLink.textContent = doc.name; // Assuming each document has a 'name' property
                docLink.onclick = () => {
                    viewDocument(doc.id); // Assuming each document has an 'id' property
                    return false;
                };

                const listItem = document.createElement('li');
                listItem.appendChild(docLink);
                docListDiv.appendChild(listItem);
            });

            assignDocumentLinkEventListeners();

            // Automatically view the first document if requested
            if (viewFirstDocument && sortedDocuments.length > 0) {
                viewDocument(sortedDocuments[0].id);
            }
        })
        .catch(error => console.error('Error loading documents:', error));
   }

    function viewDocument(documentId) {
        fetch('/get_document/' + encodeURIComponent(documentId))
            .then(response => response.json())
            .then(data => {
                const viewerDiv = document.querySelector('.document-viewer');
                viewerDiv.innerHTML = ''; // Clear existing content

                // Append title, signature, and year of adoption
                const title = document.createElement('h2');
                title.textContent = data.title;
                viewerDiv.appendChild(title);

                const signature = document.createElement('p');
                signature.textContent = 'Signature: ' + data.signature;
                viewerDiv.appendChild(signature);

                const adoptionYear = document.createElement('p');
                adoptionYear.textContent = 'Year of Adoption: ' + data.adoption_year;
                viewerDiv.appendChild(adoptionYear);

                // Append paragraphs with numbers
                data.paragraphs.forEach((text, index) => {
                    const paragraph = document.createElement('p');
                    paragraph.innerHTML = text.replace(/^(\d+\.\s*)?/, `<strong>${index + 1}.</strong> `);
                    viewerDiv.appendChild(paragraph);
                });
            })
            .catch(error => console.error('Error loading document:', error));
    }

    // Function to escape special characters for regex
    function escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // Function for dynamic search within the document
    function documentSearch(query) {
        const viewerDiv = document.querySelector('.document-viewer');
        let content = viewerDiv.getAttribute('data-original') || viewerDiv.innerHTML;
        viewerDiv.setAttribute('data-original', content);

        if (query.length >= 3) {
            const regex = new RegExp(escapeRegex(query), 'gi');
            viewerDiv.innerHTML = content.replace(regex, match => `<span class="highlight">${match}</span>`);
            Array.from(viewerDiv.children).forEach(child => {
                if (!child.innerHTML.match(regex)) {
                    child.style.display = 'none';
                }
            });
        } else {
            viewerDiv.innerHTML = content;
            Array.from(viewerDiv.children).forEach(child => {
                child.style.display = '';
            });
        }
    }

    // Event listener for dynamic search input
    const searchInput = document.getElementById('documentSearchInput');
    searchInput.addEventListener('input', () => documentSearch(searchInput.value));

// Function to set dark mode preference
function setDarkModePreference(isDarkMode) {
    localStorage.setItem('darkMode', isDarkMode ? 'enabled' : 'disabled');
}

// Function to apply dark mode based on preference
function applyDarkModePreference() {
    const isDarkMode = localStorage.getItem('darkMode') === 'enabled';
    const darkModeToggle = document.getElementById("dark-mode-toggle");

    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        darkModeToggle.querySelector('i').classList.replace("fa-moon", "fa-sun");
        darkModeToggle.querySelector('i').classList.add("dark-mode-active");
    } else {
        document.body.classList.remove('dark-mode');
        darkModeToggle.querySelector('i').classList.replace("fa-sun", "fa-moon");
        darkModeToggle.querySelector('i').classList.remove("dark-mode-active");
    }
}

// Check if the user has a preference and apply it
applyDarkModePreference();

function toggleDarkMode() {
    const body = document.body;
    const darkModeToggle = document.getElementById("dark-mode-toggle");
    body.classList.toggle("dark-mode");

    if (body.classList.contains("dark-mode")) {
        darkModeToggle.querySelector('i').classList.replace("fa-moon", "fa-sun");
        darkModeToggle.querySelector('i').classList.add("dark-mode-active");
        setDarkModePreference(true);
    } else {
        darkModeToggle.querySelector('i').classList.replace("fa-sun", "fa-moon");
        darkModeToggle.querySelector('i').classList.remove("dark-mode-active");
        setDarkModePreference(false);
    }
}

// Event listener for the dark mode toggle click
const darkModeToggle = document.getElementById("dark-mode-toggle");
if (darkModeToggle) {
    darkModeToggle.addEventListener("click", toggleDarkMode);
}

document.addEventListener('DOMContentLoaded', function() {
    var sidebarToggle = document.querySelector('.sidebar-toggle');
    var sidebar = document.querySelector('.sidebar');

// Load default documents (e.g., General Comments from the CRC)
    function loadDefaultDocuments() {
        loadDocuments('CRC', true); // Replace 'CRC' with the actual default committee identifier
    }

    loadDefaultDocuments();
});

function assignDocumentLinkEventListeners() {
    var documentLinks = document.querySelectorAll('.document-list a');
    documentLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            // Remove active class from all document links
            documentLinks.forEach(function(otherLink) {
                otherLink.classList.remove('active');
            });

            // Add active class to the clicked link
            link.classList.add('active');

            // Close sidebar on small screens by toggling the 'active' class
            if (window.innerWidth <= 767) { // Check if the screen is small
                var sidebar = document.querySelector('.sidebar');
                sidebar.classList.remove('active');
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
        // Scroll to top button functionality
    const scrollToTopBtn = document.getElementById("scrollToTopBtn");
    if (scrollToTopBtn) {
        window.onscroll = function() {
            if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
                scrollToTopBtn.style.display = "block";
            } else {
                scrollToTopBtn.style.display = "none";
            }
        };

        scrollToTopBtn.addEventListener('click', function() {
            window.scrollTo({top: 0, behavior: 'smooth'});
        });
    }
});