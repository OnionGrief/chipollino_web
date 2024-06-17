var alertBox = document.getElementById('alert');
const spinner = document.getElementById('loading-spinner');

function showAlert(text) {
    alertBox.textContent = text
    alertBox.style.opacity = 0.8;

    setTimeout(() => {
        alertBox.style.opacity = 0;
    }, 1500);
}