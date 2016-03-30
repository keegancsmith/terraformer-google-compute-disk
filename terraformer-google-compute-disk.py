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

def test():
    lines = '''NAME                                     ZONE          SIZE_GB TYPE        STATUS
disk-1                                   us-central1-f 500     pd-standard READY
disk-2                                   us-central1-f 100     pd-ssd      READY
'''.splitlines()
    want_config = '''resource "google_compute_disk" "disk-1" {
    name = "disk-1"
    type = "pd-standard"
    zone = "us-central1-f"
    size = "500"
}

resource "google_compute_disk" "disk-2" {
    name = "disk-2"
    type = "pd-ssd"
    zone = "us-central1-f"
    size = "100"
}'''
    want_full_name = 'google_compute_disk.disk-2'
    want_state_resources = {
        'google_compute_disk.disk-2': {
            'type': 'google_compute_disk',
            'primary': {
                'id': 'disk-2',
                'attributes': {
                    'id': 'disk-2',
                    'name': 'disk-2',
                    'self_link': 'https://www.googleapis.com/compute/v1/projects/my-project/zones/us-central1-f/disks/disk-2',
                    'size': '100',
                    'type': 'pd-ssd',
                    'zone': 'us-central1-f'
                }
            }
        }
    }
    got = list(from_gcloud_compute_disks_list('my-project', lines))
    got_config = tf_config(got)
    got_state_resources = tfstate_resources([got[-1]])
    assert got_config == want_config
    assert got_state_resources == want_state_resources
    print('Tests passed')

if __name__ == '__main__':
    import argparse
    import fileinput
    import json

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, help='The Project ID of the Google Developer Project')
    parser.add_argument('--tfstate', action='store_true')
    parser.add_argument('--test', action='store_true')
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
