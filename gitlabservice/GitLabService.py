from bottle import route, Bottle, request, json_loads, response, static_file
import bottle
import os
import gitlab
import urllib3
import json
from utility.deploy.CreateDeployFileXmlOld import CreateDeployFileXmlOld
from utility.deploy.CreateDeployFileSql import CreateDeployFileSql
from utility.model.DeployFileModel import DeployFileHeader
from prometheus_client import generate_latest, REGISTRY, Gauge, Counter, Summary, Info
from datetime import datetime
from functools import wraps
import logging
import logging.config


logging.config.fileConfig('logging.conf')
logger = logging.getLogger("gitlabservice")
logger.setLevel('DEBUG')


def log_to_logger(fn):
    '''
    Wrap a Bottle request so that a log line is emitted after it's handled.
    (This decorator can be extended to take the desired logger as a param.)
    '''
    @wraps(fn)
    def _log_to_logger(*args, **kwargs):
        request_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        actual_response = fn(*args, **kwargs)
        # modify this to log exactly what you need:
        if 'ready' not in request.url:
            logger.info('%s %s %s %s' % (request.remote_addr,
                                         request.method,
                                         request.url,
                                         response.status))
        return actual_response
    return _log_to_logger


app = Bottle()
app.install(log_to_logger)

# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('gitlabservice_request_processing_seconds', 'Time spent processing request')
REQUEST_TIME.observe(4.7)
#IN_PROGRESS = Gauge("gitlabservice_inprogress_requests", "help")
REQUESTS = Counter('gitlabservice_http_requests_total', 'Description of counter', ['method', 'endpoint'])
INFO = Info('gitlabservice_version', 'Description of info')
INFO.info({'version': '1.1', 'port': '3001'})


def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if bottle.request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

    return _enable_cors


# Скачивание файлов
@app.route('/api/v1/download-deploy/<filename:path>', method=['OPTIONS', 'GET'])
@enable_cors
def download_deploy_file(filename):
    return static_file(filename, root=os.path.join(cd, 'tmp'), download=filename)


# api
@app.route('/api/v1/projects', method=['OPTIONS', 'POST'])
@enable_cors
def project_get():
    REQUESTS.labels(method='POST', endpoint="project_get").inc()
    urllib3.disable_warnings()
    name = request.forms.get('name')
    with gitlab.Gitlab.from_config('home', ['config/gitlab.ini']) as gl:
        try:
            project = gl.projects.get(name)
            project_dict = {
                            'id': project.id,
                            'name': project.name,
                            'description': project.description,
                            'web_url': project.web_url,
                            'avatar_url': project.avatar_url,
                            }
            return json.JSONEncoder().encode(project_dict)
        except:
            logger.error('Project [{0}] not found'.format(name))
        return '{}'


@app.route('/api/v1/project/<project_id:int>', method=['OPTIONS', 'POST', 'GET'])
@enable_cors
@REQUEST_TIME.time()
def project_merge_request_list(project_id):
    REQUESTS.labels(method='POST', endpoint="project_merge_request_list").inc()
    urllib3.disable_warnings()
    with gitlab.Gitlab.from_config('home', ['config/gitlab.ini']) as gl:
        project = gl.projects.get(project_id)
        project_dict = {
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'web_url': project.web_url,
            'avatar_url': project.avatar_url,
        }
        merge_requests_list = project.mergerequests.list()
        mr_list = []
        for mr_item in merge_requests_list:
            mr = project.mergerequests.get(mr_item.iid)
            mr_dict = {
                'id': mr.iid,
                'title': mr.title,
                'state': mr.state,
                'web_url': mr.web_url,
                'target_branch': mr.target_branch,
                'source_branch': mr.source_branch,
                'merge_status': mr.merge_status,
            }
            mr_list.append(mr_dict)
        result = {
            'project': project_dict,
            'merge_requests': mr_list,
        }
        return result


# Список измененных файлов
@app.route('/api/v1/project/<project_id:int>/merge_request/<merge_request_id:int>/changes-files'
           , method=['OPTIONS', 'POST'])
@enable_cors
def merge_request_change_files(project_id, merge_request_id):
    urllib3.disable_warnings()
    REQUESTS.labels(method='POST', endpoint="merge_request_change_files").inc()
    diff_dict_list = []
    with gitlab.Gitlab.from_config('home', ['config/gitlab.ini']) as gl:
        project = gl.projects.get(project_id)
        mr = project.mergerequests.get(merge_request_id)
        link = mr.web_url[:mr.web_url.find("/merge_requests/")]
        diffs = mr.diffs.list()
        for mr_diff in diffs:
            diff = mr.diffs.get(mr_diff.id)
            for file in diff.diffs:
                filename, file_extension = os.path.splitext(file.get('new_path'))
                if file_extension == '.sql':
                    link_item = os.path.join(link, 'blob', mr_diff.head_commit_sha, file.get('new_path'))
                    diff_dict = {
                        'web_url': link_item,
                        'head_commit_sha': mr_diff.head_commit_sha,
                        'old_path': file.get('old_path'),
                        'new_path': file.get('new_path'),
                        'new_file': file.get('new_file'),
                        'renamed_file': file.get('renamed_file'),
                        'deleted_file': file.get('deleted_file'),
                    }
                    diff_dict_list.append(diff_dict)
            break
    return json.JSONEncoder().encode(diff_dict_list)


# Формирования файла деплоя xml
@app.route('/api/v1/project/<project_id:int>/merge_request/<merge_request_id:int>/create-deploy'
           , method=['OPTIONS', 'POST'])
@enable_cors
def merge_request_create_deploy(project_id, merge_request_id):
    files = json_loads(request.params.get('files'))
    setting = json_loads(request.params.get('setting'))
    deploy_file_header = DeployFileHeader(setting.get('group'), setting.get('profile'))
    deploy_xml = CreateDeployFileXmlOld(files, deploy_file_header)
    return json.JSONEncoder().encode(deploy_xml.create())


# Формирования файла деплоя sql
@app.route('/api/v1/project/<project_id:int>/merge_request/<merge_request_id:int>/create-deploy-script'
           , method=['OPTIONS', 'POST'])
@enable_cors
def merge_request_deploy_script_files(project_id, merge_request_id):
    REQUESTS.labels(method='POST', endpoint="merge_request_change_files").inc()
    files = json_loads(request.params.get('files'))
    with gitlab.Gitlab.from_config('home', ['config/gitlab.ini']) as gl:
        project = gl.projects.get(project_id)
        deploy_xml = CreateDeployFileSql(files, project, merge_request_id, gl.private_token)
        return json.JSONEncoder().encode(deploy_xml.create())


@app.route('/api/v1/project/<project_id:int>/merge_request/<merge_request_id:int>/create-rollback-script'
           , method=['OPTIONS', 'POST'])
@enable_cors
def merge_request_rollback_files(project_id, merge_request_id):
    REQUESTS.labels(method='POST', endpoint="merge_request_change_files").inc()
    files = json_loads(request.params.get('files'))
    with gitlab.Gitlab.from_config('home', ['config/gitlab.ini']) as gl:
        project = gl.projects.get(project_id)
        deploy_xml = CreateDeployFileSql(files, project, merge_request_id)
        return json.JSONEncoder().encode(deploy_xml.rollback())



# Проверка готовности к работе сервиса
@app.route('/ready')
@enable_cors
def ready():
    return json.JSONEncoder().encode('{"status":"ok"}')


@app.route('/metrics')
def metrics():
    return generate_latest(REGISTRY)


if __name__ == "__main__":
    cd = os.getcwd()
    app.run(host='0.0.0.0', port=3001, quiet=True)
