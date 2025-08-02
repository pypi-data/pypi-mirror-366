from netbox.plugins import PluginConfig


class PhoneManagementConfig(PluginConfig):
    name = "phone_management_plugin"
    verbose_name = "Phone Management Plugin"
    description = "An NetBox plugin to manage phone numbers and sims"
    version = "0.0.1"
    author = "Mattijs Vanhaverbeke"
    author_email = "author@example.com"
    base_url = "phone_management_plugin"
    required_settings = []
    default_settings = {

    }
    def ready(self):
        from . import signals

        super().ready()


config = PhoneManagementConfig