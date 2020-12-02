from time import sleep


def until_first_some(method):
    while True:
        result = method()
        if result:
            return result
        sleep(1)