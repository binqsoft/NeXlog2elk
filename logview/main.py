import os
import json
import datetime
from flask import Flask, render_template, jsonify, request, Response, stream_with_context, session, redirect, url_for
from elasticsearch import Elasticsearch, NotFoundError

ES_HOST = os.environ.get('ES_HOST', 'localhost')
ES_USER = os.environ.get('ES_USER', 'elastic')
ES_PASS = os.environ.get('ES_PASS', 'changeme')

es = Elasticsearch(
    [ES_HOST],
    http_auth=(ES_USER, ES_PASS),
    port=9200,
    use_ssl=False
)


def log2es(body):
    es.index(index='nexpose-process-log', doc_type='nexpose-process-log', body=body)


try:
    es.get_source(index='nexpose-log-user', doc_type='user', id='admin')
except NotFoundError as e:
    es.create(index='nexpose-log-user', doc_type='user', id='admin', body=json.dumps({
        '_password': 'Nexpose01!'
    }))


def get_admin_user(username):
    try:
        return es.get_source(index='nexpose-log-user', doc_type='user', id=username)
    except NotFoundError as e:
        return None


app = Flask(__name__)

app.secret_key = 'Nexpose'


@app.route('/')
def home():
    user = session.get('current_user')
    if not user:
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    errors = {}
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = get_admin_user(username)
        if not user:
            errors['username'] = '用户不存在'
        elif password != user['_password']:
            errors['password'] = '密码不正确'
        else:
            session['current_user'] = username
            return redirect(url_for('home'))
    return render_template('login.html', errors=errors)


@app.route('/api/nexpose-<string:index>/<int:offset>', methods=['GET'])
def nexpose_api(index, offset):
    q = request.args.get('q')
    params = {
        'size': 50,
        'from': offset,
        'sort': 'timestamp:desc'
    }
    if q:
        params['q'] = q
    resp = es.search(index='nexpose-{}-*'.format(index), params=params)
    resp['offset'] = offset
    resp['size'] = 50
    return jsonify(resp)


@app.route('/api/nexpose-<string:index>/remove-selected', methods=['DELETE'])
def remove_selected(index):
    selected_ids = request.json.get("selectedIds")
    for selected_id in selected_ids:
        doc_index, doc_type, doc_id = selected_id.split("/")
        try:
            doc = es.get_source(index=doc_index, doc_type=doc_type, id=doc_id)
            es.delete(index=doc_index, doc_type=doc_type, id=doc_id)
            log2es(json.dumps({
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'action': 'remove_selected',
                'res_id': doc_id,
                'message': doc['message'],
                'actionResult': '操作成功'
            }))
        except NotFoundError as e:
            log2es(json.dumps({
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'action': 'remove_selected',
                'actionResult': '操作失败'
            }))
    
    return jsonify({
        'success': True
    })


@app.route('/api/nexpose-<string:index>/remove-all', methods=['DELETE'])
def remove_all(index):
    q = request.args.get('q')
    params = {
    
    }
    if q:
        params['q'] = q
    resp = es.delete_by_query(index='nexpose-{}-*'.format(index), body={}, params=params)
    return jsonify(resp)


@app.route('/api/nexpose-<string:index>/backup', methods=['GET'])
def backup(index):
    def generate():
        q = request.args.get('q')
        params = {
            'size': 10,
            'from': 0,
            'sort': 'timestamp:asc'
        }
        if q:
            params['q'] = q
        resp = es.search(index='nexpose-{}-*'.format(index), params=params)
        while len(resp['hits']['hits']) > 0:
            for hit in resp['hits']['hits']:
                yield hit['_source']['message']
                yield '\n'
            params['from'] += 10
            resp = es.search(index='nexpose-{}-*'.format(index), params=params)
    
    response = Response(stream_with_context(generate()))
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Disposition'] = 'attachment; filename={}.log'.format(index)
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
