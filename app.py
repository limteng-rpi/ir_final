import json

from flask import Flask, request, render_template, jsonify
from src.crawl.database.operation import (get_top_entities, get_trend_entities,
                                          get_localization, get_related)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0



@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/get_top_entities')
def op_get_top_entities():
    top_entities = get_top_entities()
    return jsonify(top_entities)


@app.route('/get_trending_entities')
def op_get_trend_entities():
    trend_entities = get_trend_entities()
    return jsonify(trend_entities)

@app.route('/get_localization')
def op_get_localization():
    locals = get_localization()
    return jsonify(locals)


@app.route('/get_related', methods=['POST'])
def op_get_related():
    entity_list = request.form.get('entity_list')
    entity_list = json.loads(entity_list)
    related = get_related(entity_list)
    return jsonify(related)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=12181)
