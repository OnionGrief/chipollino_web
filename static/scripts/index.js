document.getElementById('chipollino-form').addEventListener('submit', (event) => {
    document.getElementById('loading-spinner').style.display = 'block';
});

window.addEventListener('unload', function (event) {
    document.getElementById('loading-spinner').style.display = 'none';
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

const testGenerator = document.getElementById('randomtest');
testGenerator.addEventListener('click', (event) => {
    fetch('/generator/' + 'Test')
        .then(response => response.text())
        .then(data => {
            document.getElementById('input-txt').value = data;
        });
});


var automaton_content = document.getElementById('automaton-content');
format_list = [];
const formatSelector = document.getElementById('format-selector');
formatSelector.querySelectorAll('option').forEach(format => {
    format_list[format.value] = {
        name: format.value,
        editable: format.dataset.editable
    };
});

var curentGraphId = null;

formatSelector.addEventListener('change', (event) => {
    const selectedValue = event.target.value;
    if (curentGraphId != null) {
    fetch(`/get_graph/${curentGraphId}/${selectedValue}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('server error');
                }
                return response.json();
            })
            .then(data => {
                automaton_content.textContent = data.text;
                if (data.editable)
                    automaton_content.disabled = false;
                else
                    automaton_content.disabled = true;
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
graph_list.forEach(g_name => {
    g_name.addEventListener('click', (event) => {
        const g_id = event.target.dataset.value;
        fetch('/get_graph/' + g_id)
            .then(response => {
                if (!response.ok) {
                    throw new Error('server error');
                }
                return response.json();
            })
            .then(data => {
                automaton_content.textContent = data.text;
                formatSelector.value = data.format;
                if (data.editable)
                    automaton_content.disabled = false;
                else
                    automaton_content.disabled = true;
                document.getElementById('automaton_image').innerHTML = data.svg;
                curentGraphId = g_id
            })
            .catch(error => {
                console.error(`Error getting graph ${g_id} :`, error);
            });
    });
});