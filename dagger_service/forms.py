# (c) 2013, The MITRE Corporation.  All rights reserved.
# Source code distributed pursuant to license agreement.

from django import forms

from crits.core.user_tools import user_sources, get_user_organization
from crits.core.handlers import get_source_names, collect_objects
from crits.core.class_mapper import class_from_type
from crits.services.handlers import get_config

class DaggerForm(forms.Form):
    rcpts = forms.MultipleChoiceField(required=True,
                                      label="Recipients",
                                      help_text="Recipients",
                                      widget=forms.SelectMultiple)

    def __init__(self, username, item, *args, **kwargs):
        """
        Initialize the form.
        Populates form fields based on context object (item) and its related items.
        The way the form fields are populated ensures that only STIXifyable / CybOXable
        options are provided.
        """
        super(DaggerForm, self).__init__(*args, **kwargs)
        sc = get_config('dagger_service')

        # Avoid options that cause failure: set recipients to intersection of
        # user's sources and the sources that have Dagger feeds configured
        user_srcs = user_sources(username)
        dagger_srcs = [crtfile.split(',')[0] for crtfile in sc['dagger_settings']]
        self.fields['rcpts'].choices = [(n, n) for n in set(user_srcs).intersection(dagger_srcs)]

class DaggerServiceConfigForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'
    hostname = forms.CharField(required=True,
                               label="Hostname",
                               initial='',
                               widget=forms.TextInput(attrs={'data-step': '1', 'data-intro': 'Enter IP of Dagger server'}),
                               help_text="Dagger server hostname.")

    active = forms.BooleanField(required=False,
                               label="Active",
                               initial=False,
                               help_text="Check to activate Dagger service",
                               widget=forms.CheckboxInput(attrs={'data-step': '2', 'data-intro': 'Check if you want to activate Dagger service'}))

    reset = forms.BooleanField(required=False,
                               label="RESET",
                               initial=False,
                               help_text="Reset on submit to 0",
                               widget=forms.CheckboxInput(attrs={'data-step': '3', 'data-intro': 'Check if you want to reset the values to 0 on submit'}))

    update_freq = forms.CharField(required=True,
                              label="Update Frequency (Seconds)",
                              initial='30',
                              widget=forms.TextInput(
                                  attrs={'data-step': '4',
                                         'data-intro': 'How often (seconds) do you want to decay?'}),
                              help_text="How often do you want to decay?")

    dagger_settings = forms.CharField(required=True,
                                label="Configuration",
                                initial='',
                                widget=forms.Textarea(attrs={'cols': 80,
                                                            'rows': 10,
                                                             'data-step': '5',
                                                             'data-intro': 'Here is where you set which feeds/sources you want to '
                                                                           'send to the Dagger server. </br> '
                                                                           '<strong>source</strong> - The name of the MARTI source </br> '
                                                                           '<strong>feed</strong> - The name of the Dagger feed</br> '
                                                                           '<strong>decay</strong> - Decimal of decay rate</br>'
                                                                           'Example(s): </br>{source},{feed},{poll} </br>'
                                                                           'ITAC,ITAC,0.4 (This means that the any incoming ITAC feed'
                                                                           'will update dagger)'}),
                                help_text="Comma delimited list of MARTI"
                                          " source name, Dagger feed name,"
                                          " decay rate")

    thread = forms.BooleanField(widget=forms.HiddenInput(),
                                initial=False,
                                required=False)

    def __init__(self, *args, **kwargs):
        super(DaggerServiceConfigForm, self).__init__(*args, **kwargs)


class UploadStandardsForm(forms.Form):
    """
    Django form for uploading a standards document.
    """

    error_css_class = 'error'
    required_css_class = 'required'
    filedata = forms.FileField()
    source = forms.ChoiceField(required=True)
    reference = forms.CharField(required=False)
    make_event = forms.BooleanField(required=False, label="Create event", initial=True)

    def __init__(self, username, *args, **kwargs):
        super(UploadStandardsForm, self).__init__(*args, **kwargs)
        self.fields['source'].choices = [(c.name,
                                          c.name) for c in get_source_names(True,
                                                                            True,
                                                                            username)]
        self.fields['source'].initial = get_user_organization(username)
