from django import forms
from .models import *
from django.db.models import Q
from web.forms.forms import GenericModelForm
from web.forms.widgets import (
    RadioSelect,
    CheckboxSelectMultipleDocument,
    CheckboxSelectMultiple,
    CheckboxSelectMultipleUser,
)
from .statics import GESLACHT
from web.forms.statics import FORMS_CHOICES
from django.utils.translation import gettext_lazy as _
from web.forms.fields import MultiSelectFormField
from web.users.models import User
from web.users.statics import BEGELEIDER, PB_FEDERATIE_BEHEERDER
from web.organizations.statics import FEDERATION_TYPE_WONINGCORPORATIE


class UserCaseForm(forms.ModelForm):
    f = forms.CharField(label=("f"), required=False, widget=forms.HiddenInput())
    search = forms.CharField(label=_("Zoeken"), required=False)

    class Meta:
        model = Case
        exclude = []


class CaseForm(forms.ModelForm):
    geslacht = forms.ChoiceField(
        label=_("Geslacht"), required=True, widget=RadioSelect(), choices=GESLACHT
    )
    search = forms.CharField(label=_("Zoeken"), required=False)

    class Meta:
        model = Case
        exclude = []


class CaseInviteUsersForm(forms.Form):
    user_list = forms.ModelMultipleChoiceField(
        label=_("Met wie van je organisatie wil je samenwerken aan deze cliënt?"),
        help_text=_(
            "Selecteer één of meerdere collega’s. Wanneer je kiest voor samenwerken met een collega kan deze:<ul><li>basisgegevens en aanvraagformulieren bekijken en bewerken</li><li>bijlagen downloaden en  toevoegen</li><li>formulieren verzenden naar afdeling Wonen Gemeente Amsterdam</li></ul>"
        ),
        queryset=User.objects.filter(
            Q(user_type__contains=BEGELEIDER)
            | Q(user_type__contains=PB_FEDERATIE_BEHEERDER)
        ),
        widget=CheckboxSelectMultiple(
            attrs={"class": "u-list-style-none scroll-list-container"}
        ),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop("queryset")
        super().__init__(*args, **kwargs)
        self.fields["user_list"].queryset = self.queryset

    class Meta:
        model = Case
        fields = []


class CaseInviteUsersConfirmForm(forms.Form):
    message = forms.CharField(
        label=_("Bericht (optioneel)"),
        help_text=_(
            "Als je een bericht wil meesturen met in de bevestings e-mail, dan kun je dat hier doen."
        ),
        widget=forms.Textarea(
            attrs={
                "rows": 4,
            }
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop("queryset")
        super().__init__(*args, **kwargs)

    class Meta:
        model = Case
        fields = []


class CaseInviteUsersCrossFederationForm(forms.Form):
    user_email_cross_federation = forms.EmailField(
        label=_("Met wie van een andere organisatie wil je samenwerken aan deze cliënt?"),
        help_text=_(
            "Voer het e-mailadres in van de persoon met wie je wil samenwerken. <br/><br/> Wanneer je kiest voor samenwerken met een collega kan deze:<ul><li>basisgegevens en aanvraagformulieren bekijken en bewerken</li><li>bijlagen downloaden en  toevoegen</li><li>formulieren verzenden naar afdeling Wonen Gemeente Amsterdam</li></ul>"
        ),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop("queryset")
        super().__init__(*args, **kwargs)

    class Meta:
        model = Case
        fields = []


class CaseRemoveInvitedUsersForm(forms.Form):
    user_list = forms.ModelMultipleChoiceField(
        label=_(
            "Met wie van je organisatie wil je níet meer samenwerken aan deze cliënt?"
        ),
        help_text=_(
            "Wanneer je de samenwerking beëindigt kunnen deze collega’s géén:<ul><li>basisgegevens en aanvraagformulieren bekijken en bewerken</li><li>bijlagen downloaden en  toevoegen</li><li>formulieren verzenden naar afdeling Wonen Gemeente Amsterdam</li>"
        ),
        queryset=User.objects.filter(
            Q(user_type__contains=BEGELEIDER)
            | Q(user_type__contains=PB_FEDERATIE_BEHEERDER)
        ),
        widget=CheckboxSelectMultipleUser(
            attrs={"class": "u-list-style-none scroll-list-container"}
        ),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop("queryset")
        super().__init__(*args, **kwargs)
        self.fields["user_list"].queryset = self.queryset

    class Meta:
        fields = []


class CaseGenericModelForm(GenericModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["document_list"] = forms.ModelMultipleChoiceField(
            label=_(
                "Vink de bijlagen aan die je bij de aanvraag mee wilt sturen."
            ),
            queryset=Document.objects.filter(case=kwargs.get("instance")),
            widget=CheckboxSelectMultipleDocument(
                attrs={
                    "instance_id": self.instance.id,
                    "instance": self.instance,
                    "path": self.path,
                    "form_config_slug": self.form_config_slug,
                }
            ),
            required=False,
        )

    class Meta:
        model = Case
        exclude = []


class SendCaseForm(forms.ModelForm):

    to_email = forms.EmailField(
        label=_("E-mailadres van de afdeling wonen van de gemeente Amsterdam"),
        required=False,
    )

    class Meta:
        model = Case
        fields = []


class CaseBaseForm(forms.ModelForm):

    class Meta:
        model = Case
        fields = [
            "client_first_name",
            "client_last_name",
            "geboortedatum",
            "emailadres",
            "partner_check",
            "partner_naam",
            "partner_geboortedatum",
            "partner_emailadres",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client_first_name"].required = True
        self.fields["client_last_name"].required = True
        self.fields["geboortedatum"].required = True
        self.fields["partner_naam"].widget.attrs.update({"class": "partner_form_elem"})
        self.fields["partner_geboortedatum"].widget.attrs.update(
            {"class": "partner_form_elem"}
        )
        self.fields["partner_emailadres"].widget.attrs.update(
            {"class": "partner_form_elem"}
        )


class CaseCleanForm(forms.ModelForm):
    form_continue_options = forms.ChoiceField(
        label=_("Wat wil je doen?"),
        widget=RadioSelect(),
        initial=1,
        choices=(
            (1, "Bekijken of bewerken huidige formulier"),
            (2, "Huidige formulier afsluiten + nieuw formulier"),
        ),
    )
    form_new_options = forms.ChoiceField(
        label=_("Wat voor nieuw formulier?"),
        widget=RadioSelect(),
        initial=1,
        choices=(
            (1, "Informatie huidige formulier gebruiken in de nieuwe"),
            (2, "Leeg nieuw formulier"),
        ),
    )

    class Meta:
        model = Case
        fields = []


class CaseAddressForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = [
            "adres_straatnaam",
            "adres_huisnummer",
            "adres_toevoeging",
            "adres_postcode",
            "adres_plaatsnaam",
            "adres_stadsdeel",
            "woningcorporatie",
            "woningcorporatie_medewerker",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["adres_straatnaam"].required = True
        self.fields["adres_huisnummer"].required = True
        self.fields["adres_postcode"].required = True
        self.fields["adres_plaatsnaam"].required = True
        self.fields["woningcorporatie"].required = True
        self.fields["adres_stadsdeel"].required = True

        self.fields["adres_straatnaam"].widget.attrs["hidden"] = True
        self.fields["adres_huisnummer"].widget.attrs["hidden"] = True
        self.fields["adres_toevoeging"].widget.attrs["hidden"] = True
        self.fields["adres_postcode"].widget.attrs["hidden"] = True
        self.fields["adres_plaatsnaam"].widget.attrs["hidden"] = True
        self.fields["adres_stadsdeel"].widget.attrs["hidden"] = True

        self.fields["woningcorporatie"].queryset = self.fields[
            "woningcorporatie"
        ].queryset.filter(
            organization__federation_type=FEDERATION_TYPE_WONINGCORPORATIE,
        )


class CaseAddressUpdateForm(forms.ModelForm):
    wijziging_reden = forms.CharField(
        label=_("Waarom wijzig je dit adres?"),
        widget=forms.Textarea(
            attrs={
                "rows": 4,
            }
        ),
        required=True,
    )

    class Meta:
        model = Case
        fields = [
            "adres_straatnaam",
            "adres_huisnummer",
            "adres_toevoeging",
            "adres_postcode",
            "adres_plaatsnaam",
            "adres_stadsdeel",
            "woningcorporatie",
            "woningcorporatie_medewerker",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["adres_straatnaam"].required = True
        self.fields["adres_huisnummer"].required = True
        self.fields["adres_postcode"].required = True
        self.fields["adres_plaatsnaam"].required = True
        self.fields["adres_stadsdeel"].required = True
        self.fields["woningcorporatie"].required = True

        self.fields["adres_straatnaam"].widget.attrs["hidden"] = True
        self.fields["adres_huisnummer"].widget.attrs["hidden"] = True
        self.fields["adres_toevoeging"].widget.attrs["hidden"] = True
        self.fields["adres_postcode"].widget.attrs["hidden"] = True
        self.fields["adres_plaatsnaam"].widget.attrs["hidden"] = True
        self.fields["adres_stadsdeel"].widget.attrs["hidden"] = True

        self.fields["woningcorporatie"].queryset = self.fields[
            "woningcorporatie"
        ].queryset.filter(
            organization__federation_type=FEDERATION_TYPE_WONINGCORPORATIE,
        )


class DocumentForm(forms.ModelForm):
    forms = MultiSelectFormField(
        label=_("Formulieren"),
        help_text=_(
            "Als er formulieren zijn waar deze bijlage aan toegevoegd moet worden, dan kun je die hier aanvinken"
        ),
        choices=FORMS_CHOICES,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        self.fields["uploaded_file"].label = "Selecteer een bestand"
        self.fields["name"].label = "Titel van de bijlage"

    class Meta:
        model = Document
        exclude = ("case",)
        widgets = {
            "uploaded_file": forms.FileInput(
                attrs={
                    "id": "file-upload",
                    "accept": "image/*,.doc,.docx,.xls,.xlsx,.pdf",
                    "required": "required",
                }
            ),
        }


class CaseDeleteRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        self.fields["delete_request_message"].label = (
            "Waarom wil je deze cliënt verwijderen?"
        )

    class Meta:
        model = Case
        fields = [
            "delete_request_message",
        ]
        widgets = {
            "delete_request_message": forms.Textarea(
                attrs={
                    "rows": 4,
                }
            )
        }


class CaseDeleteRequestRevokeForm(forms.ModelForm):
    delete_request_revoke_message = forms.CharField(
        label=_("Waarom wil je deze cliënt weer terugzetten? *"),
        widget=forms.Textarea(
            attrs={
                "rows": 4,
            }
        ),
        required=False,
    )

    class Meta:
        model = Case
        fields = []
