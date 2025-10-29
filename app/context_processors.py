from .theme_helper import get_site_config, set_site_config, get_site_configs, update_site_config

def theme_context(request):
    return  get_site_config()