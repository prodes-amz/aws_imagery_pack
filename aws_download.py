import os
import sys
import logging
import boto3
import botocore
import settings
import aws_utils as utils

from re import findall

sys.setrecursionlimit(1500)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)


def build_filename_format_convention(content, item_safe, path_item, prefix_1, prefix_2):
    """
    :param content:
    :param item_safe:
    :param path_item:
    :param prefix_1:
    :param prefix_2:
    :return path_item_output:
    """
    filename = os.path.basename(content['Key'])
    polarization_index_sorted = {'vv': 1, 'vh': 2, 'hh': 1, 'hv': 2}

    if item_safe is 'annotation':
        polarization = findall("(?:vv|vh|hh|hv)", filename)
        file_type = findall("(?:calibration|noise)", filename)

        if len(file_type) != 0:
            prefix_as_convention_aux = file_type[0] + "-" + prefix_1 + polarization[0] + prefix_2 + \
                                       str(polarization_index_sorted[polarization[0]]).zfill(3) + ".xml"
        else:
            prefix_as_convention_aux = prefix_1 + polarization[0] + prefix_2 + \
                                       str(polarization_index_sorted[polarization[0]]).zfill(3) + ".xml"

        path_item_output = path_item + "/" + prefix_as_convention_aux

    elif item_safe is 'measurement':
        polarization = findall("(?:vv|vh|hh|hv)", filename)
        prefix_as_convention_aux = prefix_1 + polarization[0] + prefix_2 + \
                                   str(polarization_index_sorted[polarization[0]]).zfill(3) + ".tiff"
        path_item_output = path_item + "/" + prefix_as_convention_aux
    else:
        path_item_output = path_item

    return path_item_output


def get_path_item(absolute_path, item, item_safe):
    """
    :param absolute_path:
    :param item:
    :param item_safe:
    :return:
    """
    path_item = absolute_path + "/" + item['item_name'] + ".SAFE" + "/" + item_safe
    utils.check_dir_exist(path_item)

    return path_item


def get_prefix_and_sufix_filename(item):
    """
    :param item:
    :return:
    """
    prefix_as_convention_1 = item['mission_identifier'] + "-" + item['mode'] + "-" + item['product_type'] + "-"
    prefix_as_convention_2 = "-" + item['start_date'] + "-" + item['stop_date'] + "-" + \
                             item['absolute_orbit'] + "-" + item['mission_data_take'] + "-"
    prefix_as_convention_1 = prefix_as_convention_1.lower()
    prefix_as_convention_2 = prefix_as_convention_2.lower()

    return prefix_as_convention_1, prefix_as_convention_2


def build_measurement_request(response, path_item, item, item_safe):
    """
    :param response:
    :param path_item:
    :param item:
    :param item_safe:
    :return:
    """
    command_list = []

    prefix_1, prefix_2 = get_prefix_and_sufix_filename(item)

    if len(response['Contents']) >= 1:
        for i, content in enumerate(response['Contents']):
            path_item_output = build_filename_format_convention(content, item_safe,
                                                                path_item, prefix_1, prefix_2)
            s3_command_aux = "aws s3 cp s3://" + settings.SENTINEL_1_PARAMS['bucket'] + "/" + content['Key'] + " " + \
                             path_item_output + " --request-payer requester"
            command_list.append(s3_command_aux)

    return command_list


def build_annotation_request(response, path_item, item, item_safe):
    """
    :param response:
    :param path_item:
    :param item:
    :param item_safe:
    :return command_list:
    """
    command_list = []

    prefix_1, prefix_2 = get_prefix_and_sufix_filename(item)

    for i, content in enumerate(response['Contents']):
        path_item_output = build_filename_format_convention(content, item_safe, path_item, prefix_1, prefix_2)
        s3_command_aux = "aws s3 cp s3://" + settings.SENTINEL_1_PARAMS['bucket'] + "/" + content['Key'] + \
                         " " + path_item_output + " --request-payer requester"
        command_list.append(s3_command_aux)

    for common_prefix in response['CommonPrefixes']:
        common_prefix_basename = common_prefix['Prefix'][0:-1].split('/')[-1]
        path_item_aux = path_item + "/" + common_prefix_basename
        utils.check_dir_exist(path_item_aux)

        prefix = item['s3_link'] + item_safe + '/' + common_prefix_basename + '/'
        subitem_response = check_response_content(common_prefix_basename, prefix)

        if len(subitem_response['Contents']) >= 1:
            for i, content in enumerate(subitem_response['Contents']):
                path_item_output = build_filename_format_convention(content, item_safe,
                                                                    path_item_aux, prefix_1, prefix_2)
                s3_command_cal = "aws s3 cp s3://" + settings.SENTINEL_1_PARAMS['bucket'] + "/" + content['Key'] + \
                                 " " + path_item_output + " --request-payer requester"
                command_list.append(s3_command_cal)

    return command_list


def build_safe_folder_command_itens(response, item, item_safe, absolute_path):
    """
    :param response:
    :param item:
    :param item_safe:
    :param absolute_path:
    :return:
    """
    command_list = None

    if item_safe is 'manifest':
        path_item = absolute_path + "/" + item['item_name'] + ".SAFE" + "/"
        utils.check_dir_exist(path_item)
        command_list = ["aws s3 cp s3://" + settings.SENTINEL_1_PARAMS['bucket'] + "/" + response['Prefix'][0:-1] + \
                       ".safe " + path_item + "manifest.safe --request-payer requester"]
    elif item_safe in ['measurement', 'support']:
        path_item = get_path_item(absolute_path, item, item_safe)
        command_list = build_measurement_request(response, path_item, item, item_safe)

    elif item_safe in ['annotation', 'preview']:
        path_item = get_path_item(absolute_path, item, item_safe)
        command_list = build_annotation_request(response, path_item, item, item_safe)
    else:
        logging.info(">>>>>> Item {} is empty! Skipped!".format(item_safe))

    return command_list


def check_response_content(item_safe, prefix):
    """
    :param item_safe:
    :param prefix:
    :return:
    """
    client = boto3.Session().client('s3')
    response = client.list_objects(Bucket=settings.SENTINEL_1_PARAMS['bucket'], Prefix=prefix,
                                   RequestPayer='requester', Delimiter='/')

    try:
        if 'Prefix' not in response:
            logging.warning(">>>>>> Prefix key is not in the response object of {}!".format(item_safe))
            return None

        if 'Contents' not in response and item_safe is not 'manifest':
            logging.warning(">>>>>> Contents key is not in the response object of {}!".format(item_safe))
            return None

        if item_safe is 'annotation' or item_safe is 'preview':
            if 'CommonPrefixes' not in response:
                logging.warning(">>>>>> CommonPrefixes key is not in the response object of {}!".format(item_safe))
                return None

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            logging.warning(">>>>>>>> The object does not exist: {}".format(e))
        else:
            raise

    return response


def s1_copy_file_aws_s3_to_personal_bucket(item, absolute_path):
    """
    Source: https://aws.amazon.com/premiumsupport/knowledge-center/s3-large-transfer-between-buckets/
    SAFE format: https://earth.esa.int/web/sentinel/user-guides/sentinel-1-sar/data-formats/sar-formats
    :param item: Item (image) full-metadata
    :param absolute_path:
    :return:
    """
    path_item = absolute_path + "/" + item['item_name'] + ".SAFE"

    safe = {'measurement': {}, 'manifest': {}, 'annotation': {}, 'preview': {}, 'support': {}}
    s3_copy_command = []

    if not os.path.isdir(path_item):
        for item_safe in safe:
            prefix = item['s3_link'] + item_safe + '/'
            response = check_response_content(item_safe, prefix)

            if response is None:
                s3_copy_command.append(None)
            else:
                s3_command = build_safe_folder_command_itens(response, item, item_safe, absolute_path)
                s3_copy_command.extend(s3_command)

        if None not in s3_copy_command:
            flat_list = utils.flatten_list(s3_copy_command)
            for item in flat_list:
                os.system(item)

            compress_file = path_item.replace(".SAFE", "") + ".zip"
            utils.make_archive(path_item, compress_file)
            utils.flush_unnecessary_folders(path_item)

        else:
            logging.warning(">>>>>> One or more itens for SAFE folder {} is broken. Thus, "
                            "none of the other wont be downloaded!".format(prefix))
    else:
        logging.info(">>>>>> SAFE folder {} already exist. Skipping!".format(item['item_name']))


def parser_s3_image_link(item_name):
    """
    Source: https://sentinel.esa.int/web/sentinel/user-guides/sentinel-1-sar/naming-conventions
    :param item_name: Item name, according to the link above
    :return: Parsed s3 link dictionary
    """
    parsed_link = {}
    splited_terms = item_name.split('_')

    parsed_link['item_name'] = item_name
    parsed_link['mission_identifier'] = splited_terms[0]
    parsed_link['mode'] = splited_terms[1]
    parsed_link['product_type'] = splited_terms[2][0:3]
    parsed_link['start_date'] = splited_terms[4]
    parsed_link['stop_date'] = splited_terms[5]
    parsed_link['absolute_orbit'] = splited_terms[6]
    parsed_link['mission_data_take'] = splited_terms[7]
    parsed_link['year'] = parsed_link['start_date'][0:4]
    parsed_link['month'] = int(parsed_link['start_date'][4:6])
    parsed_link['day'] = int(parsed_link['start_date'][6:8])

    if len(splited_terms[2]) == 3 and splited_terms[3] == '':
        product_class_and_polarization = splited_terms[4]
    else:
        product_class_and_polarization = splited_terms[3]

    parsed_link['processing_level'] = product_class_and_polarization[0:1]
    parsed_link['product_class'] = product_class_and_polarization[1:2]
    parsed_link['polarization'] = product_class_and_polarization[2:]

    if parsed_link['mode'] != '' and parsed_link['product_type'] != '' and parsed_link['polarization'] != '':
        parsed_link['s3_link'] = parsed_link['product_type'] + '/' + parsed_link['year'] + \
                                 '/' + str(parsed_link['month']) + '/' + str(parsed_link['day']) + '/' + \
                                 parsed_link['mode'] + '/' + parsed_link['polarization'] + '/' + item_name + '/'

    return parsed_link


def prepare_requests_to_download(scene_list, range_date, aoi):
    """
    :param scene_list: Metadata of each item found in AWS servers
    :param range_date:
    :param aoi:
    :return:
    """
    logging.info(">> Copying the {} repository content from {} to {}...".format(len(scene_list),
                                                                                settings.SENTINEL_1_PARAMS['bucket'],
                                                                                settings.LOCAL_TMP_BUCKET))

    range_name = range_date[0] + "_" + range_date[1]
    aoi_name = os.path.basename(aoi).split('.')[0]
    absolute_path = settings.LOCAL_TMP_BUCKET + range_name + "/" + aoi_name + "/original"

    for i, item in enumerate(scene_list):
        parsed_link = parser_s3_image_link(item)

        logging.info(">>>> Copying item {}. {}...".format(i+1, item))
        s1_copy_file_aws_s3_to_personal_bucket(parsed_link, absolute_path)

