import os
import logging
import shutil
import datetime


def evaluate_range_dates_args(ranges_args):
    """
    :param ranges_args: Sequence of dates in string format
    :return:
    """
    ranges = []
    range_count = 1

    for i in range(0, len(ranges_args)-1, 2):
        date_aux_1 = datetime.datetime.strptime(ranges_args[i], '%Y-%m-%d')
        date_aux_2 = datetime.datetime.strptime(ranges_args[i+1], '%Y-%m-%d')

        if date_aux_1 > date_aux_2:
            logging.info(">>>> {}o. pair range {} is incorrect. Stop date "
                         "is bigger than start! Skipped!".format(range_count,
                                                                 ranges_args[i] + " to " + ranges_args[i+1]))
        else:
            ranges.append((ranges_args[i], ranges_args[i+1]))

        range_count += 1

    return ranges


def check_aoi(geojson):
    """
    :param geojson:
    :return:
    """
    flag = True

    for item in geojson['features']:
        if item['geometry']['type'] is not 'Polygon':
            flag = False
            logging.warning(">>>> The AOIs need to be in Polygon "
                            "representation. {} found!".format(item['geometry']['type']))
            break

    return flag


def check_list_dir(path):
    """
    :param path:
    :return:
    """
    path_list = os.listdir(path)

    if len(path_list) == 0:
        logging.warning(">>>> Path {} is empty!".format(path))

    return path_list


def check_dir_exist(output_mosaic_path):
    """
    :param output_mosaic_path:
    :return:
    """
    try:
        os.makedirs(output_mosaic_path)
    except FileExistsError:
        pass


def get_all_file_paths(directory):
    """
    :param directory:
    :return:
    """
    file_paths = []

    for root, directories, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_paths.append(file_path)

    return file_paths


def flatten_list(non_flat_list):
    """
    :param non_flat_list:
    :return:
    """
    flat_list = []

    for item in non_flat_list:
        if isinstance(item, list):
            for subitem in item:
                flat_list.append(subitem)
        else:
            flat_list.append(item)

    return flat_list


def make_archive(source, destination):
    """
    Source: http://www.seanbehan.com/how-to-use-python-shutil-make_archive-to-zip-up-a-directory-recursively-including-the-root-folder/
    :param source:
    :param destination:
    :return:
    """
    base = os.path.basename(destination)
    name = base.split('.')[0]
    format_file = base.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format_file, archive_from, archive_to)
    shutil.move('%s.%s' % (name, format_file), destination)


def flush_unnecessary_folders(path_item):
    """
    :param path_item:
    :return:
    """
    try:
        # TODO: for s3 environment: "aws s3 rm s3://mybucket --recursive"
        shutil.rmtree(path_item)
    except OSError as e:
        logging.warning(">>>>>> Error: %s : %s" % (path_item, e.strerror))
