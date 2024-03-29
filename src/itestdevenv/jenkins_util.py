from pprint import pprint

from .util import until_first_some


def _print_queue_item(queue_item):
    try:
        why = queue_item['why']
        if not why:
            raise KeyError("Why field is None")
        print(why, flush=True)
    except KeyError:
        pprint(queue_item)


def build_branch(jenkins, branch, docker=False, installers=False, test=True, coverage=False, version='8.5.0'):
    """ Starts branch build, returns build URL """
    parameters = {'BRANCH': branch,
                  'BUILD_DOCKER': docker,
                  'build_installers': installers,
                  'GENERATE_RUN_FILES': installers,
                  'do_testing': test,
                  'do_testing_linux': test,
                  'do_testing_windows': test,
                  'RCPTT_TESTING': test,
                  'do_rcptt_windows': test,
                  'ITEST_BUILD_VERSION': version,
                  'installer_branch': 'v' + version,
                  'thirdparty_jre_branch': 'v' + version,
                  'COVERAGE': coverage
                  }
    queue_item_number = jenkins.build_job('itest--branches', parameters)

    def get_url():
        queue_item = jenkins.get_queue_item(queue_item_number)

        try:
            executable = queue_item['executable']
            if not executable:
                return None
            return executable['url']
        except (TypeError, KeyError):
            _print_queue_item(queue_item)
            return None

    return until_first_some(get_url)


def wait_build(jenkins, job, build):
    until_first_some(lambda: jenkins.get_build_info(job, build)['duration'])
