var pdfLoaded = false;

const blockSelector = document.getElementById('block-selector');
blockSelector.addEventListener('change', (event) => {
    const selectedValue = event.target.value;

    const blocks = document.querySelectorAll('.resultblock');
    for (const block of blocks) {
        if (block.id == selectedValue) {
            if (selectedValue == 'blockpdf' && !pdfLoaded) {
                spinner.style.display = 'block';
                fetch('/get_pdf/')
                    .then(response => response.blob())
                    .then(blob => {
                        const url = URL.createObjectURL(blob);
                        document.getElementById('pdf-viewer').src = url;
                        pdfLoaded = true;
                    })
                    .catch(error => {
                        showAlert('Failed to load PDF');
                    })
                    .finally(() => {
                        spinner.style.display = 'none';
                    });
            }
            block.style.display = 'block';
        } else {
            block.style.display = 'none';
        }
    }
});


var tex_content = document.getElementById("tex-content").textContent;
var downloadLink = document.getElementById("tex-download");
downloadLink.href = "data:application/tex;charset=utf-8," + encodeURIComponent(tex_content);

const header = {
    'Content-Type': 'application/json',
    'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
}

const automata = document.querySelectorAll('.object_view');
automata.forEach(element => {
    const blocks = element.querySelectorAll('.object_format');
    for (const block of blocks)
        if (block.dataset.value == 'HTML')
            block.textContent = element.querySelector('.object_figure').innerHTML

    format_selector = element.querySelector('.format-selector')
    format_selector.addEventListener('change', (event) => {
        const selectedValue = event.target.value;
        const blocks = element.querySelectorAll('.object_format');

        for (const block of blocks)
            if (block.dataset.value == selectedValue)
                block.style.display = 'block';
            else
                block.style.display = 'none';
    })

    element.querySelector('.get_tex_view').addEventListener('click', (event) => {
        // анимация загрузки
        spinner.style.display = 'block';

        tex_content = "";
        for (const block of element.querySelectorAll('.object_format'))
            if (block.dataset.value == 'LaTeX')
                tex_content = block.textContent;

        fetch('/tex_view/', make_post_body(header, {
                "tex_content": tex_content
            }))
            .then(response => {
                if (response.ok)
                    element.querySelector('.get_tex_view').disabled = true;
                return response.text()
            })
            .then(data => {
                element.querySelector('.object_figure').innerHTML = data;
            })
            .catch(error => console.error('Error getting SVG from TEX:', error))
            .finally(() => {
                spinner.style.display = 'none';
            });
    });


    save_graph_button = element.querySelector('.save_graph')
    if (save_graph_button)
        save_graph_button.addEventListener('click', (event) => {

            graph_name = prompt("Enter graph's name:", '');
            if (!graph_name)
                return;
            if (!isValidFilename(graph_name))
                return;

            dsl_content = "";
            for (const block of element.querySelectorAll('.object_format'))
                if (block.dataset.value == 'DSL')
                    dsl_content = block.textContent;

            fetch('/add_graph/', make_post_body(header, {
                    "name": graph_name,
                    "dsl_content": dsl_content
                }))
                .then(response => {
                    if (!response.ok)
                        console.error('Error saving graph');
                    return response.text();
                })
                .then(data => {
                    showAlert(data);
                })
                .catch(error => console.error('Error saving graph:', error));
        });

    element.querySelector('.copy-button').addEventListener('click', (event) => {
        // Создаем временный элемент для копирования текста
        var tempInput = document.createElement('textarea');
        for (const block of blocks)
            if (block.dataset.value == format_selector.value)
                tempInput.value = block.textContent;

        document.body.appendChild(tempInput);
        tempInput.select();
        document.execCommand('copy');
        document.body.removeChild(tempInput);
        showAlert('Text copied');
    });
});