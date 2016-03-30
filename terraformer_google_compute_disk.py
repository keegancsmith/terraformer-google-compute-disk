#!/usr/bin/env python

'''Takes output from `gcloud compute disks list` to create a terraform file
to manage them.

This is useful to bootstrap using terraform to manage google compute disks'''

from collections import namedtuple

Resource = namedtuple('Resource', ['config', 'full_name', 'state'])

def from_gcloud_compute_disks_list(project, lines):
    for line in lines:
        name, zone, size_gb, disk_type, status = line.split()
        if name == 'NAME':
            # header
            continue
        config = '''resource "google_compute_disk" "{name}" {{
    name = "{name}"
    type = "{disk_type}"
    zone = "{zone}"
    size = "{size_gb}"
}}'''.format(name=name, zone=zone, size_gb=size_gb, disk_type=disk_type)
        full_name = 'google_compute_disk.' + name
        state = {
            'type': 'google_compute_disk',
            'primary': {
                'id': name,
                'attributes': {
                    'id': name,
                    'name': name,
                    'self_link': 'https://www.googleapis.com/compute/v1/projects/{project}/zones/{zone}/disks/{name}'.format(project=project, zone=zone, name=name),
                    'size': size_gb,
                    'type': disk_type,
                    'zone': zone,
                }
            }
        }
        yield Resource(config=config, full_name=full_name, state=state)

def tfstate_resources(resources):
    return dict((r.full_name, r.state) for r in resources)

def tfstate(tfstate_resources):
    'Simple substition of a resource dict into a simple terraform.tfstate'
    return {
        'version': 1,
        'serial': 0,
        'modules': [{
            'path': ['root'],
            'outputs': {},
            'resources': tfstate_resources,
        }],
    }

def tf_config(resources):
    return '\n\n'.join(r.config for r in resources)

if __name__ == '__main__':
    import argparse
    import fileinput
    import json

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, help='The Project ID of the Google Developer Project')
    parser.add_argument('--tfstate', action='store_true')
    args = parser.parse_args()

    if args.test:
        test()
        exit(0)

    resources = from_gcloud_compute_disks_list(args.project, fileinput.input(files=[]))
    if args.tfstate:
        r = tfstate_resources(resources)
        print(json.dumps(tfstate(r), indent=4))
    else:
        print(tf_config(resources))
