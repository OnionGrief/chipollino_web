function showAlert() {
    const alertBox = document.getElementById('alert');
    alertBox.style.opacity = 0.8;

    setTimeout(() => {
        alertBox.style.opacity = 0;
    }, 1500);
}

spinner = document.getElementById('loading-spinner');