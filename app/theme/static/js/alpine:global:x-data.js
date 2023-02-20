document.addEventListener('alpine:init', () => {
    Alpine.data('global', () => ({
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

        satellite_status: false,
        satellite_status_style: 'u-styled-red',
        show_destroy_git: false,
        packages: [],
        has_packages: false,

        git_is_private: false,
        git_url_exists: false,
        repo_dot_git_config_exists: false,
        venv_exists: false,
        command_exists: false,

        package_name: '',
        wh_enabled: false,

        wh_secret: '',

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
                this.packages = jsond.packages;
                this.wh_secret = jsond.wh_secret;
                this.wh_enabled = jsond.wh_enabled;
                if (this.packages) {
                    this.has_packages = this.packages.length > 0;
                }
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
                this.alerts = jsond.alerts;
                if (jsond.success) {
                    el.innerText = 'Start';
                    this.status_();
                } else {
                    el.innerText = 'Error!';
                }
            }).catch(error => {
                console.log(error);
            })
        },
        app_restart(el) {
            el.innerText = 'Restarting...';
            fetch(`/api/restart`, {})
                .then(response => response.json()).then(jsond => {
                this.alerts = jsond.alerts;
                if (jsond.success) {
                    el.innerText = 'Restart';
                    this.status_();
                } else {
                    el.innerText = 'Error!';
                }
            }).catch(error => {
                console.log(error);
            })
        },
        app_stop(el) {
            el.innerText = 'Stopping...';
            fetch(`/api/stop`, {})
                .then(response => response.json()).then(jsond => {
                this.alerts = jsond.alerts;
                if (jsond.success) {
                    el.innerText = 'Stop';
                    this.status_();
                } else {
                    el.innerText = 'Error!';
                }
            }).catch(error => {
                console.log(error);
            })
        },
        create_venv(el) {
            el.innerText = 'Creating Virtual Environment...';
            fetch(`/api/create-venv`, {})
                .catch(_ => {
                    this.continue_polling = false;
                })
            el.innerText = 'Create Virtual Environment';
        },
        pip_install(el) {
            el.innerText = 'Installing...';
            form = new FormData();
            form.append('install', this.package_name);
            fetch(`/api/install-package`, {
                method: 'POST', body: form
            }).then(resp => {
                if (resp.ok) {
                    el.innerText = 'Install';
                    this.package_name = '';
                    this.status_();
                } else {
                    el.innerText = 'Error!';
                }
            })
                .catch(error => {
                    console.log(error);
                })
        },
        install_requirements(el) {
            el.innerText = 'Installing requirements.txt...';
            fetch(`/api/install-requirements`, {})
                .then(resp => {
                    if (resp.ok) {
                        el.innerText = 'Install requirements.txt';
                        this.status_();
                    } else {
                        el.innerText = 'Error!';
                    }
                }).catch(error => {
                console.log(error);
                this.continue_polling = false;
            })
        },
        recreate_venv(el) {
            el.innerText = 'Recreating Virtual Environment...';
            fetch(`/api/recreate-venv`, {})
                .then(resp => {
                    if (resp.ok) {
                        el.innerText = 'Recreate Virtual Environment';
                        this.status_();
                    } else {
                        el.innerText = 'Error!';
                    }
                }).catch(_ => {
                this.continue_polling = false;
            })
        },
        enable_webhook() {
            fetch(`/api/enable-webhook`, {})
                .then(response => response.json()).then(jsond => {
                this.alerts = jsond.alerts;
                if (jsond.success) {
                    this.status_();
                }
            }).catch(error => {
                console.log(error);
            });
        },
        disable_webhook() {
            fetch(`/api/disable-webhook`, {})
                .then(response => response.json()).then(jsond => {
                this.alerts = jsond.alerts;
                if (jsond.success) {
                    this.status_();
                }
            }).catch(error => {
                console.log(error);
            });
        },
        generate_new_secret() {
            fetch(`/api/generate-new-secret`, {})
                .then(response => response.json()).then(jsond => {
                this.alerts = jsond.alerts;
                if (jsond.success) {
                    this.status_();
                }
            }).catch(error => {
                console.log(error);
            });
        }
    }));
});