import sys
import logging
import time
import argparse
import settings

import aws_utils as utils
import aws_process as process

from coloredlogs import ColoredFormatter


def main(ranges):
    """
    USAGE: python aws_cli.py -ranges 2018-05-24 2018-07-23 2018-09-24 2018-11-23 2019-07-12 2019-08-11 -verbose True

    :param ranges: String range dates
    :return:
    """
    start_time = time.time()
    logging.info("Starting process...")

    ranges = utils.evaluate_range_dates_args(ranges)

    if settings.MAIN_FLOW_SEARCH_IMAGES is True:
        process.search_and_download(ranges)

    end_time = time.time()
    logging.info("Whole process completed! [Time: {0:.5f} seconds]!".format(end_time - start_time))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Search and download orbital images from AWS repositories. These images consists on the Sentinel, '
                    'Landsat, and CBERS constelations, mainly.')
    parser.add_argument('-ranges', nargs='*', action="store", dest='ranges', help='Range of dates to be downloaded. '
                                                                                  'Keep the following format: '
                                                                                  'YYYY-mm-dd, with no quotes or spaces'
                                                                                  'spaces between the numbers. The '
                                                                                  'dates must to be in pairs, where '
                                                                                  'the first is start date, following '
                                                                                  'the stop date.')
    parser.add_argument('-verbose', action="store", dest='verbose', help='Print log of processing')
    args = parser.parse_args()

    if bool(args.verbose):
        log = logging.getLogger('')

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        cf = ColoredFormatter("[%(asctime)s] {%(filename)-15s:%(lineno)-4s} %(levelname)-5s: %(message)s ")
        ch.setFormatter(cf)
        log.addHandler(ch)

        fh = logging.FileHandler('logging.log')
        fh.setLevel(logging.INFO)
        ff = logging.Formatter("[%(asctime)s] {%(filename)-15s:%(lineno)-4s} %(levelname)-5s: %(message)s ",
                               datefmt='%Y.%m.%d %H:%M:%S')
        fh.setFormatter(ff)
        log.addHandler(fh)

        log.setLevel(logging.DEBUG)
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s")

    main(args.ranges)
