    // Toggle all functionality for accordion
    let isExpanded = false;
    toggleAllButton.addEventListener('click', function () {
        document.querySelectorAll('#accordion .collapse').forEach(element => {
            let currentState = element.classList.contains('show');
            if (isExpanded && currentState || !isExpanded && !currentState) {
                new bootstrap.Collapse(element, { toggle: true });
            }
        });
        isExpanded = !isExpanded;
        toggleAllButton.textContent = isExpanded ? 'Collapse All' : 'Expand All';
    });

    // Copy to clipboard functionality
    function copyToClipboard(text, button) {
        navigator.clipboard.writeText(text).then(() => {
            const tooltip = button.querySelector('.copy-tooltip');
            tooltip.style.display = 'inline-block';
            setTimeout(() => {
                tooltip.style.display = 'none';
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
        });
    }

    // Attach event listeners to copy buttons
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const content = this.getAttribute('data-copy-content');
            copyToClipboard(content, this);
        });
    });

    // Export to Excel button functionality
    document.getElementById('exportToExcelBtn').addEventListener('click', function () {
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
