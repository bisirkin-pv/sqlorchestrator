<!doctype html>
<html lang="en">
<head>
    % include('header.tpl')
    <link href="/static/css/merge-request.css" rel="stylesheet" />
    <script src="/static/js/merge_request.js"></script>
    <script src="/static/js/Sortable.min.js"></script>
</head>
<body>
    % include('caption.tpl')
    <div class="container">
        <hr />
        <h3 class="title is-3" id="project_name">
            Name
        </h3>
        <h4 class="title is-4" id="project_desc">
            Desc
        </h4>
        <div class="tile is-ancestor">
            <div class="tile is-5 is-vertical is-parent">
                <div class="tile is-child">
                    % include('merge_requests.tpl')
                </div>
            </div>
            <div class="tile is-parent">
                <div class="tile is-child box">
                    % include('mr_table.tpl')
                </div>
            </div>
        </div>
    </div>
</body>
</html>