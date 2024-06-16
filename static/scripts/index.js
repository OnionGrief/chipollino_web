document.getElementById('chipollino-form').addEventListener('submit', (event) => {
    document.getElementById('loading-spinner').style.display = 'block';
});

window.addEventListener('unload', function (event) {
    document.getElementById('loading-spinner').style.display = 'none';
});

document.getElementById('gen_arg').onmouseover = function() {
    document.getElementById('args_list').style.display = 'block';
}

const generatorSelector = document.querySelectorAll('.gen_object')
generatorSelector.forEach(gen_obj => {
    gen_obj.addEventListener('click', (event) => {
        document.getElementById('args_list').style.display = 'none';
        const selectedValue = event.target.id;
        fetch('/generator/' + selectedValue)
            .then(response => response.text())
            .then(data => {
                document.getElementById('generator_result').innerHTML = data;
            });
    });
});

const testGenerator = document.getElementById('randomtest');
testGenerator.addEventListener('click', (event) => {
    fetch('/generator/' + 'Test')
        .then(response => response.text())
        .then(data => {
            document.getElementById('input-txt').value = data;
        });
});