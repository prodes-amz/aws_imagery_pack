from decouple import config

USER_SENTINEL_HUB = config('USER_SENTINEL_HUB', default='rodolfolotte')
PASS_SENTINEL_HUB = config('PASS_SENTINEL_HUB', default='kdh&@!639klsd')
DATASET_PATH = config('DATASET_PATH', default='/data/prodes/')
LOCAL_TMP_BUCKET = config('LOCAL_TMP_BUCKET', default='/data/prodes/tmp/')

BASE_QUERY = 'https://scihub.copernicus.eu/apihub/search?format=json&q='
MAIN_FLOW_SEARCH_IMAGES = True

SENTINEL_1_PARAMS = {
    'bucket': 'sentinel-s1-l1c',
    'platformname': 'Sentinel-1',
    'producttype': 'GRD',
    'sensoroperationalmode': 'IW',
    'polarisationmode': ['VV', 'VH'],
    'images_limit': 10
}

SENTINEL_2_PARAMS = {
    'bucket': 'sentinel-s2-l1c',
    'platformname': 'Sentinel-2',
    'cloud_tolerance': 100,
    'images_limit': 10
}
