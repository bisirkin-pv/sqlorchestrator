<!doctype html>
<html lang="en">
<head>
    % include('header.tpl')
    <link href="/static/css/index.css" rel="stylesheet" />
    <script src="/static/js/index.js"></script>
</head>
<body>
<header>
    <div class="container">
        <!-- Main container -->
        <nav class="level">
            <!-- Left side -->
            <div class="level-left">
                <div class="level-item">
                    <p class="subtitle is-5">
                        <img class="logo" src="/static/img/dog.png" style="height: 64px">
                    </p>
                </div>
            </div>

            <!-- Right side -->
            <div class="level-right">
                <div class="level-item">
                    <div class="field">
                        <div class="control has-icons-left has-icons-right">
                            <input class="input" type="text" placeholder="Enter name project" value="" id="prj_name">
                            <span class="icon is-small is-left">
                                <i class="fa fa-hashtag"></i>
                            </span>
                            <span class="icon is-small is-right is-hidden" id="icon_add_result">
                                <i class="fa fa-check"></i>
                            </span>
                        </div>
                        <p class="help is-hidden" id="add_result"></p>
                    </div>
                </div>
            </div>
        </nav>
    <hr/>
    </div>
</header>
<div class="container" id="prj_block_main">
    <div class="columns">

    </div>

</div>
</body>
</html>