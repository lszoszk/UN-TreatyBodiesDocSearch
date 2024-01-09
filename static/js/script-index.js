// Function to toggle dark mode
function toggleDarkMode() {
    const body = document.body;
    const darkModeToggle = document.getElementById("toggle-icon");
    body.classList.toggle("dark-mode");
    if (body.classList.contains("dark-mode")) {
        darkModeToggle.classList.replace("fa-moon", "fa-sun");
        localStorage.setItem("darkMode", "enabled");
    } else {
        darkModeToggle.classList.replace("fa-sun", "fa-moon");
        localStorage.removeItem("darkMode");
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const darkModeToggle = document.getElementById("toggle-icon");

    // Initial check for saved dark mode setting
    if (localStorage.getItem("darkMode") === "enabled") {
        document.body.classList.add("dark-mode");
        darkModeToggle.classList.replace("fa-moon", "fa-sun");
    }

    // Event listener for the icon click
    darkModeToggle.addEventListener("click", toggleDarkMode);

    // Function to handle form submission
    document.querySelector("form").addEventListener("submit", function(event) {
        var searchQuery = document.querySelector("input[name='search_query']").value;
        gtag('event', 'search', {
            'event_category': 'Site Search',
            'event_label': searchQuery
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    var selectElement = document.querySelector('select');

    selectElement.addEventListener('change', function () {
        // Remove any previously added 'selected' class
        this.querySelectorAll('option').forEach(option => option.classList.remove('selected'));

        // Add 'selected' class to the currently selected option
        this.querySelector('option:checked').classList.add('selected');
    });
});

        // Function to hide the cookie consent banner
        function hideCookieBanner() {
            document.getElementById("cookieConsentBanner").style.display = "none";
            localStorage.setItem("cookieConsent", "true");
        }

        // Check if cookie consent has already been given
        document.addEventListener("DOMContentLoaded", function () {
            if (localStorage.getItem("cookieConsent")) {
                document.getElementById("cookieConsentBanner").style.display = "none";
            }
        });