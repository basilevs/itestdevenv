from util import until_first_some


def build_branch(jenkins, branch, docker=False, installers=False):
    """ Starts branch build, returns build URL """
    parameters = {'BRANCH': branch,
                  'BUILD_DOCKER': docker,
                  'build_installers': installers,
                  'GENERATE_RUN_FILES': installers}
    queue_item_number = jenkins.build_job('itest--branches', parameters)

    def get_url():
        queue_item = jenkins.get_queue_item(queue_item_number)
        return queue_item['executable']['url'] if 'executable' in queue_item else None

    return until_first_some(get_url)


