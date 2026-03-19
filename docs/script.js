// Tab switching logic for the Loop examples
function showTab(event, tabId) {
    // Remove active class from all buttons in the same container
    const tabBtns = event.target.parentElement.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => btn.classList.remove('active'));

    // Remove active class from all content sections
    const tabContents = event.target.parentElement.nextElementSibling.parentElement.querySelectorAll('.tab-content');
    tabContents.forEach(content => content.classList.remove('active'));

    // Add active class to clicked button and target content
    event.target.classList.add('active');
    document.getElementById(tabId).classList.add('active');
}

// Active link highlighting on scroll
const sections = document.querySelectorAll('section');
const navItems = document.querySelectorAll('.nav-item');

window.addEventListener('scroll', () => {
    let current = '';

    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (pageYOffset >= (sectionTop - 100)) {
            current = section.getAttribute('id');
        }
    });

    navItems.forEach(item => {
        item.classList.remove('active');
        const link = item.querySelector('a');
        if (link.getAttribute('href') === `#${current}`) {
            item.classList.add('active');
        }
    });
});

// Smooth scroll for anchor links
document.querySelectorAll('.sidebar-nav a').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();

        const targetId = this.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);

        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 20,
                behavior: 'smooth'
            });
        }
    });
});

// Search functionality (simple filtering)
const searchInput = document.getElementById('search-input');
const navLinks = document.querySelectorAll('.nav-item a');

searchInput.addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase();

    navLinks.forEach(link => {
        const text = link.textContent.toLowerCase();
        const parent = link.parentElement;

        if (text.includes(term)) {
            parent.style.display = 'block';
        } else {
            parent.style.display = 'none';
        }
    });
});

// Add intersection observer for reveal animations
const observerOptions = {
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('reveal');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('.section').forEach(section => {
    observer.observe(section);
});
