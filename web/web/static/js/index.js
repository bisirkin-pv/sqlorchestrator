const API_SERVER = 'http://localhost:3001'

window.onload = function () {

    const container = document.querySelector('#prj_block_main');
    if(container){
        container.onclick = (e) => {
           const target = e.target; // элемент который вызвал событие
           let prj_id = target.getAttribute('data-prj_id');
           if(prj_id){
                prj_delete(target)
           }
        }
    }

    const prj_name = document.querySelector('#prj_name');
    if(prj_name){
        prj_name.onkeyup = function(e) {
            // спец. сочетание - не обрабатываем
            if(e.keyCode === 13){
                prj_add();
            }else{
                prj_add_class_clear();
            }
            return false;
        }
    }

    init()
}

/* Востанавливаем значение из localStorage */
function init(){

    for(let i=0; i<localStorage.length; i++) {
        let key = localStorage.key(i);
        let result_json = JSON.parse(localStorage.getItem(key));
        prj_create_block_main(result_json);
    }

}

/* index.tpl */
function prj_delete(obj){
    let prj_id = obj.getAttribute('data-prj_id');
    let prj_block = document.querySelectorAll('.project-block');
    for (var item of prj_block) {
        if(item.getAttribute('data-prj_id') == prj_id){
            item.parentElement.remove()
        }
    }
}

function prj_add(){
    let txt = document.querySelector('#prj_name');
    if(txt.value != ''){
        prj_search(txt);
    }
}

function prj_search(txt){
    let key = txt.value
    $.ajax({
        url: API_SERVER + "/api/v1/projects",
        type: 'post', // performing a POST request
        data : {
            name : txt.value // will be accessible in $_POST['data1']
        },
        dataType: 'json',
        success: function(data){
            if(data.id){
                txt.value = '';
                if(prj_find_id_in_block(data.id)){
                    prj_add_info('This project has already been added', 'is-warning', 'fa fa-exclamation-triangle')
                    return;
                };
                prj_create_block_main(data);
                localStorage.setItem(key, JSON.stringify(data));
                prj_add_info('Success', 'is-success', 'fa fa-check')
            }else{
                prj_add_info('Project not found', 'is-danger', 'fa fa-times');
            }
        },
        error: function(e){
            prj_add_info('Error', 'is-danger', 'fa fa-times')
        }
    });
}

/* Проверяем был ли уже такой проект добавлен */
function prj_find_id_in_block(prj_id){
    let prj_block_column = document.querySelectorAll('#prj_block_main .columns .column');
    for (var column of prj_block_column) {
        let prj_blocks = column.querySelectorAll('.project-block');
        for (var block of prj_blocks) {
            if(block.getAttribute('data-prj_id') == prj_id){
                return true;
            }
        }
    }
    return false;
}

function prj_create_block_main(param_json){
    let prj_block_main = document.querySelector('#prj_block_main');
    let prj_block_columns = prj_block_main.querySelectorAll('.columns');
    let prj_block_column = prj_block_columns[0].querySelectorAll('.column');
    let elemCnt = prj_block_columns.length * prj_block_column.length + 1
    var div = document.createElement('div');
    div.className = "column";
    div.innerHTML = prj_create_block(param_json);
    prj_block_columns[0].appendChild(div);
}

function prj_create_block(param_json){
    let web_img = param_json.avatar_url || '/static/img/icon_project.png'
    var html = '<article class="message is-link project-block" data-prj_id="' + param_json.id + '">\
                <div class="message-header">\
                    <p>' + param_json.name + '</p>\
                    <button class="delete project-delete" aria-label="delete" data-prj_id="'+ param_json.id +'"></button>\
                </div>\
                <div class="message-body level clear-margin-bottom">\
                    <div class="level-left">\
                        <div class="level-item">\
                            <figure class="image is-64x64">\
                               <img class="is-rounded" src="'+ web_img +'">\
                            </figure>\
                        </div>\
                    </div>\
                    <div class="level-right caption">\
                        <div class="level-item caption">\
                        '+ param_json.description +'\
                        </div>\
                    </div>\
                </div>\
                <div class="level message-footer">\
                    <div class="level-left">\
                        <div class="level-item">\
                        <a href="'+ param_json.web_url +'" target="_blank">GitLab</a>\
                        </div>\
                    </div>\
                    <div class="level-right">\
                        <div class="level-item">\
                            <a class="button is-link" href="/project/' + param_json.id + '">GO</a>\
                        </div>\
                    </div>\
                </div>\
            </article>'
    return html;
}


function prj_add_info(txt, type, icon){
    let add_input = document.querySelector('#prj_name');
    let add_input_icon = document.querySelector('#icon_add_result');
    let add_input_icon_i = add_input_icon.querySelector('i');
    let add_input_text = document.querySelector('#add_result');

    add_input.classList.add(type);
    add_input_icon.classList.remove("is-hidden");
    add_input_icon_i.classList = icon;
    add_input_text.classList.remove("is-hidden");
    add_input_text.classList.add(type);
    add_input_text.innerHTML = txt;
}

function prj_add_class_clear(){
    let add_input = document.querySelector('#prj_name');
    let add_input_icon = document.querySelector('#icon_add_result');
    let add_input_icon_i = add_input_icon.querySelector('i');
    let add_input_text = document.querySelector('#add_result');

    add_input.classList = "input";
    add_input_icon.classList.add("is-hidden");
    add_input_text.classList = "help is-hidden";
}