const graph_settings = [{
        selector: 'node',
        style: {
            'background-color': '#ffffff',
            'border-width': 1,
            'label': 'data(label)',
            'text-valign': 'center',
            'font-size': '10px',
            'shape': 'ellipse'
        }
    },
    {
        selector: 'node.dummy',
        style: {
            'border-width': 0,
        }
    },
    {
        selector: 'node.doublecircle',
        style: {
            'border-width': 3,
            'border-style': 'double',
        }
    },
    {
        selector: 'edge',
        style: {
            'width': 1,
            'line-color': '#000',
            'target-arrow-color': '#000',
            'target-arrow-shape': 'vee',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '10px',
            'text-rotation': 'autorotate',
            'text-margin-y': -10,
            'color': '#000',
            'loop-direction': '0deg',
            'loop-sweep': '25deg',
            'z-index': 2
        }
    }
];

const layout_settings = {
    name: 'breadthfirst',
    directed: true,
    spacingFactor: 1,
    transform: function (node, position) {
        return {
            x: position.y,
            y: position.x
        }; // Swap x and y to make it horizontal
    }
}


const cy_elem = document.getElementById('cy');
var cy;
var dummyId = 'dummy';
var startId = null;
var sourceNode = null;
var targetNode = null;
var selectedElement = null;

function set_size(node) {
    const labelLength = node.data('label').length;
    const width = Math.max(20, Math.min(50, labelLength * 7));
    node.style('width', width);
    node.style('height', width);
}

function lockGraph() {
    cy.nodes().forEach(function (node) {
        node.lock();
    });
}

function unlockGraph() {
    cy.nodes().forEach(function (node) {
        node.unlock();
    });
}

document.addEventListener('keydown', function (event) {
    if (event.key === 'Delete' && selectedElement && selectedElement.id() != startId) {
        lockGraph()
        if (selectedElement == sourceNode)
            sourceNode = null;
        if (selectedElement == targetNode)
            targetNode = null;
        cy.remove(selectedElement);
        selectedElement = null;
        cy.layout(layout_settings).run();
        unlockGraph()
    }
});



function addNode() {
    nodeId = prompt('Enter node id:');
    if (!nodeId)
        return;
    lockGraph();
    let start_pos = cy.getElementById(startId).position();
    a = cy.add({
        group: 'nodes',
        data: {
            id: nodeId,
            label: nodeId
        },
        position: {
            x: start_pos.x,
            y: start_pos.y - 100
        },
        locked: true,
    });
    set_size(a);
    cy.layout(layout_settings).run();
    unlockGraph();
}

function addEdge() {
    if (sourceNode != null && targetNode != null) {
        label = prompt('Enter edge label');
        if (label == null || label == "")
            return;
        lockGraph();
        cy.add({
            group: 'edges',
            data: {
                source: sourceNode.id(),
                target: targetNode.id(),
                label: label
            },

        });
        sourceNode.style('border-color', 'black');
        targetNode.style('border-color', 'black');
        cy.layout(layout_settings).run();
        unlockGraph();
    }
}

function changeFinality() {
    if (selectedElement != null && selectedElement.isNode())
        if (selectedElement.classes().includes('doublecircle'))
            selectedElement.removeClass('doublecircle');
        else
            selectedElement.addClass('doublecircle');
}


function get_cy_view(json_data) {
    const graphData = JSON.parse(json_data);
    cy = cytoscape({
        container: cy_elem,
        elements: graphData,
        style: graph_settings
    });

    startId = null;
    sourceNode = null;
    targetNode = null;
    selectedElement = null;

    cy.nodes().forEach(function (node) {
        set_size(node);
    });
    cy.edges().forEach(function (edge) {
        if (edge.source().id() == dummyId)
            startId = edge.target().id();
    });
    cy.layout(layout_settings).run();

    // Обработчик выбора узлов
    cy.on('tap', 'node', function (event) {
        var node = event.target;
        if (node.id() == dummyId)
            return;
        if (sourceNode === null && targetNode === null) {
            sourceNode = node;
            sourceNode.style('border-color', 'green');
        } else if (targetNode === null && sourceNode != null) {
            targetNode = node;
            targetNode.style('border-color', 'red');
        } else if (sourceNode != null && targetNode != null) {
            sourceNode.style('border-color', 'black');
            targetNode.style('border-color', 'black');
            targetNode = null;
            sourceNode = node;
            sourceNode.style('border-color', 'green');
        }
        selectedElement = node;
    });

    cy.on('tap', 'edge', function (event) {
        if (event.target.source().id() == dummyId)
            return;
        selectedElement = event.target;
    });
}

function getGraphJSON() {
    var nodes = cy.nodes().map(function (node) {
        node_info = {
            data: {
                id: node.data('id'),
                label: node.data('label')
            }
        };
        if (node.classes().length > 0)
            node_info['classes'] = node.classes()[0]
        return node_info;
    });

    var edges = cy.edges().map(function (edge) {
        return {
            data: {
                source: edge.data('source'),
                target: edge.data('target'),
                label: edge.data('label')
            }
        };
    });

    return JSON.stringify({
        nodes: nodes,
        edges: edges
    }, null, 2);
}

editBtn.addEventListener('click', (event) => {
    json_content = "";
    try {
        if (curentGraphId != null) {
            fetch(`/get_graph/${curentGraphId}/JSON`)
                .then(response => {
                    if (!response.ok)
                        throw new Error('server error');
                    return response.json();
                })
                .then(data => {
                    changeMode('cy');
                    json_content = data.text;
                    get_cy_view(json_content);
                })
                .catch(error => {
                    console.error(`Error getting format JSON of graph ${curentGraphId} :`, error);
                });
        }
    } catch (error) {
        changeMode('svg');
        showAlert("Can't create graph")
    }
});

renderBtn.addEventListener('click', (event) => {
    json_content = "";
    try {
        if (curentGraphId != null) {
            fetch(`/convert_graph_format/${formatSelector.value}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
                    },
                    body: JSON.stringify({
                        "format": 'JSON',
                        "content": getGraphJSON()
                    })
                })
                .then(response => {
                    if (!response.ok)
                        throw new Error('server error');
                    return response.json();
                })
                .then(data => {
                    changeMode('svg');
                    automaton_content.value = data.text;
                    automaton_image.innerHTML = data.svg;
                })
                .catch(error => {
                    console.error(`Error getting format JSON of graph ${curentGraphId} :`, error);
                });
        }
    } catch (error) {
        changeMode('cy');
        showAlert("Can't render graph")
    }
});