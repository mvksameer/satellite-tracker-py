document.documentElement.classList.add('js');

// Sticky nav gains a stronger material once the page has scrolled past the top.
const nav = document.getElementById('site-nav');
let navTicking = false;
window.addEventListener('scroll', () => {
    if (navTicking) return;
    navTicking = true;
    requestAnimationFrame(() => {
        nav.classList.toggle('scrolled', window.scrollY > 40);
        navTicking = false;
    });
}, { passive: true });

// Reveal each page's content as it enters view.
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('in-view');
            revealObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.15 });

document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

// Lightbox: present on every page via base.html, wired up unconditionally.
const lightbox = document.getElementById('lightbox');
const lightboxImg = document.getElementById('lightbox-img');

document.getElementById('lightbox-close').addEventListener('click', () => lightbox.close());

lightbox.addEventListener('click', function (e) {
    if (e.target === lightbox) lightbox.close();
});

// Everything below is specific to the tracker page, guarded since the
// tracker form only exists there.
const trackerForm = document.getElementById('tracker-form');
if (trackerForm) {
    const satelliteCharacteristics = {
        'ISS (ZARYA)': {
            type: 'Space Station',
            description: 'International Space Station, 51.6° inclination, roughly 400 km altitude'
        },
        'CSS (TIANHE)': {
            type: 'Space Station',
            description: 'Chinese Space Station (Tianhe core module), 41.5° inclination, roughly 400 km altitude'
        },
        'NOAA 15': {
            type: 'Weather Satellite',
            description: 'Polar weather satellite, 98.7° inclination, roughly 850 km altitude'
        },
        'NOAA 18': {
            type: 'Weather Satellite',
            description: 'Polar weather satellite, 99.2° inclination, roughly 860 km altitude'
        },
        'NOAA 19': {
            type: 'Weather Satellite',
            description: 'Polar weather satellite, 99.1° inclination, roughly 875 km altitude'
        }
    };

    const plotDescriptions = {
        'altitude': 'Shows satellite elevation above the horizon over time',
        'azimuth': 'Shows satellite compass direction, coloured by elevation',
        'distance': 'Shows distance from observer and orbital velocity',
        'polar': 'Shows satellite paths across the sky as a polar projection',
        'ground_track': 'Shows the satellite ground track on a world map'
    };

    document.getElementById('plot_type').addEventListener('change', function () {
        document.getElementById('plot-description').textContent =
            plotDescriptions[this.value] || '';
    });

    document.getElementById('satellite').addEventListener('change', function () {
        const infoDiv = document.getElementById('satellite-info');
        if (this.value && satelliteCharacteristics[this.value]) {
            const info = satelliteCharacteristics[this.value];
            infoDiv.innerHTML = `
                <strong>${this.value}</strong><br>
                Type: ${info.type}<br>
                ${info.description}
            `;
            infoDiv.style.display = 'block';
        } else {
            infoDiv.style.display = 'none';
        }
    });

    fetch('/satellites')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('satellite');
            select.innerHTML = '';

            const featured = ['ISS (ZARYA)', 'CSS (TIANHE)', 'NOAA 15', 'NOAA 18', 'NOAA 19'];
            featured.forEach(name => {
                if (data.includes(name)) {
                    const option = document.createElement('option');
                    option.value = name;
                    option.textContent = name;
                    select.appendChild(option);
                }
            });

            const separator = document.createElement('option');
            separator.disabled = true;
            separator.textContent = '--- All Satellites ---';
            select.appendChild(separator);

            data.forEach(name => {
                if (!featured.includes(name)) {
                    const option = document.createElement('option');
                    option.value = name;
                    option.textContent = name;
                    select.appendChild(option);
                }
            });
        })
        .catch(error => {
            console.error('Error loading satellites:', error);
            document.getElementById('satellite').innerHTML =
                '<option value="">Error loading satellites</option>';
        });

    trackerForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(this);
        const params = new URLSearchParams();
        for (let [key, value] of formData) {
            params.append(key, value);
        }

        document.getElementById('loading').style.display = 'block';
        document.getElementById('plot-container').innerHTML = '';
        document.getElementById('error-container').innerHTML = '';

        fetch('/plot?' + params.toString())
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';

                if (data.error) {
                    document.getElementById('error-container').innerHTML =
                        `<div class="error">${data.error}</div>`;
                } else {
                    document.getElementById('plot-container').innerHTML =
                        `<img src="data:image/png;base64,${data.plot}" alt="Satellite Plot">`;
                }
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('error-container').innerHTML =
                    `<div class="error">Error: ${error.message}</div>`;
            });
    });

    document.getElementById('plot-container').addEventListener('click', function (e) {
        if (e.target.tagName === 'IMG') {
            lightboxImg.src = e.target.src;
            lightbox.showModal();
        }
    });
}
