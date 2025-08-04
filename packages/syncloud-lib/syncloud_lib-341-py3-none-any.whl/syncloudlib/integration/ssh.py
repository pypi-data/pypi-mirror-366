from subprocess import check_output, STDOUT, CalledProcessError
import logging
log = logging.getLogger()

import time


def run_scp(command, throw=True, debug=True, password='syncloud', retries=0, sleep=1, port=22):
    retry = 0
    while True:
        try:
            return _run_command('scp -P {0} -o ConnectTimeout=10 -o StrictHostKeyChecking=no {1}'.format(port, command), throw, debug, password)
        except Exception as e:
            if retry >= retries:
                raise
            retry += 1
            time.sleep(sleep)
            sleep = sleep * 2
            log.info('retrying {0}'.format(retry))


def run_ssh(host, command, throw=True, debug=True, password='syncloud', retries=0, sleep=1, env_vars='', port=22):
    ssh_command='{0} {1}'.format(env_vars, command)
    retry = 0
    while True:
        try:
            return _run_command('ssh -p {0} -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@{1} "{2}"'.format(port, host, ssh_command), throw, debug, password)
        except Exception as e:
            if retry >= retries:
                raise
            retry += 1
            time.sleep(sleep)
            sleep = sleep * 2
            log.info('retrying {0}'.format(retry))


def ssh_command(password, command):
    return 'sshpass -p {0} {1}'.format(password, command)


def _run_command(command, throw, debug, password):
    try:
        log.info('ssh command: {0}'.format(command))
        output = str(check_output(ssh_command(password, command), shell=True, stderr=STDOUT, encoding='UTF-8')).strip()
        if debug:
            log.info("ssh output: " + output)
            log.info('')
        return output
    except CalledProcessError as e:
        log.info("ssh error: " + str(e.output))
        if throw:
            raise
        return str(e.output)
