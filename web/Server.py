from bottle import static_file, route, view, run, response
import bottle
import os


@route('/images/<filename:re:.*\.png>')
def send_image(filename):
    return static_file(filename, root=os.path.join(cd, 'web/images'), mimetype='image/png')


@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root=os.path.join(cd, 'web/static/'))


@route('/project/<id:int>')
@view('deploy')
def hello(id):
    return dict()


@route('/')
@view('index')
def hello():
    return dict()


# Проверка готовности к работе сервиса
@route('/ready')
def ready():
    return ''


if __name__ == "__main__":
    cd = os.getcwd()
    bottle.TEMPLATE_PATH.insert(0, os.path.join(cd, 'web/template'))
    run(host='0.0.0.0', port=8088, debug=True, reloader=True)
