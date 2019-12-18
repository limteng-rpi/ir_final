from flask import Flask, request, render_template, jsonify
from src.crawl.database.operation import (get_top_entities, get_trend_entities,
                                          get_localization)

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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=12181)
