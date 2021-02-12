const API_SERVER = 'http://localhost:3001'

window.onload = function () {

    addListener('.filter-merge-request', 'click', mr_filtered);

    const select_group = document.querySelectorAll('#dropdown_menu_group .dropdown-content .dropdown-item');
        if(select_group){
            for (var select of select_group) {
                select.onclick = (e) => {
                    const target = e.target; // элемент который вызвал событие
                    mr_check_select_group(target, '#button_menu_group');
                }
            }
        }

    const select_profile = document.querySelectorAll('#dropdown_menu_profile .dropdown-content .dropdown-item');
        if(select_profile){
            for (var select of select_profile) {
                select.onclick = (e) => {
                    const target = e.target; // элемент который вызвал событие
                    mr_check_select_group(target, '#button_menu_profile');
                }
            }
        }

    addListener('#mr_search', 'input', mr_search);
    addListener('#check_all', 'change', mr_select_file);
    addListener('#btn_create_deploy', 'click', mr_create_deploy);
    addListener('#btn_create_deploy_script', 'click', mr_create_deploy);
    addListener('#btn_create_rollback_script', 'click', mr_create_deploy);
    addListener('#button_menu_group', 'click', mr_click_select_group);
    addListener('#button_menu_profile', 'click', mr_click_select_group);
    addListener('#btn_create_list', 'click', mr_create_object_list);

    init()
}

/* Добавление простого слушателя */
function addListener(sourceElement, action, callback){
    let sourceElements = document.querySelectorAll(sourceElement);
    for (var item of sourceElements) {
        item.addEventListener(action, function(){
            callback(this);
        }, true);
    }
}

function init(){
    let project_url = window.location.pathname;
    let url = API_SERVER + "/api/v1"+ project_url;
    $.ajax({
        url: url,
        type: 'post',
        dataType: 'json',
        success: function(data){
            let project_name = document.querySelector('#project_name')
            project_name.innerHTML = data.project.name
            let project_desc = document.querySelector('#project_desc')
            project_desc.innerHTML = data.project.description

            const merge_requests_buttons = document.querySelector('#merge_requests_buttons');

            data.merge_requests.forEach(function(element){
                    var a = document.createElement('a');
                    a.innerHTML = mr_line_panel(element)
                    merge_requests_buttons.parentNode.insertBefore(a, merge_requests_buttons)
                });

            const containers = document.querySelectorAll('a.panel-block');
            if(containers){
                for (var container of containers) {
                    container.onclick = (e) => {
                        const target = e.target; // элемент который вызвал событие
                        if(target.classList.contains("get-change-list")){
                            mr_panel_click(target);
                        }
                        if(target.classList.contains("merge-request-link")){
                            mr_open_merge_request(target);
                        }
                    }
                }
            }
            $('#load_icon').hide();
        },
        error: function(e){
            console.log("Error load list MR")
        }
    });
}

/* Переключение фильтров списка mergerequest*/
function mr_filtered(obj){
    let filter = obj.getAttribute('data-filter');
    let panel = document.querySelectorAll('a.panel-block');
    for (var item of panel) {
        if(filter == 'all'){
            item.classList.remove("hidden");
        }else{
            switch(item.getAttribute('data-stage')) {
                case filter:
                    item.classList.remove("hidden");
                    break
                default:
                    item.classList.add("hidden");
            }
        }
        item.classList.remove("is-active");
    }
    for (var i = 0; i < obj.parentElement.children.length; i++) {
          let elem = obj.parentElement.children[i];
          elem.classList.remove("is-active");
    }
    obj.classList.add("is-active");
}

/* Обработка нажатия по блоку, вызыввет отображени объектов в таблице */
function mr_panel_click(obj){
    let panel = document.querySelectorAll('a.panel-block');
    for (var item of panel) {
        item.classList.remove("is-active");
    }
    let block_element = obj.parentElement.parentElement.parentElement.parentElement;
    block_element.classList.add("is-active");
    mr_changes_files(obj);
    let ch_check_all = document.querySelector('#check_all');
    ch_check_all.checked = false;
}

/* Фильтрация списка mergerequest в зависимости от введенных символов */
function mr_search(obj){
    let vl = obj.value.toLowerCase();
    let panel = document.querySelectorAll('a.panel-block');
    for (var item of panel) {
        if(vl.length>2){
            let elem = item.querySelector('span:last-child');
            let txt = elem.innerHTML.toLowerCase();
            if(txt.indexOf(vl)>0){
                item.classList.remove("hidden");
            }else{
                item.classList.add("hidden");
            }
        }else{
            item.classList.remove("hidden");
        }
        item.classList.remove("is-active");
    }
}

/* Запрос на получение информации по измененным файлам */
function mr_changes_files(obj){
    let merge_request_id = obj.getAttribute('data-mr_id');
    let project_url = window.location.pathname;
    let url = API_SERVER + "/api/v1"+ project_url +"/merge_request/" + merge_request_id + "/changes-files";
    $('#load_icon').show();
    $.ajax({
        url: url,
        type: 'post',
        dataType: 'json',
        success: function(data){
            let mr_table_files = document.querySelector('#mr_ul_files');
            mr_table_files.setAttribute('data-mr_id', merge_request_id);
            mr_table_files.innerHTML = "";
            var html = "";
            for(var i in data){
                let id = Number(i) + 1;
                html += mr_create_files_row(id,data[i].new_path, data[i].web_url, getClazzRowByStage(data[i]));
            }
            mr_table_files.innerHTML = html;
            var el = document.getElementById('mr_ul_files');
            var sortable = Sortable.create(el);
            $('#load_icon').hide();
        },
        error: function(e){
            console.log("error")
        }
    });
}

/*  переход на gitlab (ссылка на merge request) */
function mr_open_merge_request(obj){
    let link = obj.getAttribute('data-href');
    window.open(link, '_blank');
}

/* Формирует строку для строки измененнных файлов */
function mr_create_files_row(id, item, link, clazz){
    var html =
        '<li>\
            <span class="cb-file-column"><input type="checkbox" class="cb-check-file" value="'+ item +'"></span>\
            <span class="cb-body-column"><span class="'+ clazz +'">'+ item +'</span></span>\
            <span class="cb-link-column"><a href="'+ link +'" title="Просмотр файла" target="_blank"><i class="fa fa-link"></i></a></span>\
            <span class="cb-result-column"><i class="fa fa-check" style="display:none"></i></span>\
        </li>'
    return html;
}
/* определяем класс для строки таблицы */
function getClazzRowByStage(data){
    if(data.deleted_file){
        return 'is-deleted';
    }
    if(data.new_file){
        return 'is-added';
    }
    if(data.renamed_file){
        return 'is-rename';
    }
    return 'is-modified';
}

/* Устанавливаем/снимаем все галочки с файлов */
function mr_select_file(obj){
    let checkbox_list = document.querySelectorAll('.cb-check-file');
    for(var cb of checkbox_list){
        if(obj.checked){
            cb.checked = true;
        }else{
            cb.checked = false;
        }
    }
}

/* Сбор выделенных файлов и отправка на сервер для формирования xml */
function mr_create_deploy(obj){
    let checkbox_list = document.querySelectorAll('.cb-check-file');
    let merge_request_id = document.querySelector('#mr_ul_files').getAttribute('data-mr_id');
    let project_url = window.location.pathname;
    let project_id = project_url.replace('/project/', '');
    var cb_check_list = [];
    for(var cb of checkbox_list){
        let el = cb.parentElement.nextElementSibling.nextElementSibling.nextElementSibling.firstElementChild;
        el.style.display = "none";
        if(cb.checked){
            var clazz = cb.parentElement.parentElement.querySelector('.cb-body-column span');
            var clazz_value = "";
            if(clazz.classList.length>0){
                clazz_value = clazz.classList[0];
            }
            /* Данные для формирования списка */
            var file_obj = {name:cb.value, state: clazz_value};
            cb_check_list.push(file_obj);
        }
    }
    let setting = {
        group: 'dev',
        profile: 'mssql'
    }
    let url = "";
    if(obj.id == 'btn_create_deploy'){
        url = API_SERVER + "/api/v1"+ project_url +"/merge_request/" + merge_request_id + "/create-deploy";
    }else if(obj.id == 'btn_create_deploy_script'){
        url = API_SERVER + "/api/v1"+ project_url +"/merge_request/" + merge_request_id + "/create-deploy-script";
    }else{
        url = API_SERVER + "/api/v1"+ project_url +"/merge_request/" + merge_request_id + "/create-rollback-script";
    }
        $.ajax({
            url: url,
            type: 'post',
            data: {
                files: JSON.stringify(cb_check_list),
                setting: JSON.stringify(setting)
            },
            success: function(data){
                let obj = JSON.parse(data);
                console.log('success', obj)
                if (obj.status == 200){
                    if (obj.type == 'deploy'){
                        console.log('download')
                        window.open(API_SERVER + "/api/v1/download-deploy/"+obj.filename,"_blank");
                    }
                    if(!obj.objects) return
                    for(var cb of checkbox_list){
                        if(cb.checked){
                            let el = cb.parentElement.nextElementSibling.nextElementSibling.nextElementSibling.firstElementChild;
                            let vEl = cb.parentElement.nextElementSibling.firstElementChild;
                            let current = vEl.innerHTML;
                            for(var name of obj.objects){
                                if(current.indexOf(name)>0){
                                    el.style.display = "inline-block";
                                }
                            }
                        }
                    }
                }
            },
            error: function(e){
                console.log("error")
            }
        });
}

/* Обработка выпадающих списков */
function mr_click_select_group(obj){
    let select_group = obj.parentElement.parentElement;
    if (select_group.classList.contains('is-active')){
        select_group.classList.remove("is-active");
    }
    else{
        select_group.classList.add("is-active");
    }
}

function mr_check_select_group(obj, clazz){
    const button = document.querySelector(clazz);
    button.querySelector('span').innerHTML = obj.innerHTML;
    mr_click_select_group(button);
}

/* Строка в списке мердж реквестов */
function mr_line_panel(merge_request_info){
    let title = merge_request_info.source_branch + ' => ' + merge_request_info.target_branch
    var icon = ''
    if (merge_request_info.state == 'opened'){
        icon = 'fa fa-question'
    }
    if (merge_request_info.state == 'merged'){
        icon = 'fa fa-check'
    }
    if (merge_request_info.state == 'close'){
        icon = 'fa fa-times'
    }
    if (merge_request_info.state == 'cannot_be_merged'){
        icon = 'fa fa-exclamation-triangle'
    }

    let html = '<a class="panel-block" data-stage="' + merge_request_info.state + '" title="' + title + '">\
        <div class="level" style="width:100%">\
            <div class="level-left">\
                <div class="level-item">\
                    <span class="panel-icon">\
                      <i class="' + icon + '" aria-hidden="true"></i>\
                    </span>\
                        <span class="get-change-list text-overflow" data-mr_id="' + merge_request_info.id + '">' + merge_request_info.title + '</span>\
                </div>\
            </div>\
            <div class="level-right">\
                <span class="panel-icon">\
                    <i class="fa fa-link merge-request-link" data-href="' + merge_request_info.web_url + '" aria-hidden="true"></i>\
                </span>\
            </div>\
        </div>\
    </a>'
    return html
}
/* просто список отмеченныъ файлов */
function mr_create_object_list(obj){
    let checkbox_list = document.querySelectorAll('.cb-check-file');
    let merge_request_id = document.querySelector('#mr_ul_files').getAttribute('data-mr_id');
    let project_url = window.location.pathname;
    let project_id = project_url.replace('/project/', '');
    var cb_check_list = [];
    for(var cb of checkbox_list){
        let el = cb.parentElement.nextElementSibling.nextElementSibling.nextElementSibling.firstElementChild;
        el.style.display = "none";
        if(cb.checked){
            var clazz = cb.parentElement.parentElement.querySelector('.cb-body-column span');
            var clazz_value = "";
            if(clazz.classList.length>0){
                clazz_value = clazz.classList[0];
            }
            /* Данные для формирования списка */
            part_name = cb.value.split('/');
            cb_check_list.push(part_name[part_name.length-1].replace(".sql", ""));
        }
    }

    download("objects.txt",cb_check_list.join("\n"));
}

function download(filename, text) {
  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}


