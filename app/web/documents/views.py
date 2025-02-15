from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from .models import *
from django.urls import reverse
from .forms import *
from web.users.auth import auth_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db import transaction
from web.timeline.models import Moment
from django.core.files.storage import default_storage
from web.users.auth import user_passes_test
from django.views.decorators.http import require_http_methods
from web.users.statics import REDACTIE
from django.http import HttpResponse, JsonResponse, Http404
import json


class DocumentList(ListView):
    model = Document
    template_name_suffix = '_list_page'


class DocumentDelete(UserPassesTestMixin, DeleteView):
    model = Document
    template_name_suffix = '_delete_form'
    success_url = reverse_lazy('home')

    def get_success_url(self):
        return '%s?m=%s#processtap-%s' % (
            self.success_url,
            self.request.GET.get('moment_id'),
            self.request.GET.get('moment_id'),
        )

    def test_func(self):
        return auth_test(self.request.user, REDACTIE)

    def post(self, request, *args, **kwargs):
        response = super().delete(self, request, *args, **kwargs)
        messages.add_message(self.request, messages.INFO, "Het document '%s' is verwijderd." % self.object.name)
        return response


class DocumentCreate(UserPassesTestMixin, CreateView):
    model = Document
    fields = ('name', 'document_type')
    template_name_suffix = '_create_form'
    success_url = reverse_lazy('home')

    def test_func(self):
        return auth_test(self.request.user, REDACTIE)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.add_message(self.request, messages.INFO, "Het document '%s' is aangemaakt." % self.object.name)
        return response


class DocumentUpdate(UserPassesTestMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('home')

    def get_success_url(self):
        return '%s?m=%s#processtap-%s' % (
            self.success_url,
            self.request.GET.get('moment_id'),
            self.request.GET.get('moment_id'),
        )

    def test_func(self):
        return auth_test(self.request.user, REDACTIE)

    def form_valid(self, form):
        response = super().form_valid(form)
        for moment in self.object.moment_set.all():
            moment.documents.remove(self.object)
        for moment in form.cleaned_data.get("moment_list"):
            moment.documents.add(self.object)
        messages.add_message(self.request, messages.INFO, "Het document '%s' is aangepast." % self.object.name)

        return response

    def form_invalid(self, form):
        for k, v in form.errors.items():
            for e in v:
                messages.add_message(self.request, messages.ERROR, e)
        return super().form_invalid(form)


class DocumentVersionCreate(UserPassesTestMixin, CreateView):
    model = DocumentVersion
    form_class = DocumentVersionForm
    template_name_suffix = '_create_form'
    success_url = reverse_lazy('home')

    def get_success_url(self):
        return '%s?m=%s#processtap-%s' % (
            self.success_url,
            self.request.GET.get('moment_id'),
            self.request.GET.get('moment_id'),
        )

    def test_func(self):
        return auth_test(self.request.user, REDACTIE)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'document': Document.objects.get(id=self.kwargs.get('document'))
        })
        return super().get_context_data(**kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial = initial.copy()
        initial['document'] = self.kwargs.get('document')
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.add_message(self.request, messages.INFO, "De versie '%s' is aangemaakt." % self.object.uploaded_str)
        return response


class DocumentVersionDelete(UserPassesTestMixin, DeleteView):
    model = DocumentVersion
    template_name_suffix = '_delete_form'
    success_url = reverse_lazy('home')

    def test_func(self):
        return auth_test(self.request.user, REDACTIE)


class DocumentVersionFormSetCreate(UserPassesTestMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name_suffix = '_and_docversion_create_form'
    success_url = reverse_lazy('home')

    def test_func(self):
        return auth_test(self.request.user, REDACTIE)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['documentversionformset'] = DocumentVersionFormSet(self.request.POST, self.request.FILES)
        else:
            data['documentversionformset'] = DocumentVersionFormSet()
        data.update({
            'moment_id': self.kwargs.get('moment_id'),
        })
        return data

    def form_invalid(self, form):
        respond = super().form_invalid(form)
        for k, v in form.errors.items():
            for e in v:
                messages.add_message(self.request, messages.ERROR, e)
        return respond

    def form_valid(self, form):
        context = self.get_context_data()
        documentversionformset = context['documentversionformset']
        with transaction.atomic():
            if documentversionformset.is_valid():
                self.object = form.save()
                documentversionformset.instance = self.object
                documentversionformset.save()
            else:
                return super().form_invalid(form)

        messages.add_message(self.request, messages.INFO, "Het document '%s' is aangemaakt" % self.object.name)
        return super().form_valid(form)


class CreateDocumentAddToMoment(DocumentVersionFormSetCreate):
    def get_success_url(self):
        return '%s#processtap-%s' % (
            self.success_url,
            self.kwargs.get('moment_id')
        )

    def get_initial(self):
        initial = super().get_initial()
        initial = initial.copy()
        get_object_or_404(Moment, pk=self.kwargs.get('moment_id'))
        initial['moment_id'] = self.kwargs.get('moment_id')
        return initial

    def form_valid(self, form):
        valid = super().form_valid(form)
        moment_id = self.kwargs.get('moment_id')
        moment = Moment.objects.get(id=moment_id) if Moment.objects.filter(id=moment_id).count() else None
        if moment:
            with transaction.atomic():
                moment.documents.add(self.object)
        messages.add_message(self.request, messages.INFO, "Het aangemaakte document is toegevoegd aan de processtap '%s'" % moment.name)
        return valid


def download_documentversion(request, id):
    documentversion = get_object_or_404(DocumentVersion, id=id)
    file_name = documentversion.uploaded_file.name
    if not default_storage.exists(default_storage.generate_filename(documentversion.uploaded_file.name)):
        raise Http404()
    with default_storage.open(file_name, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


@require_http_methods(["POST"])
@user_passes_test(auth_test, user_type=REDACTIE)
def document_name_exists(request):
    data = json.loads(request.body)
    status_code = 200
    if data.get('id'):
        get_object_or_404(Document, id=data.get('id'))
    if not data.get('name'):
        out = False
    else:
        existing_names = Document.objects.get_by_name(name=data.get('name'))
        if data.get('id'):
            existing_names = existing_names.exclude(id=data.get('id'))
        out = bool(existing_names)
        if existing_names:
            out = reverse('add_document_version_to_document', kwargs={'document': existing_names[0].id})

    return JsonResponse({'message': out}, status=status_code)
