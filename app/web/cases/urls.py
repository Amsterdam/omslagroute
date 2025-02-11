from .views import *
from django.urls import path


urlpatterns = [
    path('', UserCaseListAll.as_view(), name='case_list'),
    path('mijn-clienten/', UserCaseList.as_view(), name='cases_by_profile'),
    path('archief/', CaseListArchive.as_view(), name='case_archive'),
    path('<int:pk>/', CaseDetailView.as_view(), name='case'),
    path('versie/<int:pk>/', CaseVersionDetailView.as_view(), name='case_version'),

    # invite
    path('<int:pk>/uitnodigen/', CaseInviteUsers.as_view(), name='case_invite_users'),
    path('<int:pk>/uitnodigen-organisatie/', CaseInviteUsersCrossFederation.as_view(), name='case_invite_users_federation'),
    path('<int:pk>/uitgenodigingen-intrekken/', CaseRemoveInvitedUsers.as_view(), name='case_remove_invited_users'),

    path('<int:pk>/alle-velden/', CaseDetailAllDataView.as_view(), name='case_all_data'),
    path('verwijder-verzoek/<int:pk>/', CaseDeleteRequestView.as_view(), name='delete_request_case'),
    path('verwijder-verzoek-ongedaan-gemaakt/<int:pk>/', CaseDeleteRequestRevokeView.as_view(), name='delete_request_revoke_case'),
    path('verwijder/<int:pk>/', CaseDeleteView.as_view(), name='delete_case'),
    path('nieuw/basis-gegevens/', CaseCreateView.as_view(), name='create_case'),
    path('<int:pk>/basis-gegevens/', CaseBaseUpdateView.as_view(), name='update_case_base'),
    path('<int:pk>/adres-aanmaken/', CaseAddressCreate.as_view(), name='create_case_address'),
    path('<int:pk>/adres-aanpassen/', CaseAddressUpdate.as_view(), name='update_case_address'),
    path('<int:pk>/<str:form_config_slug>/nieuw/', CaseCleanView.as_view(), name='update_case_clean'),
    path('<int:pk>/<str:form_config_slug>/', GenericCaseUpdateFormView.as_view(), name='update_case'),
    path('<int:pk>/<str:form_config_slug>/controleren/', ValidateCaseView.as_view(), name='validate_case'),
    path('<int:pk>/<str:form_config_slug>/verstuur', SendCaseView.as_view(), name='send_case'),

    path('<int:pk>/form/<str:form_config_slug>/', CaseVersionFormDetailView.as_view(), name='case_version_form'),

    path('<int:pk>/bijlage-lijst', CaseDocumentList.as_view(), name='case_document_list'),
    path('<int:case_pk>/nieuwe-bijlage', DocumentCreate.as_view(), name='add_case_document'),
    path('<int:case_pk>/wijzig-bijlage/<int:pk>/', DocumentUpdate.as_view(), name='update_case_document'),
    path('<int:case_pk>/verwijder-bijlage/<int:pk>/', DocumentDelete.as_view(), name='delete_case_document'),

    path('<int:case_pk>/download-bijlage/<int:document_pk>', download_document, name='download_case_document'),
    path('<int:case_pk>/bekijk-bijlage/<int:document_pk>', view_document, name='view_case_document'),

    path("zoek-adres/", search_adres, name="zoek-adres"),
    path("zoek-stadsdeel/", search_stadsdeel, name="zoek-stadsdeel"),
]
