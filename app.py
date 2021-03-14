# -*- coding: utf-8 -*-
import hashlib

from flask import Flask
from flask import Response
from flask import request, render_template
import json
from link import parse_link_data
import query
app = Flask(__name__)

conn = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '1234',
    'database': 'rsnav'
}
g_query = query.Query(*conn.values())


def resp_json(_dict):
    content = json.dumps(_dict, ensure_ascii=False)
    resp = Response(content)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['content-type'] = 'application/json'
    return resp


@app.route('/')
def root():
    return resp_json({})


@app.route('/link', methods=['POST'])
def link():
    args = request.args
    url = args.get('url')
    res = parse_link_data(url)
    resp = {'code': 200, 'data': res} if res else {
        'code': 400, 'msg': 'No data is available for this URL'}
    return resp_json(resp)


@app.route('/queryAll', methods=['POST'])
def query_all():
    data_dict = request.json
    rest = g_query.select_all(data_dict)
    total = g_query.select_count(data_dict)[0]
    for it in rest:
        it['category'] = g_query.select_category(it.pop('uid'))
        lid = it['lid']
        it['lid'] = hashlib.md5(str(lid).encode(
            'utf-8')).hexdigest()[0:16] + str(lid)
    return resp_json({'code': 200, 'data': rest, 'total': total['total']})


@app.route('/add', methods=['POST'])
def add():
    data_dict = request.json
    lst = ['title', 'link', 'favicon', 'describe', 'category']
    data_dict = sorted(data_dict.items(), key=lambda item: lst.index(item[0]))
    return resp_json({'code': 200, 'msg': 'add success'}) if g_query.add_item(data_dict) else {'code': 400, 'msg': 'add failed'}


@app.route('/update', methods=['POST'])
def update():
    lst = ['title', 'link', 'favicon', 'describe', 'category', 'lid']
    data_dict = request.json
    data_dict['lid'] = data_dict['lid'][16:]
    query_data = sorted(data_dict.items(), key=lambda item: lst.index(item[0]))
    return resp_json({'code': 200, 'msg': 'update success'}) if g_query.update_item(query_data) else {'code': 400, 'msg': 'update failed'}


@app.route('/delete', methods=['POST'])
def delete():
    lid = request.json.get('lid')
    return {'code': 200, 'msg': 'del success'} if g_query.del_item(lid[16:]) else {'code': 400, 'msg': 'del failed'}


@app.errorhandler(403)
def page_not_found(error):
    resp = resp_json({"code": "403"})
    return resp


@app.errorhandler(404)
def page_not_found(error):
    resp = resp_json({"code": "404"})
    return resp


@app.errorhandler(400)
def page_not_found(error):
    resp = resp_json({"code": "400"})
    return resp


@app.errorhandler(410)
def page_not_found(error):
    resp = resp_json({"code": "410"})
    return resp


@app.errorhandler(500)
def page_not_found(error):
    resp = resp_json({"code": "500"})
    return resp


if __name__ == '__main__':
    app.run(debug=True)  # threaded=True
