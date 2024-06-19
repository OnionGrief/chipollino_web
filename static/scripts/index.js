document.getElementById('chipollino-form').addEventListener('submit', (event) => {
    spinner.style.display = 'block';
});

window.addEventListener('unload', function (event) {
    spinner.style.display = 'none';
});

document.getElementById('gen_arg').onmouseover = function () {
    document.getElementById('args_list').style.display = 'block';
}
document.getElementById('gen_arg').onmouseout = function () {
    document.getElementById('args_list').style.display = 'none';
}
document.getElementById('args_list').onmouseover = function () {
    document.getElementById('args_list').style.display = 'block';
}
document.getElementById('args_list').onmouseout = function () {
    document.getElementById('args_list').style.display = 'none';
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

/*const testGenerator = document.getElementById('randomtest');
testGenerator.addEventListener('click', (event) => {
    fetch('/generator/' + 'Test')
        .then(response => response.text())
        .then(data => {
            document.getElementById('input-txt').value = data;
        });
});*/


var automaton_content = document.getElementById('automaton-content');
var automaton_image = document.getElementById('automaton-svg');
var editBtn = document.getElementById('edit');
var renderBtn = document.getElementById('render');
var resetBtn = document.getElementById('reset');
const cy_container = document.getElementById('cy-block');

function changeMode(mode) {
    if (mode == 'none') {
        automaton_image.hidden = true;
        cy_container.hidden = true;
        editBtn.hidden = true;
        renderBtn.hidden = true;
        resetBtn.hidden = true;
    } else if (mode == 'svg') {
        automaton_image.hidden = false;
        cy_container.hidden = true;
        if (format_list[formatSelector.value].editable)
            editBtn.hidden = false;
        else 
            editBtn.hidden = true;
        renderBtn.hidden = true;
        resetBtn.hidden = true;
    } else if (mode == 'cy') {
        automaton_image.hidden = true;
        cy_container.hidden = false;
        editBtn.hidden = true;
        renderBtn.hidden = false;
        resetBtn.hidden = false;
    }
}
changeMode('none');

format_list = [];
const formatSelector = document.getElementById('format-selector');
formatSelector.querySelectorAll('option').forEach(format => {
    format_list[format.value] = {
        name: format.value,
        editable: format.dataset.editable == 'True' ? true : false
    };
});

var curentGraphId = null;

formatSelector.addEventListener('change', (event) => {
    const selectedValue = event.target.value;
    if (curentGraphId != null) {
        fetch(`/get_graph/${curentGraphId}/${selectedValue}`)
            .then(response => {
                if (!response.ok) 
                    throw new Error('server error');
                return response.json();
            })
            .then(data => {
                automaton_content.value = data.text;
                if (data.editable)
                    automaton_content.disabled = false;
                else
                    automaton_content.disabled = true;
                automaton_image.innerHTML = data.svg;
                changeMode('svg');
            })
            .catch(error => {
                console.error(`Error getting format ${selectedValue} of graph ${curentGraphId} :`, error);
            });

        if (format_list[selectedValue].editable == "True")
            automaton_content.disabled = false;
        else
            automaton_content.disabled = true;
    }
});

const graph_list = document.querySelectorAll('.graph_name')
var prev_g_name = null;
graph_list.forEach(g_name => {
    g_name.addEventListener('click', (event) => {
        const g_id = event.target.dataset.value;
        fetch(`/get_graph/${g_id}/`)
            .then(response => {
                if (!response.ok)
                    throw new Error('server error');
                return response.json();
            })
            .then(data => {
                automaton_content.value = data.text;
                formatSelector.value = data.format;
                if (data.editable)
                    automaton_content.disabled = false;
                else
                    automaton_content.disabled = true;
                automaton_image.innerHTML = data.svg;
                curentGraphId = g_id;
                changeMode('svg');
            })
            .catch(error => {
                console.error(`Error getting graph ${g_id} :`, error);
            });

        if (prev_g_name)
            prev_g_name.style.backgroundColor = '#e6e6e6';
        prev_g_name = event.target;
        event.target.style.backgroundColor = '#c1c1c1'
    });
});

document.getElementById('delete_graph').addEventListener('click', (event) => {
    if (curentGraphId != null) {
        fetch(`/delete_graph/${curentGraphId}/`).then(response => {
                if (!response.ok)
                    console.error('Error deleting graph');
                return response.text();
            })
            .then(data => {
                showAlert(data);
                automaton_content.value = '';
                automaton_image.innerHTML = '';
                graph_list.forEach(g_name => {
                    if (g_name.dataset.value == curentGraphId)
                        g_name.remove();
                });
                changeMode('none');
            })
            .catch(error => console.error('Error deleting graph:', error));
    }
});

document.getElementById('save_graph').addEventListener('click', (event) => {
    if (curentGraphId != null) {
        fetch(`/save_graph/${curentGraphId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
                },
                body: JSON.stringify({
                    "format": formatSelector.value,
                    "content": automaton_content.value
                })
            })
            .then(response => {
                if (!response.ok)
                    console.error('Error saving graph');
                return response.text();
            })
            .then(data => {
                showAlert(data);
                // automaton_image.innerHTML = data.svg;
            })
            .catch(error => console.error('Error saving graph:', error));
    }
});

// перерисовка svg при изменении txt графа
automaton_content.addEventListener('blur', function (event) {
    if (curentGraphId != null) {
        fetch('/get_svg_graph/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
                },
                body: JSON.stringify({
                    "format": formatSelector.value,
                    "content": automaton_content.value
                })
            })
            .then(response => response.text())
            .then(data => {
                if (data != "None") {
                    automaton_image.innerHTML = data;
                    changeMode('svg');
                } else {
                    showAlert('invalid syntax');
                }
            })
            .catch(e => {
                console.error('Graph update error')
            });
    }
});

document.querySelector('.copy-button').addEventListener('click', (event) => {
    // Создаем временный элемент для копирования текста
    var tempInput = document.createElement('textarea');
    tempInput.value = automaton_content.value;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand('copy');
    document.body.removeChild(tempInput);
    showAlert('Text copied');
});
