from django.views.generic import TemplateView, FormView, UpdateView, CreateView
from django.urls import reverse_lazy
from .forms import *
from django.contrib import messages
import json
from json import JSONEncoder
import datetime
from .statics import FORMS_BY_SLUG
from django.http import Http404
from web.organizations.models import Federation
from web.organizations.statics import FEDERATION_TYPE_WONINGCORPORATIE


class DateTimeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


class FormListView(TemplateView):
    template_name = 'forms/form_list_page.html'


class GenericFormView(FormView):
    template_name = 'forms/generic_form.html'
    success_url = reverse_lazy('form_list')
    form_class = GenericForm

    def get_discard_url(self):
        return reverse_lazy('form_list')

    def get_initial(self):
        self.initial.update(json.loads(self.request.session.get('client_data', '{}')))
        return super().get_initial()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'sections': self.kwargs.get('sections'),
        })
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session['client_data'] = json.dumps(form.cleaned_data, cls=DateTimeEncoder)
        messages.add_message(self.request, messages.INFO, "Het formulier is ontvangen")
        return response

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs.update(
            self.kwargs
        )
        kwargs.update({
            'discard_url': self.get_discard_url(),
        })
        return kwargs


class GenericUpdateFormView(UpdateView):
    template_name = 'forms/generic_form.html'
    success_url = reverse_lazy('form_list')
    form_class = GenericModelForm

    def get_discard_url(self):
        return reverse_lazy('form_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        form_config = FORMS_BY_SLUG.get(self.kwargs.get('form_config_slug'))
        if not form_config:
            raise Http404
        kwargs.update({
            'form_config': form_config,
            'path': self.request.path,
        })
        return kwargs

    def get_context_data(self, **kwargs):

        kwargs = super().get_context_data(**kwargs)
        form_config = FORMS_BY_SLUG.get(self.kwargs.get('form_config_slug'), {})
        kwargs.update(
            self.kwargs
        )
        kwargs.update(form_config)

        federation_type = form_config.get('federation_type')
        federation = Federation.objects.filter(
            organization__federation_type=federation_type,
        ).first()

        case = kwargs.get("case")
        woningcorporatie = getattr(case, 'woningcorporatie', None) if case else None

        # If federation type is woningcorporatie, set the woningcorporatie which is connected to the case address.
        if federation_type == FEDERATION_TYPE_WONINGCORPORATIE and woningcorporatie:
            federation = woningcorporatie

        kwargs.update({
            'discard_url': self.get_discard_url(),
            'federation': federation
        })
        return kwargs


class GenericCreateFormView(CreateView):
    template_name = 'forms/generic_form.html'
    success_url = reverse_lazy('form_list')
    form_class = GenericModelForm

    def get_discard_url(self):
        return reverse_lazy('form_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        form_config = FORMS_BY_SLUG.get(self.kwargs.get('form_config_slug'))
        if not form_config:
            raise Http404
        kwargs.update({
            'form_config': form_config,
            'path': self.request.path,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        form_config = FORMS_BY_SLUG.get(self.kwargs.get('form_config_slug'), {})
        kwargs.update(
            self.kwargs
        )
        kwargs.update(form_config)
        self.kwargs.update(form_config)
        kwargs.update({
            'discard_url': self.get_discard_url(),
            'title': form_config.get('title_new'),
        })
        return kwargs
