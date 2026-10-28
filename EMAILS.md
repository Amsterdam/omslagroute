# E-mails

Overzicht van alle momenten waarop de Omslagroute een e-mail verstuurt, per type ontvanger.

E-mails worden alleen verstuurd als `EMAIL_HOST_USER` is ingesteld. Lokaal worden ze opgevangen door Mailpit (zie de [README](README.md#e-mail-mailpit)).

## Persoonlijk begeleider (zorginstelling)

Ontvangers (`get_zorginstelling_medewerkers_email_list` in `app/web/users/utils.py`):
- alle actieve begeleiders die aan de cliënt gekoppeld zijn, en
- het standaard e-mailadres van de federaties van alle gebruikers die aan de cliënt gekoppeld zijn.

| Gebeurtenis | Uitgevoerd door | Onderwerp | Code |
|---|---|---|---|
| Aanvraag ter controle gestuurd | Begeleider / PB & Organisatie beheerder | Omslagroute - {formulier} controleren | `ValidateCaseView` |
| Aanvraag ingediend (alle formulieren) | Begeleider / PB & Organisatie beheerder | Omslagroute - {formulier} | `SendCaseView` |
| Status van een aanvraag gewijzigd (goedgekeurd, afgekeurd, in behandeling, …) | Wonen / Woningcorporatie medewerker | Omslagroute - {formulier}, status: {status} | `CaseStatusUpdateViewSet` |
| Adres van de cliënt gewijzigd | Begeleider / PB & Organisatie beheerder | Omslagroute - Cliënt adres wijziging | `CaseAddressUpdate` |
| Verzoek om cliënt te verwijderen | Begeleider / PB & Organisatie beheerder | Omslagroute - Verzoek verwijderen cliënt | `CaseDeleteRequestView` |
| Verzoek om cliënt te verwijderen teruggedraaid | Begeleider / PB & Organisatie beheerder | Omslagroute - Verzoek verwijderen cliënt terug gedraaid | `CaseDeleteRequestRevokeView` |
| Cliënt definitief verwijderd | Wonen | Omslagroute - Cliënt definitief verwijderd | `CaseDeleteView` |
| Toegevoegd aan het team van een cliënt | Begeleider / PB & Organisatie beheerder | Omslagroute - je bent toegevoegd aan een team | `CaseInviteUsers`, `CaseInviteUsersCrossFederation` |
| Verwijderd uit het team van een cliënt | Begeleider / PB & Organisatie beheerder | Omslagroute - je bent uit een team verwijderd | `CaseRemoveInvitedUsers` |

Bijzonderheden:
- *Aanvraag ter controle gestuurd* gaat alleen naar het standaard e-mailadres van de eigen federatie (de controle afdeling), niet naar de gekoppelde begeleiders.
- *Toegevoegd aan* en *verwijderd uit een team* gaan alleen naar de betreffende gebruiker zelf.

## Wonen (gemeente)

Ontvangers (`get_wonen_medewerkers_email_list` in `app/web/users/utils.py`):
1. het standaard e-mailadres van de federatie Wonen (ADW), of
2. als dat niet is ingesteld: alle Wonen medewerkers.

| Gebeurtenis | Uitgevoerd door | Onderwerp | Code |
|---|---|---|---|
| Aanvraag ingediend: *Aanvraag Urgentie onder voorwaarden* of *Aanvraag Voordracht omklap* | Begeleider / PB & Organisatie beheerder | Omslagroute - {formulier} | `SendCaseView` |
| Adres van de cliënt gewijzigd | Begeleider / PB & Organisatie beheerder | Omslagroute - Cliënt adres wijziging | `CaseAddressUpdate` |
| Verzoek om cliënt te verwijderen | Begeleider / PB & Organisatie beheerder | Omslagroute - Verzoek verwijderen cliënt | `CaseDeleteRequestView` |
| Verzoek om cliënt te verwijderen teruggedraaid | Begeleider / PB & Organisatie beheerder | Omslagroute - Verzoek verwijderen cliënt terug gedraaid | `CaseDeleteRequestRevokeView` |

## Woningcorporatie

Alleen als er bij de cliënt een woningcorporatie is ingevuld.

Ontvangers (`get_woningcorporatie_medewerkers_email_list` in `app/web/users/utils.py`), in deze volgorde:
1. de e-mailadressen die bij de woningcorporatie zijn ingesteld voor het stadsdeel van de cliënt (`adres_stadsdeel`);
2. als er geen stadsdeel bekend is of daarvoor geen e-mailadres is ingesteld: het standaard e-mailadres van de woningcorporatie;
3. als dat ook niet is ingesteld: alle medewerkers van de woningcorporatie.

| Gebeurtenis | Uitgevoerd door | Onderwerp | Code |
|---|---|---|---|
| Aanvraag ingediend: *Evaluatie wonen*, *Match met passende woning* of *Kennismaking woningcorporatie* | Begeleider / PB & Organisatie beheerder | Omslagroute - {formulier} | `SendCaseView` |
| Adres van de cliënt gewijzigd | Begeleider / PB & Organisatie beheerder | Omslagroute - Cliënt adres wijziging | `CaseAddressUpdate` |
| Verzoek om cliënt te verwijderen | Begeleider / PB & Organisatie beheerder | Omslagroute - Verzoek verwijderen cliënt | `CaseDeleteRequestView` |
| Verzoek om cliënt te verwijderen teruggedraaid | Begeleider / PB & Organisatie beheerder | Omslagroute - Verzoek verwijderen cliënt terug gedraaid | `CaseDeleteRequestRevokeView` |
| Cliënt definitief verwijderd | Wonen | Omslagroute - Cliënt definitief verwijderd | `CaseDeleteView` |

Het stadsdeel van de cliënt wordt bij het opslaan van het adres server-side bepaald op basis van het gekozen adres (`AddressStadsdeelMixin` in `app/web/cases/forms.py`). Bij een adreswijziging wordt de mail verstuurd naar het stadsdeel van het nieuwe adres.

## Algemeen

- Bij een adreswijziging, een verzoek om te verwijderen en het terugdraaien daarvan krijgt de gebruiker die de actie uitvoert zelf geen e-mail.
- De e-mails van de cliënt staan in de views in `app/web/cases/views.py` en `app/web/cases/viewsets.py`, de teksten in `app/web/cases/templates/cases/mail/`.

## Overige e-mails

| Gebeurtenis | Ontvanger | Onderwerp | Code |
|---|---|---|---|
| Account aangemaakt door een beheerder | De nieuwe gebruiker | Omslagroute - je account is aangemaakt | `UserCreationView`, `UserCreationFederationView` |
| Nieuwe gebruiker logt voor het eerst in via Keycloak | Federatie beheerders van de federatie, anders alle beheerders | Omslagroute - gebruiker aangemaakt | `app/web/users/auth.py` |
| Feedback verstuurd | Adressen in de instelling `FEEDBACK_RECIPIENT_LIST` | Omslagroute - feedback | `app/web/feedback/views.py` |
| Testmail via `/admin/sendmail?mailadres=…` | Opgegeven adres | Omslagroute - mail | `SendMailView` |
