import terraformer_google_compute_disk as terraformer
import unittest

class GCloudDiskTestCase(unittest.TestCase):
    lines = '''NAME                                     ZONE          SIZE_GB TYPE        STATUS
disk-1                                   us-central1-f 500     pd-standard READY
disk-2                                   us-central1-f 100     pd-ssd      READY
'''.splitlines()

    def test_tf_config(self):
        want = '''resource "google_compute_disk" "disk-1" {
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
        got = list(terraformer.from_gcloud_compute_disks_list('my-project', self.lines))
        self.assertEqual(terraformer.tf_config(got), want)

    def test_tfstate_resources(self):
        want = {
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
        got = list(terraformer.from_gcloud_compute_disks_list('my-project', self.lines))
        self.assertEqual(terraformer.tfstate_resources([got[-1]]), want)

if __name__ == '__main__':
    unittest.main()
    
