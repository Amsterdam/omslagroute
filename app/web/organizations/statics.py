FEDERATION_TYPE_ADW = 1
FEDERATION_TYPE_ZORGINSTELLING = 2
FEDERATION_TYPE_WONINGCORPORATIE = 3

FEDERATION_TYPE_CHOICES = (
    (FEDERATION_TYPE_ADW, 'ADW',),
    (FEDERATION_TYPE_ZORGINSTELLING, 'Zorginstelling',),
    (FEDERATION_TYPE_WONINGCORPORATIE, 'Woningcorporatie',),
)

STADSDELEN = [
    'Centrum',
    'Nieuw-West',
    'Noord',
    'Oost',
    'Weesp',
    'West',
    'Westpoort',
    'Zuid',
    'Zuidoost',
]

STADSDEEL_CHOICES = tuple((stadsdeel, stadsdeel) for stadsdeel in STADSDELEN)