from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
    DetailView,
    FormView,
    TemplateView,
)
from django.views.generic.base import RedirectView
from .models import *
from .statics import CASE_STATUS_INGEDIEND
from django.urls import reverse_lazy, reverse
from .forms import *
from web.users.auth import auth_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from web.users.statics import (
    BEGELEIDER,
    WONEN,
    PB_FEDERATIE_BEHEERDER,
    WONINGCORPORATIE_MEDEWERKER,
)
from web.forms.statics import FORMS_BY_SLUG, FORMS_SLUG_BY_FEDERATION_TYPE
from web.forms.views import GenericUpdateFormView, GenericCreateFormView
from web.forms.utils import get_sections_fields
import logging
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.template.loader import render_to_string
from web.organizations.models import Federation
from django.http import Http404, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from web.users.auth import user_passes_test
from django.core.paginator import Paginator
from web.timeline.models import Moment
from formtools.wizard.views import SessionWizardView
from django.db.models import Q
from django.db.models.functions import Concat
from django.db.models import TextField
from django.core.exceptions import PermissionDenied
from datetime import datetime
from web.users.utils import *
from web.users.utils import (
    get_zorginstelling_medewerkers_email_list,
    filter_valid_emails,
)
from operator import or_
from django.utils import timezone
from django.http.response import HttpResponse
import mimetypes
import magic
import requests
from django.http import JsonResponse

logger = logging.getLogger(__name__)

PAGE_SIZE = 20


class UserCaseList(UserPassesTestMixin, ListView):
    model = Case
    template_name_suffix = "_list_page"

    def test_func(self):
        return auth_test(self.request.user, [PB_FEDERATIE_BEHEERDER, BEGELEIDER])

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs = super().get_context_data(object_list=object_list, **kwargs)
        object_list = kwargs.pop("object_list")

        search = self.request.GET.get("search")
        if search:
            search_terms = search.split()

            # Initialize an empty queryset to store the filtered results
            filtered_queryset = object_list.none()

            for term in search_terms:
                # Check if the search term is a valid date format
                try:
                    search_date = datetime.strptime(term, "%d-%m-%Y").date()
                except ValueError:
                    search_date = None

                # Create a base filter
                base_filter = (
                    Q(client_first_name__icontains=term)
                    | Q(client_last_name__icontains=term)
                    | Q(emailadres__icontains=term)
                )

                # Apply filters based on the search term
                if search_date:
                    filtered_queryset |= object_list.filter(
                        or_(base_filter, Q(geboortedatum=search_date))
                    )
                else:
                    filtered_queryset |= object_list.filter(base_filter)

            # Remove double items
            object_list = filtered_queryset.distinct()

        # Create the search parameters string
        search_params = f"&search={search}" if search else ""

        # pagination
        paginator = Paginator(object_list, PAGE_SIZE)
        page = self.request.GET.get("page", 1)
        object_list = paginator.get_page(page)
        form = UserCaseForm(self.request.GET)
        kwargs.update(
            {
                "object_list": object_list,
                "form": form,
                "search_params": search_params,
            }
        )
        return kwargs


class CaseListArchive(UserPassesTestMixin, ListView):
    model = Case
    template_name_suffix = "_list_archive"

    def test_func(self):
        return auth_test(self.request.user, WONEN)

    def get_queryset(self):
        return super().get_queryset().filter(delete_request_date__isnull=False)

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs = super().get_context_data(object_list=None, **kwargs)
        object_list = kwargs.pop("object_list")

        search = self.request.GET.get("search")
        if search:
            search_terms = search.split()

            # Initialize an empty queryset to store the filtered results
            filtered_queryset = object_list.none()

            for term in search_terms:
                # Check if the search term is a valid date format
                try:
                    search_date = datetime.strptime(term, "%d-%m-%Y").date()
                except ValueError:
                    search_date = None

                # Create a base filter
                base_filter = (
                    Q(client_first_name__icontains=term)
                    | Q(client_last_name__icontains=term)
                    | Q(emailadres__icontains=term)
                )

                # Apply filters based on the search term
                if search_date:
                    filtered_queryset |= object_list.filter(
                        or_(base_filter, Q(geboortedatum=search_date))
                    )
                else:
                    filtered_queryset |= object_list.filter(base_filter)

            # Remove double items
            object_list = filtered_queryset.distinct()

        # Create the search parameters string
        search_params = f"&search={search}" if search else ""

        paginator = Paginator(object_list, PAGE_SIZE)
        page = self.request.GET.get("page", 1)
        object_list = paginator.get_page(page)
        form = UserCaseForm(self.request.GET)
        kwargs.update(
            {
                "object_list": paginator.get_page(page),
                "form": form,
                "search_params": search_params,
            }
        )
        return kwargs


class UserCaseListAll(UserPassesTestMixin, TemplateView):
    template_name = "cases/case_list_page_wonen.html"

    def test_func(self):
        return auth_test(self.request.user, [WONEN, WONINGCORPORATIE_MEDEWERKER])

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)

        casestatus_list = CaseStatus.objects.all()

        casestatus_list = casestatus_list.filter(
            case__in=Case.objects.by_user(self.request.user).values_list(
                "id", flat=True
            ),
        ).exclude(status=CASE_STATUS_AFGESLOTEN)

        search = self.request.GET.get("search")

        if search:
            # Initialize an empty queryset to store the filtered results
            filtered_queryset = casestatus_list.none()
            search_terms = search.split()
            for term in search_terms:
                # Check if the search term is a valid date format
                try:
                    search_date = datetime.strptime(term, "%d-%m-%Y").date()
                except ValueError:
                    search_date = None

                # Create a base filter
                base_filter = (
                    Q(client_first_name__icontains=term)
                    | Q(client_last_name__icontains=term)
                    | Q(emailadres__icontains=term)
                )

                # Apply filters based on the search term
                if search_date:
                    filtered_queryset |= casestatus_list.filter(
                        case__in=Case.objects.filter(
                            or_(base_filter, Q(geboortedatum=search_date))
                        )
                    )
                else:
                    filtered_queryset |= casestatus_list.filter(
                        case__in=Case.objects.filter(base_filter)
                    )

            # Remove double items
            casestatus_list = filtered_queryset.distinct()

        qs = casestatus_list.exclude(
            status=CASE_STATUS_INGEDIEND,
        )
        qs = qs.order_by("-created")
        qs = qs.annotate(distinct_name=Concat("case", "form", output_field=TextField()))
        qs = qs.order_by("distinct_name", "-created")
        qs = qs.distinct("distinct_name")
        all_objects = casestatus_list.order_by("-created")
        tabs_ids = [s.id for s in qs]
        final_set = all_objects.filter(
            id__in=tabs_ids, case__delete_request_date__isnull=True
        )
        form_slug_list = FORMS_SLUG_BY_FEDERATION_TYPE.get(
            self.request.user.federation.organization.federation_type
        )

        ingediend = casestatus_list
        ingediend = ingediend.order_by("-created")
        ingediend = ingediend.annotate(
            distinct_name=Concat("case", "form", output_field=TextField())
        )
        ingediend = ingediend.order_by("distinct_name", "-created")
        ingediend = ingediend.distinct("distinct_name")
        ingediend_final_set = casestatus_list.order_by("-created")
        ingediend_final_set = ingediend_final_set.filter(
            id__in=[s.id for s in ingediend]
        )
        ingediend_final_set = ingediend_final_set.filter(
            status=CASE_STATUS_INGEDIEND,
            form__in=form_slug_list,
            case__delete_request_date__isnull=True,
        )

        tabs = [
            [cs, CASE_STATUS_DICT.get(cs).get("current")]
            for cs in CASE_STATUS_CHOICES_BY_FEDEATION_TYPE.get(
                self.request.user.federation.organization.federation_type
            )
        ]
        tabs.append([0, "Alle"])
        tabs = [
            {
                "filter": t[0],
                "title": t[1],
                "queryset": (
                    final_set.filter(
                        status=t[0],
                        form__in=form_slug_list,
                    )
                    if t[0]
                    else final_set
                ),
            }
            for t in tabs
        ]

        tabs[0]["queryset"] = ingediend_final_set

        tab_all_ids = [
            s.id for s in ingediend_final_set if s.is_first_of_statustype
        ] + tabs_ids

        tabs[-1]["queryset"] = all_objects.filter(
            id__in=set(tab_all_ids),
            form__in=form_slug_list,
            case__delete_request_date__isnull=True,
        )

        tab_index = self.request.GET.get("f", 0)
        try:
            int(tab_index)
        except ValueError:
            tab_index = "0"
        paginator = Paginator(tabs[int(tab_index)].get("queryset"), PAGE_SIZE)
        page = self.request.GET.get("page", 1)
        object_list = paginator.get_page(page)

        # Create the search parameters string
        search_params = f"&search={search}" if search else ""

        initial_form_data = {"f": str(tab_index)}

        form = UserCaseForm(self.request.GET, initial=initial_form_data)
        kwargs.update(
            {
                "filter_params": f"&f={tab_index}",
                "object_list": object_list,
                "tabs": tabs,
                "search": search,
                "search_params": search_params,
                "form": form,
                "case_archive_list": Case.objects.filter(
                    delete_request_date__isnull=False
                ),
            }
        )
        return kwargs


class CaseDocumentList(UserPassesTestMixin, DetailView):
    model = Case
    template_name_suffix = "_document_list_page"

    def test_func(self):
        return auth_test(self.request.user, [PB_FEDERATIE_BEHEERDER, BEGELEIDER])

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)

    def get_context_data(self, **kwargs):
        kwargs.update({"document_list": Document.objects.filter(case=self.object)})
        return super().get_context_data(**kwargs)


class CaseDetailView(UserPassesTestMixin, DetailView):
    model = Case
    template_name_suffix = "_page"

    def get_context_data(self, **kwargs):
        kwargs.update(
            {
                "moment_list": Moment.objects.all(),
            }
        )
        return super().get_context_data(**kwargs)

    def test_func(self):
        return auth_test(
            self.request.user,
            [WONEN, BEGELEIDER, PB_FEDERATIE_BEHEERDER, WONINGCORPORATIE_MEDEWERKER],
        )

    def get_queryset(self):
        # Check if the user has the WONEN permission
        if auth_test(self.request.user, WONEN):
            # return all cases because Wonen can see the case details through the "Archief".
            return super().get_queryset()
        else:
            return self.model._default_manager.by_user(user=self.request.user)


class CaseVersionDetailView(UserPassesTestMixin, DetailView):
    model = CaseVersion
    template_name_suffix = "_page"

    def get_context_data(self, **kwargs):
        form_config = FORMS_BY_SLUG.get(self.object.version_verbose)

        kwargs.update(
            {
                "form_config": form_config,
            }
        )
        return super().get_context_data(**kwargs)

    def test_func(self):
        return auth_test(
            self.request.user,
            [WONEN, BEGELEIDER, PB_FEDERATIE_BEHEERDER, WONINGCORPORATIE_MEDEWERKER],
        )

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)


class CaseVersionFormDetailView(UserPassesTestMixin, DetailView):
    model = Case
    template_name_suffix = "_form_status"

    def get_context_data(self, **kwargs):
        form_config = FORMS_BY_SLUG.get(self.kwargs.get("form_config_slug"))
        kwargs.update(
            {
                "form_fields": get_sections_fields(form_config.get("sections")),
                "form_config": form_config,
                "user_list": ", ".join(
                    get_zorginstelling_medewerkers_email_list(self.object)
                ),
                "document_list": self.object.document_set.filter(
                    forms__contains=self.kwargs.get("form_config_slug")
                ),
                "status_options": json.dumps(
                    dict(
                        (k, v)
                        for k, v in CASE_STATUS_DICT.items()
                        if k
                        in CASE_STATUS_CHOICES_BY_FEDEATION_TYPE.get(
                            self.request.user.federation.organization.federation_type
                        )
                    )
                ),
            }
        )
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)

    def test_func(self):
        form_slug_list = FORMS_SLUG_BY_FEDERATION_TYPE.get(
            self.request.user.federation.organization.federation_type
        )
        if not self.kwargs.get("form_config_slug") in form_slug_list:
            return False
        return auth_test(self.request.user, [WONEN, WONINGCORPORATIE_MEDEWERKER])


class CaseDetailAllDataView(CaseDetailView):
    template_name_suffix = "_page_all_data"


class CaseCreateView(UserPassesTestMixin, CreateView):
    model = Case
    form_class = CaseBaseForm
    template_name_suffix = "_create_form"

    def get_success_url(self):
        return reverse("case", args=[self.object.id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"title": "Cliënt aanmaken", "mode": "page"})
        return context

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)

    def test_func(self):
        return auth_test(self.request.user, [BEGELEIDER, PB_FEDERATIE_BEHEERDER])

    def form_valid(self, form):
        response = super().form_valid(form)
        case = form.save(commit=False)
        case.saved_by = self.request.user.profile
        case.save()
        self.request.user.profile.cases.add(case)
        messages.add_message(
            self.request,
            messages.INFO,
            "De cliënt '%s' is aangemaakt." % case.client_name,
        )
        return response


class CaseDeleteView(UserPassesTestMixin, DeleteView):
    model = Case
    template_name_suffix = "_delete"
    success_url = reverse_lazy("case_archive")

    def get_success_url(self):
        return reverse("case_list") + "?iframe=%s" % self.success_url

    def test_func(self):
        return auth_test(self.request.user, [WONEN])

    def post(self, request, *args, **kwargs):
        case = self.get_object()
        response = super().delete(request, *args, **kwargs)

        recipient_list = list(
            set(
                get_zorginstelling_medewerkers_email_list(case)
                + get_woningcorporatie_medewerkers_email_list(case)
            )
        )

        current_site = get_current_site(self.request)
        body = render_to_string(
            "cases/mail/case_deleted.txt",
            {
                "case": case,
                "case_url": "https://%s%s"
                % (
                    current_site.domain,
                    reverse(
                        "case",
                        kwargs={
                            "pk": case.id,
                        },
                    ),
                ),
                "user": self.request.user,
            },
        )
        if settings.EMAIL_HOST_USER and recipient_list:
            subject = ("Omslagroute - Cliënt definitief verwijderd",)
            from_email = settings.FROM_EMAIL
            to_emails = recipient_list
            send_mail(subject, body, from_email, to_emails, fail_silently=False)

        messages.add_message(
            self.request,
            messages.INFO,
            "De cliënt '%s' is verwijderd." % case.client_name,
        )

        return response


class CaseDeleteRequestView(UserPassesTestMixin, UpdateView):
    model = Case
    template_name_suffix = "_delete_request"
    success_url = reverse_lazy("cases_by_profile")
    form_class = CaseDeleteRequestForm

    def get_success_url(self):
        return "./?iframe=%s" % (self.success_url,)

    def test_func(self):
        return auth_test(self.request.user, [BEGELEIDER, PB_FEDERATIE_BEHEERDER])

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)

    def form_valid(self, form):
        case = form.save(commit=False)
        case.delete_request_date = timezone.now()
        case.delete_request_by = self.request.user.profile
        case.save()

        recipient_list = list(
            set(
                get_wonen_medewerkers_email_list()
                + get_zorginstelling_medewerkers_email_list(self.object)
                + get_woningcorporatie_medewerkers_email_list(self.object)
            )
        )
        if self.request.user.username in recipient_list:
            recipient_list.remove(self.request.user.username)

        current_site = get_current_site(self.request)
        body = render_to_string(
            "cases/mail/case_delete_request.txt",
            {
                "case": case,
                "case_url": "https://%s%s"
                % (
                    current_site.domain,
                    reverse(
                        "case",
                        kwargs={
                            "pk": case.id,
                        },
                    ),
                ),
                "user": self.request.user,
            },
        )
        if settings.EMAIL_HOST_USER:
            subject = "Omslagroute - Verzoek verwijderen cliënt"
            from_email = settings.FROM_EMAIL
            to_emails = recipient_list
            send_mail(subject, body, from_email, to_emails, fail_silently=False)

        messages.add_message(
            self.request, messages.INFO, "Het verwijder verzoek is verstuurd."
        )
        return super().form_valid(form)


class CaseDeleteRequestRevokeView(UserPassesTestMixin, UpdateView):
    model = Case
    template_name_suffix = "_delete_request_revoke"
    success_url = reverse_lazy("cases_by_profile")
    form_class = CaseDeleteRequestRevokeForm

    def get_success_url(self):
        return "./?iframe=%s" % (self.success_url,)

    def test_func(self):
        return auth_test(self.request.user, [BEGELEIDER, PB_FEDERATIE_BEHEERDER])

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)

    def form_valid(self, form):
        case = form.save(commit=False)
        case.delete_request_date = None
        case.delete_request_message = None
        case.delete_request_by = None
        case.save()

        recipient_list = list(
            set(
                get_wonen_medewerkers_email_list()
                + get_zorginstelling_medewerkers_email_list(self.object)
                + get_woningcorporatie_medewerkers_email_list(self.object)
            )
        )
        if self.request.user.username in recipient_list:
            recipient_list.remove(self.request.user.username)

        current_site = get_current_site(self.request)
        body = render_to_string(
            "cases/mail/case_delete_request_revoke.txt",
            {
                "case": case,
                "case_url": "https://%s%s"
                % (
                    current_site.domain,
                    reverse(
                        "case",
                        kwargs={
                            "pk": case.id,
                        },
                    ),
                ),
                "delete_request_revoke_message": form.cleaned_data.get(
                    "delete_request_revoke_message"
                ),
                "user": self.request.user,
            },
        )
        if settings.EMAIL_HOST_USER:
            subject = "Omslagroute - Verzoek verwijderen cliënt terug gedraaid"
            from_email = settings.FROM_EMAIL
            to_emails = recipient_list
            send_mail(subject, body, from_email, to_emails, fail_silently=False)

        messages.add_message(
            self.request, messages.INFO, "Het verwijder verzoek is teruggedraaid."
        )
        return super().form_valid(form)


class CaseCleanView(UserPassesTestMixin, UpdateView):
    model = Case
    template_name = "cases/case_clean_form.html"
    form_class = CaseCleanForm
    success_url = reverse_lazy("cases_by_profile")

    def get_fields(self):
        form_config = FORMS_BY_SLUG.get(self.kwargs.get("form_config_slug"))
        return (get_sections_fields(form_config.get("sections")),)

    def get_not_empty_fields(self):
        return [
            f
            for f in self.get_fields()[0]
            if hasattr(self.object, f) and getattr(self.object, f)
        ]

    def test_func(self):
        return auth_test(self.request.user, [BEGELEIDER, PB_FEDERATIE_BEHEERDER])

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)

    def get_success_url(self):
        return reverse(
            "update_case",
            kwargs={
                "pk": self.object.id,
                "form_config_slug": self.kwargs.get("form_config_slug"),
            },
        )

    def reset_form(self):
        version = self.object.create_version(self.kwargs.get("form_config_slug"))

        case_status_dict = {
            "form": self.kwargs.get("form_config_slug"),
            "case": self.object,
            "case_version": version,
            "profile": self.request.user.profile,
            "status": CASE_STATUS_AFGESLOTEN,
        }
        case_status = CaseStatus(**case_status_dict)
        case_status.save()

        return True

    def clean_form(self):
        form_config = FORMS_BY_SLUG.get(self.kwargs.get("form_config_slug"))
        form_fields = get_sections_fields(form_config.get("sections", {}))
        for f in form_fields:
            if hasattr(self.object, f):
                setattr(self.object, f, None)
        self.object.save()
        return True

    def form_valid(self, form):
        response = super().form_valid(form)
        form_data = form.cleaned_data
        case_status = self.object.get_status(self.kwargs.get("form_config_slug"))
        if not case_status or case_status in IN_CONCEPT:
            raise Http404()
        if form_data.get("form_continue_options") == "1":
            messages.add_message(
                self.request, messages.INFO, "Je kan verder met de aanvraag."
            )
        elif form_data.get("form_new_options") == "1":
            self.reset_form()
            messages.add_message(
                self.request,
                messages.INFO,
                "Je kan starten met deze nieuwe aanvraag. De vorige aanvraag is afgesloten.",
            )
        elif form_data.get("form_new_options") == "2":
            self.reset_form()
            self.clean_form()
            messages.add_message(
                self.request,
                messages.INFO,
                "Je kan starten met deze nieuwe lege aanvraag. De vorige aanvraag is afgesloten.",
            )
        return response

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs.update(
            {
                "form_config": FORMS_BY_SLUG.get(self.kwargs.get("form_config_slug")),
                "case_status": CaseStatus.objects.filter(
                    case=self.object, form=self.kwargs.get("form_config_slug")
                )
                .order_by("-created")
                .first(),
            }
        )
        return kwargs


class GenericCaseUpdateFormView(UserPassesTestMixin, GenericUpdateFormView):
    model = Case
    template_name = "forms/generic_form.html"
    success_url = reverse_lazy("cases_by_profile")
    form_class = CaseGenericModelForm

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if (
            FORMS_BY_SLUG.get(self.kwargs.get("form_config_slug"))
            .get("options", {})
            .get("addres_required")
            and not self.object.address_complete
        ):
            return redirect(
                "%s%s"
                % (
                    reverse("create_case_address", args=[self.object.id]),
                    "?next=%s"
                    % reverse(
                        "update_case",
                        args=[self.object.id, self.kwargs.get("form_config_slug")],
                    ),
                )
            )
        return response

    def get_initial(self):
        self.initial.update(
            {
                "document_list": Document.objects.filter(
                    case=self.object,
                    forms__contains=self.kwargs.get("form_config_slug"),
                )
            }
        )
        return super().get_initial()

    def test_func(self):
        return auth_test(self.request.user, [BEGELEIDER, PB_FEDERATIE_BEHEERDER])

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)

    def get_success_url(self):
        next = self.request.POST.get("next")
        default_url = reverse(
            "update_case",
            kwargs={
                "pk": self.object.id,
                "form_config_slug": self.kwargs.get("form_config_slug"),
            },
        )
        percentage = self.object.status(
            FORMS_BY_SLUG.get(self.kwargs.get("form_config_slug"), {}).get("sections")
        ).get("percentage")
        if percentage < 100 and next:
            return "%s?control=1" % default_url
        if next:
            return next
        return default_url

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)

        form_config = FORMS_BY_SLUG.get(self.kwargs.get("form_config_slug"))

        kwargs.update(
            {
                "case_versions": self.object.get_history(form_config),
                "case_status_list": CaseStatus.objects.filter(
                    case=self.object, form=self.kwargs.get("form_config_slug")
                ).order_by("-created"),
            }
        )
        return kwargs

    def get_discard_url(self):
        return reverse("case", kwargs={"pk": self.object.id})

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        response = super().form_valid(form)
        form_config_slug = self.kwargs.get("form_config_slug")
        self.object.saved_by = self.request.user.profile
        self.object.saved_form = form_config_slug
        self.object.save()
        document_list = form.cleaned_data.get("document_list")
        for doc in form.fields["document_list"].queryset:
            if doc in document_list and form_config_slug not in doc.forms:
                doc.forms.append(form_config_slug)
            elif doc not in document_list and form_config_slug in doc.forms:
                doc.forms.remove(form_config_slug)
            doc.save()
        messages.add_message(
            self.request, messages.INFO, "Eventuele wijzigingen zijn opgeslagen."
        )
        return response


class GenericCaseCreateFormView(UserPassesTestMixin, GenericCreateFormView):
    model = Case
    template_name = "forms/generic_form.html"
    success_url = reverse_lazy("cases_by_profile")
    form_class = CaseGenericModelForm

    def test_func(self):
        return auth_test(self.request.user, [BEGELEIDER, PB_FEDERATIE_BEHEERDER])

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)

    def get_success_url(self):
        form_config = FORMS_BY_SLUG.get(self.kwargs.get("form_config_slug"), {})
        if not form_config.get("enable_ajax", False):
            return reverse("case", kwargs={"pk": self.object.id})
        return reverse(
            "update_case",
            kwargs={
                "pk": self.object.id,
                "form_config_slug": self.kwargs.get("form_config_slug"),
            },
        )

    def get_discard_url(self):
        return reverse("cases_by_profile")

    def form_valid(self, form):
        response = super().form_valid(form)
        case = form.save(commit=False)
        case.saved_by = self.request.user.profile
        case.save()
        self.request.user.profile.cases.add(case)
        messages.add_message(
            self.request,
            messages.INFO,
            "De cliënt '%s' is aangemaakt." % case.client_name,
        )
        return response


class ValidateCaseView(UserPassesTestMixin, RedirectView):
    model = Case
    permanent = False
    query_string = True

    def test_func(self):
        return auth_test(self.request.user, [BEGELEIDER, PB_FEDERATIE_BEHEERDER])

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)

    def get_redirect_url(self, *args, **kwargs):
        self.object = get_object_or_404(self.model, pk=kwargs["pk"])
        form_config = FORMS_BY_SLUG.get(self.kwargs.get("form_config_slug"))
        redirect_url = reverse(
            "case",
            args=[
                self.object.id,
            ],
        )
        recipient_list = self.request.user.federation.main_email_list
        current_site = get_current_site(self.request)
        body = render_to_string(
            "cases/mail/validate_case.txt",
            {
                "form_name": form_config.get("title"),
                "case_url": "https://%s%s"
                % (
                    current_site.domain,
                    reverse(
                        "update_case",
                        args=[
                            self.object.id,
                            self.kwargs.get("form_config_slug"),
                        ],
                    ),
                ),
                "user": self.request.user,
            },
        )
        if settings.EMAIL_HOST_USER and recipient_list:
            subject = ("Omslagroute - %s controleren" % form_config.get("title"),)
            from_email = settings.FROM_EMAIL
            to_emails = recipient_list
            send_mail(subject, body, from_email, to_emails, fail_silently=False)

            messages.add_message(
                self.request,
                messages.INFO,
                "De aanvraag is ter controle gestuurd naar '%s'."
                % (
                    (
                        self.request.user.federation.name_form_validation_team
                        if self.request.user.federation.name_form_validation_team
                        else self.request.user.federation.name
                    ),
                ),
            )
        return redirect_url


class SendCaseView(UserPassesTestMixin, UpdateView):
    model = Case
    template_name = "cases/send.html"
    form_class = SendCaseForm

    def test_func(self):
        return auth_test(self.request.user, [BEGELEIDER, PB_FEDERATIE_BEHEERDER])

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)

    def get_success_url(self):
        return reverse("case", kwargs={"pk": self.object.id})

    def get_federation(self):
        form_config = FORMS_BY_SLUG.get(self.kwargs.get("form_config_slug"))
        federation_type = form_config.get("federation_type")
        federation = Federation.objects.filter(
            organization__federation_type=federation_type
        ).first()
        if (
            federation_type == FEDERATION_TYPE_WONINGCORPORATIE
            and self.object.woningcorporatie
        ):
            federation = self.object.woningcorporatie
        return federation

    def get_recipient_list(self):
        form_config = FORMS_BY_SLUG.get(self.kwargs.get("form_config_slug"))
        federation_type = form_config.get("federation_type")
        recipient_list = get_zorginstelling_medewerkers_email_list(self.object)
        if federation_type == FEDERATION_TYPE_ADW:
            recipient_list += get_wonen_medewerkers_email_list()
        elif federation_type == FEDERATION_TYPE_WONINGCORPORATIE:
            recipient_list += get_woningcorporatie_medewerkers_email_list(self.object)
        recipient_list = list(set(recipient_list))
        filtered_recipients = filter_valid_emails(recipient_list)
        return filtered_recipients

    def get_context_data(self, **kwargs):
        kwargs.update(self.kwargs)
        form_config = FORMS_BY_SLUG.get(self.kwargs.get("form_config_slug"))
        if not form_config:
            raise Http404
        kwargs.update(form_config)
        federation_type = form_config.get("federation_type")
        federation = self.get_federation()
        recipient_list = self.get_recipient_list()

        kwargs.update(
            {
                "federation_type": federation_type,
                "form_config": form_config,
                "federation": federation,
                "recipient_list": recipient_list,
                "object": self.object,
                "document_list": Document.objects.filter(
                    case=self.object,
                    forms__contains=self.kwargs.get("form_config_slug"),
                ),
            }
        )
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        form_config = FORMS_BY_SLUG.get(self.kwargs.get("form_config_slug"))
        version = self.object.create_version(self.kwargs.get("form_config_slug"))
        case_status_dict = {
            "form": self.kwargs.get("form_config_slug"),
            "case": self.object,
            "case_version": version,
            "profile": self.request.user.profile,
        }
        case_status = CaseStatus(**case_status_dict)
        case_status.save()

        recipient_list = self.get_recipient_list()
        federation = self.get_federation()

        if recipient_list:
            current_site = get_current_site(self.request)
            body = render_to_string(
                "cases/mail/case_link.txt",
                {
                    "form_name": form_config.get("title"),
                    "case_url": "https://%s%s"
                    % (
                        current_site.domain,
                        reverse(
                            "case_version_form",
                            kwargs={
                                "pk": self.object.id,
                                "form_config_slug": self.kwargs.get("form_config_slug"),
                            },
                        ),
                    ),
                    "user": self.request.user,
                },
            )
            if settings.EMAIL_HOST_USER:
                subject = "Omslagroute - %s" % form_config.get("title")
                from_email = settings.FROM_EMAIL
                to_emails = recipient_list
                send_mail(subject, body, from_email, to_emails, fail_silently=False)

            messages.add_message(
                self.request,
                messages.INFO,
                "De aanvraag is ingediend bij en vanaf nu zichtbaar voor medewerkers van '%s'."
                % (federation.name,),
            )
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class CaseInviteUsers(UserPassesTestMixin, SessionWizardView):
    model = Case
    template_name = "cases/case_invite.html"
    form_class = CaseInviteUsersForm
    success_url = reverse_lazy("cases_by_profile")
    instance = None
    form_list = [
        CaseInviteUsersForm,
        CaseInviteUsersConfirmForm,
    ]

    def get_success_url(self):
        return "%s?iframe=true" % reverse("case", kwargs={"pk": self.instance.id})

    def get_all_users(self):
        return (
            User.objects.filter(
                Q(user_type__contains=PB_FEDERATIE_BEHEERDER)
                | Q(user_type__contains=BEGELEIDER),
                profile__isnull=False,
            )
            .exclude(id=self.request.user.id)
            .order_by("federation", "username")
        )

    def get_user_options(self):
        instance = self.model.objects.get(id=self.kwargs.get("pk"))
        return (
            self.get_all_users()
            .filter(
                federation=self.request.user.federation,
            )
            .exclude(
                profile__in=instance.profile_set.all(),
            )
        )

    def get_linked_users(self):
        instance = self.model.objects.get(id=self.kwargs.get("pk"))
        return self.get_all_users().filter(
            profile__in=instance.profile_set.all(),
        )

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step=step)
        self.instance = self.model.objects.get(id=self.kwargs.get("pk"))
        kwargs.update({"queryset": self.get_user_options()})
        return kwargs

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)

    def test_func(self):
        return auth_test(self.request.user, [BEGELEIDER, PB_FEDERATIE_BEHEERDER])

    def get_context_data(self, **kwargs):
        self.instance = self.model.objects.get(id=self.kwargs.get("pk"))
        kwargs.update(
            {
                "linked_users": self.get_linked_users(),
                "unlinked_users": self.get_user_options(),
                "instance": self.instance,
                "selected_users": self.get_all_cleaned_data().get("user_list", []),
            }
        )
        kwargs = super().get_context_data(**kwargs)
        return kwargs

    def done(self, form_list, **kwargs):
        form_data = {}
        for f in form_list:
            form_data.update(f.cleaned_data)

        user_list = form_data.get("user_list", [])
        for user in user_list:
            user.profile.cases.add(self.instance)
        if settings.EMAIL_HOST_USER:

            current_site = get_current_site(self.request)
            for invited in user_list:
                context = {}
                context.update(form_data)
                context.update(
                    {
                        "case": self.instance,
                        "user": self.request.user,
                        "invited": invited,
                        "case_url": "https://%s%s"
                        % (
                            current_site.domain,
                            reverse("case", kwargs={"pk": self.instance.id}),
                        ),
                    }
                )
                body = render_to_string("cases/mail/invite.txt", context)
                subject = "Omslagroute - je bent toegevoegd aan een team"
                from_email = settings.FROM_EMAIL
                to_emails = [invited.username]
                send_mail(subject, body, from_email, to_emails, fail_silently=False)

        messages.add_message(
            self.request,
            messages.INFO,
            "De nieuwe gebruikers hebben een email gekregen van hun uitnodiging.",
        )
        return HttpResponseRedirect(self.get_success_url())


class CaseInviteUsersCrossFederation(UserPassesTestMixin, SessionWizardView):
    model = Case
    template_name = "cases/case_invite_cross_federation.html"
    form_class = CaseInviteUsersCrossFederationForm
    success_url = reverse_lazy("cases_by_profile")
    instance = None
    form_list = [
        CaseInviteUsersCrossFederationForm,
        CaseInviteUsersConfirmForm,
    ]

    def get_success_url(self):
        return "%s?iframe=true" % reverse("case", kwargs={"pk": self.instance.id})

    def get_all_users(self):
        return User.objects.filter(
            profile__isnull=False,
        ).exclude(id=self.request.user.id)

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step=step)
        self.instance = self.model.objects.get(id=self.kwargs.get("pk"))
        kwargs.update({"queryset": []})
        return kwargs

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)

    def test_func(self):
        return auth_test(self.request.user, [BEGELEIDER, PB_FEDERATIE_BEHEERDER])

    def get_context_data(self, **kwargs):
        self.instance = self.model.objects.get(id=self.kwargs.get("pk"))
        kwargs.update(
            {
                "instance": self.instance,  # For the client/case name
            }
        )
        kwargs = super().get_context_data(**kwargs)
        return kwargs

    def done(self, form_list, **kwargs):
        form_data = {}
        for f in form_list:
            form_data.update(f.cleaned_data)

        # Get email input from form
        user_email_cross_federation = form_data.get("user_email_cross_federation")
        queryset = self.get_all_users().filter(email=user_email_cross_federation)
        invited_user = queryset.first()

        # Check if user exists
        if not invited_user:
            messages.add_message(
                self.request,
                messages.ERROR,
                "Er is geen gebruiker met dit e-mailadres gevonden.",
            )
            return HttpResponseRedirect(self.get_success_url())

        # Check if user has role BEGELEIDER or PB_FEDERATIE_BEHEERDER
        if (
            BEGELEIDER not in invited_user.user_type_values
            and PB_FEDERATIE_BEHEERDER not in invited_user.user_type_values
        ):
            messages.add_message(
                self.request,
                messages.ERROR,
                "De persoon met wie u wilt samenwerken is geen persoonlijk begeleider.",
            )
            return HttpResponseRedirect(self.get_success_url())

        # Add client/case to profile
        invited_user.profile.cases.add(self.instance)

        if settings.EMAIL_HOST_USER:
            current_site = get_current_site(self.request)
            context = {}
            context.update(form_data)
            context.update(
                {
                    "case": self.instance,
                    "user": self.request.user,
                    "invited": invited_user,
                    "case_url": "https://%s%s"
                    % (
                        current_site.domain,
                        reverse("case", kwargs={"pk": self.instance.id}),
                    ),
                }
            )
            body = render_to_string("cases/mail/invite.txt", context)
            subject = "Omslagroute - je bent toegevoegd aan een team"
            from_email = settings.FROM_EMAIL
            to_emails = [invited_user.email]
            send_mail(subject, body, from_email, to_emails, fail_silently=False)

        messages.add_message(
            self.request,
            messages.INFO,
            "De gebruiker is toegevoegd en heeft een e-mail gekregen met een uitnodiging.",
        )
        return HttpResponseRedirect(self.get_success_url())


class CaseRemoveInvitedUsers(UserPassesTestMixin, FormView):
    model = Case
    template_name = "cases/case_remove_invited.html"
    form_class = CaseRemoveInvitedUsersForm
    success_url = reverse_lazy("cases_by_profile")

    def get_all_users(self):
        return (
            User.objects.filter(
                Q(user_type__contains=PB_FEDERATIE_BEHEERDER)
                | Q(user_type__contains=BEGELEIDER),
                profile__isnull=False,
            )
            .exclude(id=self.request.user.id)
            .order_by("federation", "username")
        )

    def get_user_options(self):
        instance = self.model.objects.get(id=self.kwargs.get("pk"))
        return self.get_all_users().filter(
            profile__in=instance.profile_set.all(),
        )

    def get_success_url(self):
        return "%s?iframe=true" % reverse("case", kwargs={"pk": self.instance.id})

    def test_func(self):
        return auth_test(self.request.user, [BEGELEIDER, PB_FEDERATIE_BEHEERDER])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.instance = self.model.objects.get(id=self.kwargs.get("pk"))
        if self.instance not in self.model._default_manager.by_user(
            user=self.request.user
        ):
            raise PermissionDenied
        kwargs.update({"queryset": self.get_user_options()})
        return kwargs

    def form_valid(self, form):
        case = self.instance
        for user in form.cleaned_data.get("user_list"):
            # Check if there are other profiles with this case
            profiles_with_case_count = Profile.objects.filter(cases=case).count()
            # If there is just 1 user or less with this case in his profile, do not remove this case (yet).
            # If you delete this case from this profile, there will no longer be a relation between a user and this case.
            # To prevent a floating case, add this case to the current user (Probably PB & Organisatie beheerder).
            if profiles_with_case_count <= 1:
                # Check if the currently logged in user has this case in their profile.
                current_user_cases = self.request.user.profile.cases
                if not current_user_cases.filter(pk=case.pk).exists():
                    current_user_cases.add(case)
            user.profile.cases.remove(self.instance)

        if settings.EMAIL_HOST_USER:

            current_site = get_current_site(self.request)
            for user in form.cleaned_data.get("user_list"):
                context = {}
                context.update(
                    {
                        "case": self.instance,
                        "user": self.request.user,
                        "removed_user": user,
                        "case_url": "https://%s%s"
                        % (
                            current_site.domain,
                            reverse("case", kwargs={"pk": self.instance.id}),
                        ),
                    }
                )
                body = render_to_string("cases/mail/invated_removed.txt", context)
                subject = "Omslagroute - je bent uit een team verwijderd"
                from_email = settings.FROM_EMAIL
                to_emails = [user.username]
                send_mail(subject, body, from_email, to_emails, fail_silently=False)

        messages.add_message(
            self.request,
            messages.INFO,
            "De gebruikers hebben een mail ontvangen van het verbreken van de samenwerking.",
        )
        return super().form_valid(form)


class CaseBaseUpdateView(UserPassesTestMixin, UpdateView):
    model = Case
    form_class = CaseBaseForm
    template_name_suffix = "_create_form"
    success_url = reverse_lazy("cases_by_profile")

    def get_success_url(self):
        return "%s?iframe=true" % reverse("case", args=[self.object.id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"title": "Cliënt aanpassen", "mode": "iframe"})
        return context

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)

    def test_func(self):
        return auth_test(self.request.user, [BEGELEIDER, PB_FEDERATIE_BEHEERDER])

    def form_valid(self, form):
        messages.add_message(
            self.request,
            messages.INFO,
            "De cliënt '%s' is aangepast." % self.object.client_name,
        )
        return super().form_valid(form)


class CaseAddressCreate(UserPassesTestMixin, UpdateView):
    model = Case
    form_class = CaseAddressForm
    template_name_suffix = "_create_address_form"
    success_url = reverse_lazy("home")

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)

    def get_success_url(self):
        if self.request.GET.get("next"):
            return self.request.GET.get("next")
        return "%s?iframe=true" % reverse("case", args=[self.object.id])

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def test_func(self):
        return auth_test(self.request.user, [BEGELEIDER, PB_FEDERATIE_BEHEERDER])

    def form_valid(self, form):
        case = form.save(commit=False)
        case.saved_by = self.request.user.profile
        case.save()
        messages.add_message(self.request, messages.INFO, "Het adres is opgeslagen.")

        self.object.create_version(CASE_VERSION_ADDRESS)
        return HttpResponseRedirect(self.get_success_url())


class CaseAddressUpdate(UserPassesTestMixin, UpdateView):
    model = Case
    form_class = CaseAddressUpdateForm
    template_name_suffix = "_update_address_form"
    success_url = reverse_lazy("home")

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)

    def get_success_url(self):
        return "%s?iframe=true" % reverse("case", args=[self.object.id])

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def test_func(self):
        return auth_test(self.request.user, [BEGELEIDER, PB_FEDERATIE_BEHEERDER])

    def form_valid(self, form):
        case = form.save(commit=False)
        case.adres_wijziging_reden = form.cleaned_data.get("wijziging_reden")
        case.saved_by = self.request.user.profile
        case.save()

        current_site = get_current_site(self.request)
        context = {
            "case": case,
            "user": self.request.user,
            "case_url": "https://%s%s"
            % (current_site.domain, reverse("case", kwargs={"pk": case.id})),
        }
        body = render_to_string("cases/mail/case_address_changed.txt", context)

        recipient_list = list(
            set(
                get_wonen_medewerkers_email_list()
                + get_zorginstelling_medewerkers_email_list(self.object)
                + get_woningcorporatie_medewerkers_email_list(self.object)
            )
        )
        if self.request.user.username in recipient_list:
            recipient_list.remove(self.request.user.username)

        if settings.EMAIL_HOST_USER:
            subject = "Omslagroute - Cliënt adres wijziging"
            from_email = settings.FROM_EMAIL
            to_emails = recipient_list
            send_mail(subject, body, from_email, to_emails, fail_silently=False)

        messages.add_message(self.request, messages.INFO, "Het adres is opgeslagen.")
        self.object.create_version(CASE_VERSION_ADDRESS)
        return HttpResponseRedirect(self.get_success_url())


class DocumentCreate(UserPassesTestMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name_suffix = "_create_form"
    success_url = reverse_lazy("home")

    def get_success_url(self):
        if self.request.POST.get("next"):
            url = "%s%s" % (
                self.request.POST.get("next").split("#")[0],
                "?iframe=true" if self.request.GET.get("open-in-iframe") else "",
            )
            return url
        return ".?iframe=true"

    def test_func(self):
        cases = Case._default_manager.by_user(user=self.request.user)
        self.case = get_object_or_404(Case, id=self.kwargs.get("case_pk"))
        if self.case not in cases:
            return False
        return auth_test(self.request.user, [BEGELEIDER, PB_FEDERATIE_BEHEERDER])

    def get_context_data(self, **kwargs):
        kwargs.update(
            {
                "case": self.case,
            }
        )
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        document = form.save(commit=False)
        document.case = self.case

        messages.add_message(
            self.request,
            messages.INFO,
            "De bijlage '%s' is opgeslagen." % document.name,
        )
        return super().form_valid(form)


class DocumentUpdate(UserPassesTestMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name_suffix = "_create_form"
    success_url = reverse_lazy("home")

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)

    def get_success_url(self):
        return ".?iframe=true"

    def test_func(self):
        cases = Case._default_manager.by_user(user=self.request.user)
        self.case = get_object_or_404(Case, id=self.kwargs.get("case_pk"))
        if self.case not in cases:
            return False
        return auth_test(self.request.user, [BEGELEIDER, PB_FEDERATIE_BEHEERDER])

    def get_context_data(self, **kwargs):
        kwargs.update(
            {
                "case": self.case,
            }
        )
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        document = form.save(commit=False)
        document.case = self.case

        messages.add_message(
            self.request,
            messages.INFO,
            "De bijlage '%s' is opgeslagen." % document.name,
        )
        return super().form_valid(form)


class DocumentDelete(UserPassesTestMixin, DeleteView):
    model = Document
    form_class = DocumentForm
    template_name_suffix = "_delete_form"
    success_url = reverse_lazy("home")

    def get_queryset(self):
        return self.model._default_manager.by_user(user=self.request.user)

    def get_success_url(self):
        return "%s?iframe=true" % reverse(
            "case", kwargs={"pk": self.kwargs.get("case_pk")}
        )

    def test_func(self):
        cases = Case._default_manager.by_user(user=self.request.user)
        self.case = get_object_or_404(Case, id=self.kwargs.get("case_pk"))
        if self.case not in cases:
            return False
        return auth_test(self.request.user, [BEGELEIDER, PB_FEDERATIE_BEHEERDER])

    def get_context_data(self, **kwargs):
        form_status_list = [
            f[0]
            for f in self.case.casestatus_set.all()
            .order_by("form")
            .distinct()
            .values_list("form")
        ]

        kwargs.update(
            {
                "case": self.case,
                "shared_in_forms": [
                    f for f in self.object.forms if f in form_status_list
                ],
            }
        )
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        document_name = self.get_object().name
        response = super().delete(self, request, *args, **kwargs)
        messages.add_message(
            self.request,
            messages.INFO,
            "De bijlage '%s' is verwijderd." % document_name,
        )
        return response


def get_document_for_case(request, case_pk, document_pk):
    """
    Utility function to retrieve and validate the document.
    """
    qs = Case._default_manager.by_user(user=request.user)
    case = qs.filter(pk=case_pk).first()

    if not case:
        raise PermissionDenied

    document = get_object_or_404(Document, id=document_pk)

    # Check permissions
    if any(
        user_type in [WONEN, WONINGCORPORATIE_MEDEWERKER]
        for user_type in request.user.user_type_values
    ):
        form_status_list = [
            f[0]
            for f in case.casestatus_set.all()
            .order_by("form")
            .distinct()
            .values_list("form")
        ]
        shared_in_forms = [f for f in document.forms if f in form_status_list]
        if not shared_in_forms:
            raise PermissionDenied

    if document.case != case:
        raise PermissionDenied

    # Check if file exists in storage
    if not default_storage.exists(
        default_storage.generate_filename(document.uploaded_file.name)
    ):
        raise Http404()

    return document


def serve_document(document, disposition_type):
    """
    Utility function to serve a document with a specified Content-Disposition type.
    """
    with default_storage.open(document.uploaded_file.name, "rb") as file:
        file_data = file.read()
    mime = magic.Magic(mime=True)
    file_mime_type = mime.from_buffer(file_data)
    if file_mime_type not in settings.ALLOWED_FILE_TYPES:
        raise HttpResponseNotAllowed()

    content_type = mimetypes.guess_type(document.uploaded_file.name)[0] or 'application/octet-stream'

    response = HttpResponse(file_data, content_type=content_type)
    response['Content-Disposition'] = f'{disposition_type}; filename="{document.uploaded_file.name}"'

    return response


@user_passes_test(
    auth_test,
    user_type=[WONEN, BEGELEIDER, PB_FEDERATIE_BEHEERDER, WONINGCORPORATIE_MEDEWERKER],
)
def download_document(request, case_pk, document_pk):
    # Retrieve and validate the document
    document = get_document_for_case(request, case_pk, document_pk)

    # Serve the document as an attachment (download)
    return serve_document(document, "attachment")


@user_passes_test(
    auth_test,
    user_type=[WONEN, BEGELEIDER, PB_FEDERATIE_BEHEERDER, WONINGCORPORATIE_MEDEWERKER],
)
def view_document(request, case_pk, document_pk):
    # Retrieve and validate the document
    document = get_document_for_case(request, case_pk, document_pk)

    # Serve the document inline (for viewing)
    return serve_document(document, "inline")


@user_passes_test(
    auth_test,
    user_type=[BEGELEIDER, PB_FEDERATIE_BEHEERDER],
)
def search_adres(request):
    query = request.GET.get("query", "")
    if not query:
        return JsonResponse({"results": []})

    url = "https://api.pdok.nl/bzk/locatieserver/search/v3_1/suggest"
    params = {
        "q": query,
        "fq": "gemeentenaam:(amsterdam) AND (type:adres) AND (adrestype: hoofdadres)",
        "fl": "weergavenaam,nummeraanduiding_id,adresseerbaarobject_id,straatnaam,huisnummer,huisletter,huisnummertoevoeging,postcode,woonplaatsnaam",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("response", {}).get("docs", [])
        return JsonResponse({"results": results})
    except requests.exceptions.RequestException:
        return JsonResponse({"results": []}, status=400)


@user_passes_test(
    auth_test,
    user_type=[BEGELEIDER, PB_FEDERATIE_BEHEERDER],
)
def search_stadsdeel(request):
    nummeraanduiding_id = request.GET.get("nummeraanduidingid", "")
    if not nummeraanduiding_id:
        return JsonResponse({"error": "Missing nummeraanduidingid"}, status=400)

    url = f"https://api.data.amsterdam.nl/v1/benkagg/adresseerbareobjecten/{nummeraanduiding_id}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return JsonResponse(response.json())
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error stadsdeel: {e}")
        return JsonResponse({"error": "Error searching stadsdeel"}, status=400)
