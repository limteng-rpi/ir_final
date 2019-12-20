mapboxgl.accessToken = 'pk.eyJ1IjoibGltdGVuZyIsImEiOiJjajJjcGdzNjUwM2NkMndvNzBpeTBrZjFwIn0.9YDJZ3qB_VuNHF3L-ni6PQ';
var trending_entity_list = [];

$(document).ready(function () {
    update_top_entities();
    update_trending_entities();
    setTimeout(function () {
        get_related();
    }, 1000);
    setTimeout(function () {
        update_locals();
    }, 2000);
});

function nummber_with_comma(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

var map = new mapboxgl.Map({
    minZoom: 2,
    maxZoom: 15,
    container: 'map-wrapper',
    style: 'mapbox://styles/mapbox/dark-v9'
});

setTimeout(function () {
    map.addLayer({
        'id': '3d-buildings',
        'source': 'composite',
        'source-layer': 'building',
        'filter': ['==', 'extrude', 'true'],
        'type': 'fill-extrusion',
        'minzoom': 5,
        'paint': {
            'fill-extrusion-color': '#aaa',
            'fill-extrusion-height': {
                'type': 'identity',
                'property': 'height'
            },
            'fill-extrusion-base': {
                'type': 'identity',
                'property': 'min_height'
            },
            'fill-extrusion-opacity': .6
        }
    });
}, 2000);

var options = {
    responsive: true,
    maintainAspectRatio: false,
    elements: {
        line: {
            tension: 0.5
        }
    },
    plugins: {
        filler: {
            propagate: true
        }
    },
    scales: {
        xAxes: [{ticks: {display: true, fontSize: 10}}],
        yAxes: [{
            ticks: {
                display: true,
                beginAtZero: true,
                fontSize: 8,
                autoSkip: true,
                maxTicksLimit: 8
            }
        }
        ]
    },
    legend: {
        display: false
    }
};


function update_top_entities() {
    $.getJSON('/get_top_entities',
        function (response) {
            console.log(response);

            var top_entity_list_ul = $('ul#top-entity-list');
            $.each(response.mentions, function (i, mention) {
                var li_div = $('<li></li>').addClass('top-entity');
                var text_div = $('<div></div>').addClass('top-entity-name').text(
                    mention[0]);
                li_div.append(text_div);

                var entity_info_div = $('<div></div>').addClass('top-entity-info');
                var count = nummber_with_comma(mention[1]);
                var count_div = $('<span></span>').addClass('tag').text(
                    'Count: ' + count);
                entity_info_div.append(count_div);
                var type_list = mention[2];
                $.each(type_list, function (j, t) {
                    var type_span = $('<span></span>').addClass('tag').text(t);
                    entity_info_div.append(type_span);
                });
                li_div.append(entity_info_div);
                top_entity_list_ul.append(li_div);
            });
        }
    )
}

function update_trending_entities() {
    $.getJSON('/get_trending_entities',
        function (response) {
            // console.log(response);

            var trend_entity_list_ul = $('ul#trending-entity-list');
            $.each(response.mentions, function (i, mention) {
                var li_div = $('<li></li>').addClass('trending-entity');

                var name_div = $('<div></div>').addClass('trending-entity-name').text(mention[0]);
                li_div.append(name_div);
                trending_entity_list.push(mention[0]);

                var info_div = $('<div></div>').addClass('trending-entity-info')
                    .attr('entity', mention[0]);
                info_div.append($('<span></span>').addClass('tag').text(
                    'Count: ' + nummber_with_comma(mention[2])));
                li_div.append(info_div);

                var timeline_div = $('<div></div>').addClass('trending-entity-timeline');
                timeline_div.append($('<canvas></canvas>').addClass('timeline')
                    .attr('id', 'timeline-' + i));
                li_div.append(timeline_div);

                trend_entity_list_ul.append(li_div);

                new Chart('timeline-' + i, {
                    type: 'line',
                    data: {
                        labels: response.dates, //Array.from({length: 14}, (v, k) => k),
                        datasets: [{
                            pointRadius: 0,
                            borderWidth: 1,
                            borderColor: '#dd2434',
                            backgroundColor: 'rgba(143,74,86,0.3)',
                            data: mention[3],
                            label: 'Dataset',
                            fill: 'start'
                        }]
                    },
                    options: options
                });
            });
        });
}

function update_locals() {
    $.getJSON('/get_localization', function (response) {
        var data = response.data;
        map.addSource('data', {
            type: 'geojson',
            data: data
        });

         map.addLayer({
            id: 'local',
            type: 'circle',
            source: 'data',
            paint: {
                'circle-color': '#ff1e37',
                // 'circle-color': {
                //     property: 'count',
                //     type: 'categorical',
                // },
                'circle-radius': {
                    property: 'count',
                    stops: [[1, 5], [10, 12], [50, 25], [200, 35]]
                },
                'circle-opacity': {
                    property: 'count',
                    stops: [[1, .3], [50, .1], [200, .05]]
                },
                'circle-blur': 0
            }
        });

    });
}

function get_related() {
    // console.log(trending_entity_list);
    $.post('/get_related',
        {
            'entity_list': JSON.stringify(trending_entity_list)
        },
        function (response) {
            $.each(response, function (k, v) {
                var info_div = $('.trending-entity-info[entity="' + k + '"]');
                $.each(v, function (i, m) {
                    info_div.append($('<span></span>')
                        .addClass('tag')
                        .addClass('opacity70')
                        .text(m));
                });
            })
        // console.log(response);
        },
        'json');
}
