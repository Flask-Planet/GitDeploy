document.addEventListener('alpine:init', () => {
    Alpine.data('global', () => (
        {
            init() {
                this.get_repo_contents()
            },
            alerts: [],
            repo_contents: [],

            edit_git: false,
            edit_command: false,
            show_command_templates: false,

            model_login_t1: '',
            model_login_t2: '',

            model_command: '',

            git_app_status: 'Stopped',
            git_app_status_style: 'u-styled-red',
            show_destroy_git: false,
            packages: {},
            show_settings_token: false,

            git_url_exists: false,
            repo_dot_git_config_exists: false,
            venv_exists: false,
            command_exists: false,

            scroll_to_bottom(el) {
                el.scrollTop = el.scrollHeight;
            },
            get_repo_contents() {
                fetch(`/api/get-repo-contents`, {})
                    .then(response => response.json()).then(jsond => {
                    this.repo_contents = jsond.repo_contents;
                }).catch(error => {
                    console.log(error);
                })
            },
            clone_repo(el) {
                this.alerts = []
                el.innerText = 'Cloning...';
                fetch(`/api/clone-repo`, {})
                    .then(response => response.json()).then(jsond => {
                    this.alerts = jsond.alerts;
                    if (jsond.success) {
                        this.repo_dot_git_config_exists = true;
                        this.get_repo_contents();
                        el.innerText = 'Clone';
                    }
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
                        this.get_repo_contents();
                    }
                }).catch(error => {
                    console.log(error);
                })
            },
            app_status() {

            },
            app_start() {

            },
            app_restart() {

            },
            app_stop() {

            },
            git_manual_pull() {

            },
            env_get_packages() {

            }
        }
    ));
});