const App = (() => {

    // ── Chargement d'un partial HTML dans un élément ──────────────────
    async function loadPartial(selector, url) {
        const el = document.querySelector(selector);
        if (!el) return;
        const html = await fetch(url).then(r => r.text());
        el.innerHTML = html;
    }

    // ── Gestion du cookie passphrase ──────────────────────────────────
    function getPassphrase() {
        // return document.cookie.split('; ')
        //     .find(r => r.startsWith('housify_pass='))
        //     ?.split('=')[1] ?? null;
        return localStorage.getItem('housify_pass');
    }

    function setPassphrase(value) {
        // expires dans 7 jours
        const exp = new Date(Date.now() + 7 * 864e5).toUTCString();
        document.cookie = `housify_pass=${value}; expires=${exp}; path=/; SameSite=Strict`;
        localStorage.setItem('housify_pass', value);
    }

    function clearPassphrase() {
        localStorage.removeItem('housify_pass');
        document.cookie = 'housify_pass=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
    }

    // ── Vérification du passphrase via /api/check_passphrase/ ─────────
    async function checkPassphrase(passphrase) {
        const res = await fetch('/api/check_passphrase/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ passphrase })
        });
        const data = await res.json();
        return data.status === 'success';
    }

    // ── Affichage / masquage de l'overlay login ───────────────────────
    function showLoginOverlay() {
        const overlay = document.getElementById('login-overlay');
        if (overlay) overlay.style.display = 'flex';

        document.getElementById('login-form').addEventListener('submit',  (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();

            fetch('/api/login/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success'){
                    setPassphrase(data.passphrase);
                    hideLoginOverlay();
                    return true;
                }
                else{
                    localStorage.removeItem('housify_pass');
                    return false;
                }
            });

        });
    }

    function hideLoginOverlay() {
        const overlay = document.getElementById('login-overlay');
        if (overlay) overlay.style.display = 'none';
    }

    // ── Init : appelé sur chaque page ─────────────────────────────────
    async function init() {
        // 1. Injecter nav et overlay login
        await loadPartial('#nav-placeholder', '/partials/nav.html');
        await loadPartial('#login-placeholder', '/partials/login.html');

        // 2. Marquer le lien actif dans la nav
        document.querySelectorAll('.top-menu a').forEach(link => {
            if (link.href === location.href) link.classList.add('active');
        });

        // 3. Vérifier l'auth
        const passphrase = getPassphrase();
        if (!passphrase || !(await checkPassphrase(passphrase))) {
            localStorage.removeItem('housify_pass');
            showLoginOverlay();
        }
        else {
            hideLoginOverlay();
        }

        // 4. Stocker le passphrase accessible aux autres scripts
        window.__passphrase = getPassphrase();
    }

    return { init, getPassphrase, clearPassphrase, loadPartial };
})();

document.addEventListener('DOMContentLoaded', () => App.init());