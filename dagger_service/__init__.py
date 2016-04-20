import logging
import os

from django.template.loader import render_to_string

from crits.core.handlers import does_source_exist
from crits.services.core import Service, ServiceConfigError
from crits.services.handlers import get_config as new_config, update_config

from . import forms
from . import handlers
from . import auto
import time

logger = logging.getLogger(__name__)

class DaggerClient(Service):
    """
    Send Dagger message to Dagger server.
    """

    name = "dagger_service"
    version = "2.0.2"
    supported_types = []
    required_fields = []
    description = "Send Dagger messages to a Dagger server."

    auto.start_dagger()

    @staticmethod
    def parse_config(config):
        # When editing a config we are given a string.
        # When validating an existing config it will be a list.
        # Convert it to a list of strings.
        certfiles = config.get('dagger_settings', [])
        if isinstance(certfiles, basestring):
            config['dagger_settings'] = [cf for cf in certfiles.split('\r\n')]

        hostname = config.get("hostname", "").strip()
        reset = config.get("reset","")
        update_freq = config.get("update_freq", "").strip()
        errors = []
        if not hostname:
            errors.append("You must specify a Dagger Server.")
        if not update_freq:
            errors.append("You must specify an update frequency.")
        for crtfile in config['dagger_settings']:
            try:
                (marti_name, dagger_name, decay) = crtfile.split(',')
            except ValueError as e:
                errors.append("You must specify a source, feed name, "
                              " true/false polling, and true/false inbox for each source. (%s)" % str(e))
                break
            marti_name.strip()
            if reset:
                handlers.init_values(marti_name,dagger_name,decay,0)
            else:
                handlers.init_values(marti_name,dagger_name,decay)

            if not does_source_exist(marti_name):
                errors.append("Invalid source: %s" % marti_name)
        if errors:
            raise ServiceConfigError("\n".join(errors))

    @staticmethod
    def get_config_details(config):
        display_config = {}

        # Rename keys so they render nice.
        fields = forms.DaggerServiceConfigForm().fields
        for name, field in fields.iteritems():
            # Convert sigfiles to newline separated strings
            if name == 'dagger_settings':
                display_config[field.label] = '\r\n'.join(config[name])
            else:
                display_config[field.label] = config[name]

        return display_config

    @staticmethod
    def get_config(existing_config):
        # Generate default config from form and initial values.
        config = {}
        fields = forms.DaggerServiceConfigForm().fields
        for name, field in fields.iteritems():
            config[name] = field.initial

        # If there is a config in the database, use values from that.
        if existing_config:
            for key, value in existing_config.iteritems():
                config[key] = value
        return config

    @classmethod
    def generate_config_form(self, config):
        # Convert sigfiles to newline separated strings
        config['dagger_settings'] = '\r\n'.join(config['dagger_settings'])
        html = render_to_string('services_config_form.html',
                                {'name': self.name,
                                 'form': forms.DaggerServiceConfigForm(initial=config),
                                 'config_error': None})
        form = forms.DaggerServiceConfigForm
        return form, html

    def run(self, obj, config):
        pass # Not available via old-style services.
