#!/usr/bin/env python

import argparse
import logging
import os

import erppeek

erppeek.Client._config_file = '%s/erppeek.ini' % \
    os.path.dirname(os.path.realpath(__file__))

logging.basicConfig(format='tssh %(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S')
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def download_and_save_instances():
    _logger.info('Download instances ...')
    client = erppeek.Client.from_config('tms')
    domain = [('active', '=', True)]
    fields = ('name', 'project_id', 'host_id', 'server_type')
    instances = client.model('tms.instance').read(domain, fields)

    _logger.info('Mapping instances ...')
    alias_hosts = {}
    for instance in instances:
        name = instance['name'].replace('openerp-', '').\
                                replace('integration', 'inte').\
                                replace('staging', 'stag').\
                                replace('hotfix', 'hotfix').\
                                replace('production', 'prod')
        host = instance['host_id'][1].split(' ')[0]
        alias_hosts[name] = host

    _logger.info('Save instances ...')
    with open('%s/.ssh/mapping_hosts' % os.path.expanduser('~'), 'w+') as f:
        for alias, host in alias_hosts.items():
            f.write('%s %s\n' % (alias, host))


def get_mapping_instance():
    fpath = '%s/.ssh/mapping_hosts' % os.path.expanduser('~')
    if not os.path.exists(fpath):
        _logger.error('Mapping instances not found, try download first ...')

    with open(fpath, 'r') as f:
        for line in f:
            yield line


parser = argparse.ArgumentParser()
parser.add_argument('-c', '--connect')
parser.add_argument('-d', '--download', action='store_true')
args = parser.parse_args()

if args.connect:
    found = False
    for line in get_mapping_instance():
        alias = line.split(' ')
        if args.connect in alias:
            found = True
            ssh_cmd = 'ssh -A %s' % alias[1]
            _logger.info('Connect to host: %s ...' % alias[1])
            os.system(ssh_cmd)

    if not found:
        _logger.error('NOT FOUND INSTANCE: %s ...' % args.connect)
if args.download:
    download_and_save_instances()
else:
    pass
