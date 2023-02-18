document.addEventListener('alpine:init', () => {
    Alpine.data('global', () => (
        {
            init() {
                this.poller();
            },
            sleep(ms) {
                return new Promise(resolve => setTimeout(resolve, ms));
            },
            alerts: [],
            repo_contents: [],
            continue_polling: true,

            edit_git: false,
            edit_command: false,
            show_command_templates: false,

            model_login_t1: '',
            model_login_t2: '',

            model_command: '',

            satellite_status: '...',
            satellite_status_style: 'u-styled-red',
            show_destroy_git: false,
            packages: {},

            git_is_private: false,
            git_url_exists: false,
            repo_dot_git_config_exists: false,
            venv_exists: false,
            command_exists: false,

            poller() {
                this.status_();
                if (this.continue_polling === true) {
                    this.sleep(5000).then(() => {
                        this.poller();
                    });
                }
            },
            status_() {
                fetch(`/api/status`, {})
                    .then(response => response.json()).then(jsond => {
                    this.repo_contents = jsond.repo_contents;
                    this.satellite_status = jsond.satellite_status;
                    this.venv_exists = jsond.venv_exists;
                }).catch(_ => {
                    this.continue_polling = false;
                })
            },
            scroll_to_bottom(el) {
                el.scrollTop = el.scrollHeight;
            },
            clone_repo(el) {
                this.alerts = []
                el.innerText = 'Cloning...';
                fetch(`/api/clone-repo`, {})
                    .then(response => response.json()).then(jsond => {
                    this.alerts = jsond.alerts;
                    if (jsond.success === true) {
                        this.repo_dot_git_config_exists = true;
                        this.status_();
                    }
                    el.innerText = 'Clone';
                }).catch(error => {
                    console.log(error);
                })
            },
            pull_repo(el) {
                this.alerts = []
                el.innerText = 'Pulling Changes...';
                fetch(`/api/pull-repo`, {})
                    .then(response => response.json()).then(jsond => {
                    this.alerts = jsond.alerts;
                    el.innerText = 'Pull Changes';
                }).catch(error => {
                    console.log(error);
                })
            },
            destroy_repo() {
                this.alerts = []
                fetch(`/api/destroy-repo`, {})
                    .then(response => response.json()).then(jsond => {
                    this.alerts = jsond.alerts;
                    if (jsond.success) {
                        this.show_destroy_git = false;
                        this.repo_dot_git_config_exists = false;
                        this.status_();
                    }
                }).catch(error => {
                    console.log(error);
                })
            },
            app_start(el) {
                el.innerText = 'Starting...';
                fetch(`/api/start`, {})
                    .then(response => response.json()).then(jsond => {
                    if (jsond.success === true) {
                        this.satellite_status = true;
                    }
                }).catch(_ => {
                    this.continue_polling = false;
                })
                el.innerText = 'Start';
            },
            app_restart(el) {
                el.innerText = 'Restarting...';
                fetch(`/api/restart`, {})
                    .then(response => response.json()).then(jsond => {
                    if (jsond.success === true) {
                        this.satellite_status = true;
                    }
                }).catch(_ => {
                    this.continue_polling = false;
                })
                el.innerText = 'Restart';
            },
            app_stop(el) {
                el.innerText = 'Stopping...';
                fetch(`/api/restart`, {})
                    .then(response => response.json()).then(jsond => {
                }).catch(_ => {
                    this.continue_polling = false;
                })
                el.innerText = 'Stop';
            },
            create_venv(el) {
                el.innerText = 'Creating Virtual Environment...';
                fetch(`/api/create-venv`, {})
                    .then(response => response.json()).then(jsond => {
                }).catch(_ => {
                    this.continue_polling = false;
                })
                el.innerText = 'Create Virtual Environment';
            }
        }
    ));
});