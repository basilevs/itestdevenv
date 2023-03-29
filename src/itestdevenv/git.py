from subprocess import run, CalledProcessError, PIPE
from sys import stderr


def _run_command(*command_and_arguments):
    print("$", *command_and_arguments, flush=True)
    run(command_and_arguments, stdout=None, stderr=None, check=True)


def _get_output(*command_and_arguments):
    print("$", *command_and_arguments, flush=True)
    result = run(command_and_arguments, stdout=PIPE, stderr=PIPE, check=True)
    print(result.stderr.decode('utf-8'), file=stderr)
    return result.stdout.decode('utf-8')


class Git:
    
    def __init__(self):
        self._current_branch = None
        
    @staticmethod
    def pull_branch(branch):
        _run_command('git', 'pull', '--no-edit', 'origin', branch)

    def current_branch(self):
        self._current_branch = _get_output('git', 'branch', '--show-current').strip() 
        return self._current_branch

    @staticmethod
    def pull():
        _run_command('git', 'pull')

    @staticmethod
    def push():
        _run_command('git', 'push')
        
    @staticmethod
    def toplevel():
        return _get_output('git', 'rev-parse', '--show-toplevel').rstrip()

    @staticmethod
    def push_branch(local, remote):
        _run_command('git', 'push', 'origin', local + ":" + remote)

    def checkout(self, branch):
        try:
            _run_command('git', 'fetch', 'origin', branch + ':' + branch)
        except CalledProcessError:
            pass        
        _run_command('git', 'checkout', branch)
        self._current_branch = branch
#        _run_command('git', 'lfs', 'pull')

    def force_checkout(self, branch):
        _run_command('git', 'checkout', '-f', branch)
        self._current_branch = branch

    def reset_hard(self):
        _run_command('git', 'reset', '--hard')        

    def update_branch(self, target, *source):
        if self._current_branch != target: 
            self.checkout(target)
        try:
            self.pull_branch(target)
        except CalledProcessError:
            pass
        for s in source:
            self.pull_branch(s)
        self.push_branch(target, target)
