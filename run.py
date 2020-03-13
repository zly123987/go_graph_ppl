import argparse
import logging
from extract_dependencies.master_dep_parse import run as parse_dep_for_new_libs
from calculating_affected_libs.get_libdepends import filter_affected_libs
from extract_dependencies.run_dep_parse import run as parse_dep_for_affected_libs
from generate_csv.generate_lib import generate_csv
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('step', type=str)
    return parser.parse_args()


def handle_args(step):

    if step == 'get_libdepends':
        try:
            parse_dep_for_new_libs()
        except Exception as e:
            logger.error(str(e))

    elif step == 'filter_affected':
        try:
            filter_affected_libs()
        except Exception as e:
            logger.error(str(e))

    elif step == 'get_dependencies':
        try:
            parse_dep_for_affected_libs()
        except Exception as e:
            logger.error(str(e))

    elif step == 'generate_csv':
        try:
            generate_csv()
        except Exception as e:
            logger.error(str(e))


if __name__ == '__main__':
    args = parse_args()
    handle_args(args.step)



