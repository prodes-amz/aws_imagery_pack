import itertools
import re
import os
import logging

import aws_search
import aws_download
import aws_utils as utils
import settings

from sentinelsat import geojson_to_wkt


def search_and_download(ranges):
    """
    :param ranges:
    :return:
    """
    aois_path = settings.DATASET_PATH + 'aoi/'
    aois_list = list(map(lambda file: os.path.join(aois_path, file), [f for f in os.listdir(aois_path) if re.search(r'.*\.(shp|kml|csv|geojson)$', f)]))
    logging.info(">> {} AOIs (in .geojson format) found!".format(len(aois_list)))
    for range in ranges:
        for aoi in aois_list:
            logging.info(">> Range date: {} to {} - AOI: {}".format(range[0], range[1], aoi))

            if os.path.isfile(aoi):
                bbox_geojson = utils.read_shape_file(aoi).geometry.__geo_interface__
                is_valid_aoi = utils.check_aoi(bbox_geojson)

                if is_valid_aoi is not True:
                    logging.info(">>>> Skipping AOI {}!".format(aoi))
                    continue

                bbox_wkt = geojson_to_wkt(bbox_geojson)
                scene_list = aws_search.s1_full_text_search(bbox_wkt, range)

                if len(scene_list) != 0:
                    logging.info(">>>>>> {} images found!".format(len(scene_list)))

                    if len(scene_list) > settings.SENTINEL_1_PARAMS['images_limit']:
                        logging.warning(
                            ">>>>>> There is a limit of {} images per AOI ({}) and range dates {}. Thus, only "
                            "{} from {} will be used!".format(settings.SENTINEL_1_PARAMS['images_limit'], aoi,
                                                              range, settings.SENTINEL_1_PARAMS['images_limit'],
                                                              len(scene_list)))
                        scene_list = dict(itertools.islice(scene_list.items(),
                                                           settings.SENTINEL_1_PARAMS['images_limit']))

                else:
                    logging.info(">>>>>> 0 images found!")
                    continue

                aws_download.prepare_requests_to_download(scene_list, range, aoi)
