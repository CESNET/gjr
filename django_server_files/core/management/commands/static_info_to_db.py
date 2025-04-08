import random
from django.core.management.base import BaseCommand
from core.models import Pulsar

# TODO take from conf file data, log with logger

class Command(BaseCommand):
    help = 'Generates pulsar objects in the database'

    def handle(self, *args, **options):
        # add_random_pulsars()
        add_galaxy_server("usegalaxy.eu")
        add_galaxy(galaxy_eu_pulsars_real, 'usegalaxy.eu')
        # add_galaxy(galaxy_eu_pulsars, 'usegalaxy.eu')
        # add_galaxy(galaxy_cz_pulsars, 'usegalaxy.cz')
        # add_galaxy(galaxy_uk_pulsars, 'usegalaxy.uk')
        # add_galaxy(galaxy_se_pulsars, 'usegalaxy.se')
        # add_galaxy(galaxy_lv_pulsars, 'usegalaxy.lv')
        # add_galaxy(galaxy_au_pulsars, 'usegalaxy.au')
        # add_galaxy(galaxy_org_pulsars, 'usegalaxy.org')
        # add_galaxy(galaxy_fr_pulsars, 'usegalaxy.fr')
        # add_galaxy(galaxy_sp_pulsars, 'usegalaxy.sp')

def add_galaxy_server(galaxy_name):
    Galaxy.objects.create(
            name="usegalaxy.eu",
            latitude=48.012669109891426,
            longitude=7.835061597283835
        )

def add_random_pulsars():
    NUM_PULSARS_TO_GENERATE = 5
    for _ in range(NUM_PULSARS_TO_GENERATE):
        Pulsar.objects.create(
            name="pulsar",
            galaxy="usegalaxy.eu",
            latitude=random.uniform(40,60),
            longitude=random.uniform(0,15),
            queued_jobs=random.randint(0, 150),
            running_jobs=random.randint(0, 150),
            failed_jobs=random.randint(0, 150)
        )
    print(f"{Pulsar.objects.count()} random pulsars now in the database")

def add_galaxy(pulsars, galaxy):
    for pulsar in pulsars:
        Pulsar.objects.create(
            name=pulsar[0],
            galaxy=galaxy,
            latitude=pulsar[1],
            longitude=pulsar[2],
            queued_jobs=0,
            running_jobs=0,
            failed_jobs=0
        )
    print(f"{Pulsar.objects.count()} pulsars is in database, {galaxy} and its pulsars now in the database")

"""
{ name: 'usegalaxy.eu', coordinates: [48.9731131, 9.3016003], color: get_rand_color() },
        // { name: 'usegalaxy.org', coordinates: [43.000000, -75.000000], color: get_rand_color() },
        // { name: 'usegalaxy.au', coordinates: [-33.865143, 151.209900], color: get_rand_color() },
        { name: 'usegalaxy.cz', coordinates: [50.2117769, 15.3615611], color: get_rand_color() },
        { name: 'usegalaxy.uk', coordinates: [51.5188083, 0.1403647], color: get_rand_color() },
        { name: 'usegalaxy.se', coordinates: [59.8583539, 17.6291306], color: get_rand_color() },
        { name: 'usegalaxy.sp', coordinates: [40.616775, -3.703790], color: get_rand_color() },
        { name: 'usegalaxy.fr', coordinates: [48.6107856, 1.6836897], color: get_rand_color() },
        { name: 'usegalaxy.lv', coordinates: [56.9479739, 24.0932114], color: get_rand_color() }
"""

galaxy_eu_pulsars_real = [
    # eu pbs
    ("eu_pbs", 48.012669109891426, 7.835061597283835), # posunout o kousek doprava nahoru nad pulsar +1 +1
    # Freiburg - Mira's pulsar
    ("pulsar_mira_tpv", 48.1731131, 8.9016003),
    # Freiburg - Snajay's pulsar
    ("pulsar_sanjay_tpv", 48.1731131, 9),
    # Rennes - GenOuest bioinformatics
    ("pulsar_fr01_tpv", 49.2204433, 3.9920847),
    # Bari - RECAS
    ("pulsar_it_tpv", 41.9028, 12.4964),
    # Bari - RECAS 2
    ("pulsar_it02_tpv", 42, 12.4964),
    # Bari - INFN
    ("pulsar_it03_tpv", 41.1198900, 16.8570750),
    # Brussel - VIB
    ("pulsar_be_tpv", 50.8476, 4.3572),
    # Prague - MetaCentrum
    ("pulsar_cz01_tpv", 50.0755, 14.4378),
    ("pulsar_cz02_tpv", 50.09902989683802, 14.38859386931844),
    # pulsar_egi01_tpv
    # Bratislava - IISAS
    ("pulsar_sk01_tpv", 48.148598, 17.107748),
    # Barcelona - BSC-CNS
    ("pulsar_bsc01_tpv", 40.416775, -3.703790),
    # Ankara - TUBITAK ULAKBIM
    ("pulsar_tubitak01_tpv", 39.2233947, 28.7209361),
    # Krakow - Cyfronet
    ("pulsar_cyf01_tpv", 52.237049, 21.017532),
    # Herakilon-Crete - HCMR
    ("pulsar_hcmr01_tpv", 35.3369294, 25.1281525),
    # Greek FAIR-Ease
    ("pulsar_greek_tpv", 38.0217778, 23.7427561)
]

galaxy_cz_pulsars = [
    ("cz_pbs", 50.2117769, 15.3615611), # posunout o kousek doprava nahoru nad pulsar +1 +1
    ("pulsar_brno", 49.148598, 16.107748),
    ("pulsar_praha", 50.2755, 14.8378)
]

galaxy_eu_pulsars = [
    # eu pbs
    ("eu_pbs", 48.9731131, 9.3016003), # posunout o kousek doprava nahoru nad pulsar +1 +1
    # Freiburg - Mira's pulsar
    ("pulsar_mira_tpv", 48.1731131, 8.9016003),
    # Freiburg - Snajay's pulsar
    ("pulsar_sanjay_tpv", 48.1731131, 9),
    # Rennes - GenOuest bioinformatics
    ("pulsar_fr01_tpv", 49.2204433, 3.9920847),
    # Bari - RECAS
    ("pulsar_it_tpv", 41.9028, 12.4964),
    # Bari - RECAS 2
    ("pulsar_it02_tpv", 42, 12.4964),
    # Bari - INFN
    ("pulsar_it03_tpv", 41.1198900, 16.8570750),
    # Brussel - VIB
    ("pulsar_be_tpv", 50.8476, 4.3572),
    # Prague - MetaCentrum
    ("pulsar_cz01_tpv", 50.0755, 14.4378),
    ("pulsar_cz02_tpv", 50.1755, 14.5378),
    # pulsar_egi01_tpv
    # Bratislava - IISAS
    ("pulsar_sk01_tpv", 48.148598, 17.107748),
    # Barcelona - BSC-CNS
    ("pulsar_bsc01_tpv", 40.416775, -3.703790),
    # Ankara - TUBITAK ULAKBIM
    ("pulsar_tubitak01_tpv", 39.2233947, 28.7209361),
    # Krakow - Cyfronet
    ("pulsar_cyf01_tpv", 52.237049, 21.017532),
    # Herakilon-Crete - HCMR
    ("pulsar_hcmr01_tpv", 35.3369294, 25.1281525),
    # Greek FAIR-Ease
    ("pulsar_greek_tpv", 38.0217778, 23.7427561)
]

galaxy_uk_pulsars = [
    ("pulsar_london", 51.4836325, 0.1676136),
    ("pulsar_oxford", 51.7700753, -1.2992056),
    ("pulsar_dublin", 53.3985861, -6.2430531),
    ("pulsar_glasgow", 55.9081400, -4.2435414)
]

galaxy_lv_pulsars = [
    ("pulsar_riga", 56.9529361, 24.1231578),
    ("pulsar_tallin", 59.4692431, 24.7603647),
    ("pulsar_vilnius", 54.6886222, 25.2657358),
    ("pulsar_tartu", 58.4093600, 26.7159311)
]

galaxy_se_pulsars = [
    ("pulsar_oslo", 59.9072789, 10.6978647),
    ("pulsar_uppsala", 59.8797247, 17.6192517),
    ("pulsar_stockholm", 59.3462364, 18.0696911),
    ("pulsar_trondheim", 63.4324758, 10.3353161),
    ("pulsar_kobenhavn", 55.6796211, 12.4886364)
]

galaxy_org_pulsars = [
    ("pulsar_newyork", 40.6125247, -74.0396839),
    ("pulsar_toronto", 43.8014614, -79.3131214),
    ("pulsar_phoenix", 33.5764478, -112.1402700),
    ("pulsar_oregon", 45.4555900, -122.7476506),
    ("pulsar_berkeley", 37.8672108, -122.2787789),
    ("pulsar_yale", 41.3909219, -73.0915975),
    ("pulsar_harvard", 42.3714486, -71.1245489)
]

galaxy_au_pulsars = [
    ("pulsar_sydney", -33.7812708, 150.9918761),
    ("pulsar_melbourne", -37.8909764, 145.1617197),
    ("pulsar_adelaide", -34.7573064, 138.7039417),
    ("pulsar_brisbane", -27.4545069, 152.9668675)
]

galaxy_fr_pulsars = [
    ("pulsar_rennes", 48.1140083, -1.6768606),
    ("pulsar_marseille", 43.2843767, 5.3434031),
    ("pulsar_bordeaux", 44.8122131, -0.6221731)
]

galaxy_sp_pulsars = [
    ("pulsar_barcelona", 41.3883211, 2.1353953),
    ("pulsar_sevilla", 37.4172611, -5.9944875),
    ("pulsar_santander", 43.4879736, -3.8191944)
]
