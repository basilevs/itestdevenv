from subprocess import run, CalledProcessError
from sys import stderr


def _run_command(*command_and_arguments):
    print("$", *command_and_arguments)
    run(command_and_arguments, capture_output=False, check=True)


def _get_output(*command_and_arguments):
    print("$", *command_and_arguments)
    result = run(command_and_arguments, capture_output=True, check=True)
    print(result.stderr.decode('utf-8'), file=stderr)
    return result.stdout.decode('utf-8')


class Git:
    @staticmethod
    def pull_branch(branch):
        _run_command('git', 'pull', 'origin', branch)

    @staticmethod
    def current_branch():
        return _get_output('git', 'branch', '--show-current').strip()

    @staticmethod
    def pull():
        _run_command('git', 'pull')

    @staticmethod
    def push():
        _run_command('git', 'push')

    @staticmethod
    def push_branch(local, remote):
        _run_command('git', 'push', 'origin', local + ":" + remote)

    @staticmethod
    def checkout(branch):
        try:
            _run_command('git', 'checkout', branch)
        except CalledProcessError:
            _run_command('git', 'fetch', 'origin', branch + ':' + branch)
            _run_command('git', 'checkout', branch)

    def update_branch(self, branch):
        self.checkout(branch)
        try:
            self.pull_branch(branch)
        except CalledProcessError:
            pass
        self.pull_branch('v8.4.0')
        self.push_branch(branch, branch)
