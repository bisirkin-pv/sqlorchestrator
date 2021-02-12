
<nav class="panel">
    <p class="panel-heading">
        Merge requests
        <span id="load_icon" style="display:inline-block;"><i class="fa fa-spinner fa-spin"></i></span>
    </p>
    <div class="panel-block">
        <p class="control has-icons-left">
            <input class="input is-small" type="text" placeholder="filter" id="mr_search"/>
            <span class="icon is-small is-left">
        <i class="fa fa-search" aria-hidden="true"></i>
      </span>
        </p>
    </div>
    <p class="panel-tabs" id="merge_requests_tab">
        <a class="is-active filter-merge-request" data-filter="all">all</a>
        <a class="filter-merge-request" data-filter="opened">opened</a>
        <a class="filter-merge-request" data-filter="merged">merged</a>
        <a class="filter-merge-request" data-filter="closed">closed</a>
    </p>

    <div class="panel-block" id="merge_requests_buttons">
        <div class="level" style="width:100%">
            <div class="level-left">
                <div class="buttons">
                    <button class="button is-link is-outlined" id="btn_create_deploy">
                        Create xml
                    </button>
                    <button class="button is-link is-outlined" id="btn_create_list">
                        Objects list
                    </button>
                </div>
            </div>
            <div class="level-right">
                <div class="buttons">
                    <button class="button is-info is-outlined" id="btn_create_rollback_script">
                        Create rollback
                    </button>
                    <button class="button is-link is-outlined" id="btn_create_deploy_script">
                        Create deploy
                    </button>
                </div>
            </div>
        </div>
    </div>
</nav>