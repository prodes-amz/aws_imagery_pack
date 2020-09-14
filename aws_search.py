import requests
import logging

import settings


def check_status_code(response):
    """
    :param response:
    :return:
    """

    if response.status_code == 404:
        raise Exception('openSearchS2SAFE API not found: {}'.format(response.status_code))
        return {}

    if response.status_code == 503:
        raise Exception('openSearchS2SAFE API is currently unavailable: {}'.format(response.status_code))
        return {}

    if not response.status_code // 100 == 2:
        raise Exception('openSearchS2SAFE API returned unexpected response: {}:'.format(response.status_code))
        return {}

    return response


# TODO: adapt routines to sentinel-2 search crawler
# def s2_full_text_search(bbox, range_date):

def s1_full_text_search(bbox, range_date):
    """
    Retrieve Sentinel Images from Copernicus.
    api_hub options:
      'https://scihub.copernicus.eu/apihub/' for fast access to recently acquired imagery in the API HUB rolling archive
      'https://scihub.copernicus.eu/dhus/' for slower access to the full archive of all acquired imagery
    :param bbox: Area of interest
    :param range_date: Tuple containing range date (start and end)
    :return:
    """
    scenes = {}
    count_results = 0
    limit = int(100000)
    totres = 1000000

    plain_text_pol = " ".join(str(i) for i in settings.SENTINEL_1_PARAMS['polarisationmode'])

    query = settings.BASE_QUERY
    query += 'platformname:{}'.format(settings.SENTINEL_1_PARAMS['platformname'])
    query += ' AND beginposition:[{}T00:00:00.000Z TO {}T23:59:59:999Z]'.format(range_date[0], range_date[1])
    query += ' AND polarisationmode:{}'.format(plain_text_pol)
    query += ' AND sensoroperationalmode:{}'.format(settings.SENTINEL_1_PARAMS['sensoroperationalmode'])
    query += ' AND producttype:{}'.format(settings.SENTINEL_1_PARAMS['producttype'])
    query += ' AND footprint:"Intersects({})"'.format(bbox)

    logging.info(">>>> Searching in {} rows [pagination]...".format(100))

    while count_results < min(limit, totres) and totres != 0:
        rows = min(100, limit - len(scenes), totres)
        first = count_results
        pquery = query + '&rows={}&start={}'.format(rows, first)

        try:
            r = requests.get(pquery, auth=(settings.USER_SENTINEL_HUB, settings.PASS_SENTINEL_HUB), verify=True)
            r = check_status_code(r)

            r_dict = r.json()
            if 'entry' in r_dict['feed']:
                if not isinstance(r_dict['feed']['entry'], list):
                    r_dict['feed']['entry'] = [r_dict['feed']['entry']]
                for result in r_dict['feed']['entry']:
                    count_results += 1
                    identifier = result['title']
                    type_product = identifier.split('_')[1]

                    scenes[identifier] = {}
                    scenes[identifier]['pathrow'] = identifier.split('_')[-2][1:]
                    scenes[identifier]['sceneid'] = identifier
                    scenes[identifier]['type'] = type_product

                    for data in result['date']:
                        if str(data['name']) == 'beginposition':
                            scenes[identifier]['date'] = str(data['content'])[0:10]

                    for data in result['str']:
                        if str(data['name']) == 'size':
                            scenes[identifier]['size'] = data['content']
                        if str(data['name']) == 'footprint':
                            scenes[identifier]['footprint'] = data['content']
                        if str(data['name']) == 'tileid':
                            scenes[identifier]['tileid'] = data['content']

                    scenes[identifier]['link'] = result['link'][0]['href']
                    scenes[identifier]['icon'] = result['link'][2]['href']
            else:
                totres = 0

        except requests.exceptions.RequestException as exc:
            raise Exception(">>>>>> RequestException: {} - {}".format(r.status_code, exc))
            return {}

    return scenes
