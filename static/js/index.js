mapboxgl.accessToken = 'pk.eyJ1IjoibGltdGVuZyIsImEiOiJjajJjcGdzNjUwM2NkMndvNzBpeTBrZjFwIn0.9YDJZ3qB_VuNHF3L-ni6PQ';


$(document).ready(function () {
    update_top_entities();
    update_trending_entities();
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
                display: false,
                beginAtZero: true
            }
        }
        ]
    },
    legend: {
        display: false
    }
};

//
// new Chart('timeline-0', {
//     type: 'line',
//     data: {
//         labels: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
//         datasets: [{
//             pointRadius: 0,
//             borderWidth: 1,
//             borderColor: '#dd2434',
//             backgroundColor: 'rgba(143,74,86,0.3)',
//             data: [1, 3, 4, 5, 7, 2, 35, 150, 9, 2, 1, 4, 15, 102, 210, 304, 23, 12, 0, 1, 2, 1, 1, 3, 4, 5, 7, 2, 35, 690, 9, 2, 1, 4, 15, 102],
//             label: 'Dataset',
//             fill: 'start'
//         }]
//     },
//     options: options
// });
// new Chart('timeline-1', {
//     type: 'line',
//     data: {
//         labels: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
//         datasets: [{
//             pointRadius: 0,
//             borderWidth: 1,
//             borderColor: '#dd2434',
//             backgroundColor: 'rgba(143,74,86,0.3)',
//             data: [1, 3, 4, 5, 7, 2, 4, 15, 901, 25, 790, 1, 240, 13, 2, 34, 56, 9, 2, 1, 4, 15, 102, 2, 14, 150, 70, 13, 23, 5, 7, 2, 35, 690, 9, 2, 1, 4, 15, 102],
//             label: 'Dataset',
//             fill: 'start'
//         }]
//     },
//     options: options
// });
// new Chart('timeline-2', {
//     type: 'line',
//     data: {
//         labels: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
//         datasets: [{
//             pointRadius: 0,
//             borderWidth: 1,
//             borderColor: '#dd2434',
//             backgroundColor: 'rgba(143,74,86,0.3)',
//             data: [1, 2, 1, 4, 15, 102, 210, 304, 23, 12, 0, 1, 2, 101, 1, 3, 4, 5, 7, 2, 35, 790, 9, 2, 1, 4, 15, 102, 2, 14, 150, 70, 13, 23, 4, 5, 1],
//             label: 'Dataset',
//             fill: 'start'
//         }]
//     },
//     options: options
// });
// new Chart('timeline-3', {
//     type: 'line',
//     data: {
//         labels: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
//         datasets: [{
//             pointRadius: 0,
//             borderWidth: 1,
//             borderColor: '#dd2434',
//             backgroundColor: 'rgba(143,74,86,0.3)',
//             data: [1, 3, 4, 5, 7, 2, 35, 150, 9, 2, 1, 4, 15, 102, 210, 304, 23, 12, 0, 1, 2, 1, 1, 3, 4, 5, 7, 2, 35, 690, 9, 2, 1, 4, 15, 102],
//             label: 'Dataset',
//             fill: 'start'
//         }]
//     },
//     options: options
// });

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
            console.log(response);

            var trend_entity_list_ul = $('ul#trending-entity-list');
            $.each(response.mentions, function (i, mention) {
                var li_div = $('<li></li>').addClass('trending-entity');

                var name_div = $('<div></div>').addClass('trending-entity-name').text(mention[0]);
                li_div.append(name_div);

                var info_div = $('<div></div>').addClass('trending-entity-info');
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
                    stops: [[1, 5], [10, 10], [50, 20], [200, 30]]
                },
                'circle-opacity': {
                    property: 'count',
                    stops: [[1, .2], [50, .3], [200, .5]]
                },
                'circle-blur': 0
            }
        });

    });
}