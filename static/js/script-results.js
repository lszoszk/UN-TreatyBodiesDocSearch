document.addEventListener("DOMContentLoaded", function() {
    // Cache DOM elements for efficiency
    const darkModeToggle = document.getElementById("toggle-icon");
    const body = document.body;
    const toggleAllButton = document.getElementById('toggle-all');

    // Toggle dark mode
    function toggleDarkMode() {
        body.classList.toggle("dark-mode");
        darkModeToggle.classList.toggle("fa-sun");
        darkModeToggle.classList.toggle("fa-moon");
        localStorage.setItem("darkMode", body.classList.contains("dark-mode") ? "enabled" : "disabled");
    }

    // Check and set dark mode on load
    if (localStorage.getItem("darkMode") === "enabled") {
        body.classList.add("dark-mode");
        darkModeToggle.classList.replace("fa-moon", "fa-sun");
    }

    darkModeToggle.addEventListener("click", toggleDarkMode);

    // Toggle all functionality for accordion
    let isExpanded = false;
    toggleAllButton.addEventListener('click', function() {
        document.querySelectorAll('#accordion .collapse').forEach(element => {
            // Check if the current state of the accordion matches the desired state
            let currentState = element.classList.contains('show');
            if(isExpanded && currentState || !isExpanded && !currentState) {
                new bootstrap.Collapse(element, { toggle: true });
            }
        });
        isExpanded = !isExpanded;
        toggleAllButton.textContent = isExpanded ? 'Collapse All' : 'Expand All';
    });

    // Copy to clipboard functionality
    function copyToClipboard(text, button) {
        navigator.clipboard.writeText(text).then(() => {
            // Success: Show tooltip
            const tooltip = button.querySelector('.copy-tooltip');
            tooltip.style.display = 'inline-block';
            setTimeout(() => {
                tooltip.style.display = 'none';
            }, 2000);
        }).catch(err => {
            // Error: Log to console
            console.error('Failed to copy: ', err);
        });
    }

    // Attach event listeners to copy buttons
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const content = this.getAttribute('data-copy-content');
            copyToClipboard(content, this);
        });
    });

    document.getElementById('exportToExcelBtn').addEventListener('click', function() {
        var searchKey = "{{ search_key }}"; // Replace with actual search key passed from Flask

        var form = document.createElement('form');
        form.method = 'POST';
        form.action = '/export_to_excel';
        form.style.display = 'none';

        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'search_key';
        input.value = searchKey;
        form.appendChild(input);

        document.body.appendChild(form);
        form.submit();
        document.body.removeChild(form);
    });
});