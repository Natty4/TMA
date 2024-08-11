document.addEventListener("DOMContentLoaded", function () {
    const tg = window.Telegram.WebApp;
    tg.ready(); // Signal Telegram that your web app is ready

    function applyTheme() {
        const theme = tg.themeParams || {};
        document.documentElement.style.setProperty('--bg-color', theme.bg_color || '#ffffff');
        document.documentElement.style.setProperty('--text-color', theme.text_color || '#000000');
        document.documentElement.style.setProperty('--card-bg-color', theme.secondary_bg_color || '#f0f0f0');
        document.documentElement.style.setProperty('--card-hover-bg-color', theme.button_color || '#8eaffd');
        document.documentElement.style.setProperty('--box-shadow', '0 2px 5px ' + (theme.shadow_color || 'rgba(0, 0, 0, 0.1)'));
        document.documentElement.style.setProperty('--box-shadow-hover', '0 4px 10px ' + (theme.shadow_color || 'rgba(0, 0, 0, 0.2)'));
    }

    applyTheme();
});