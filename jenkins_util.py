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
        if 'executable' not in queue_item:
            return None
        executable = queue_item['executable']
        if not executable:
            return None
        return executable['url']

    return until_first_some(get_url)


