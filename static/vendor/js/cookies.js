function setCookie(name, value, days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = "expires=" + date.toUTCString();
    document.cookie = name + "=" + value + ";" + expires + ";path=/";
}

function areCookiesAccepted() {
    return document.cookie.indexOf("cookiesAccepted=true") !== -1;
}

function showCookieBanner() {
    const banner = document.getElementById("cookieBanner");
    banner.style.display = "block";
}

function hideCookieBanner() {
    const banner = document.getElementById("cookieBanner");
    banner.style.display = "none";
}

if (!areCookiesAccepted()) {
    showCookieBanner();
}

function acceptCookies() {
    setCookie("cookiesAccepted", "true", 365); // 1 year
    hideCookieBanner();
    showNotification("Thank you for accepting cookies!", true);
}