document.addEventListener('alpine:init', () => {
    Alpine.data('global', () => (
        {
            model_login_t1: '',
            model_login_t2: '',

            git_app_status: 'Stopped',
            git_app_status_style: 'u-styled-red',
            show_destroy_git: false,
            packages: {},
            show_settings_token: false,
            scroll_to_bottom(el) {
                el.scrollTop = el.scrollHeight;
            },
            start_app() {

            },
            restart_app() {

            },
            stop_app() {

            },
            manual_pull() {

            },
            get_packages() {

            }
        }
    ));
});