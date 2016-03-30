# Terraformer Google Compute Disk

Export existing Google Compute Disks to [Terraform][1] style (tf,
tfstate). Inspired by [dtan4/terraforming][2]

## Usage

Say you have a Google Cloud Platform project called `my-project` in the region
`us-central1`. Then to bootstrap using terraform run the following:

```bash
$ cat > provider.tf <<EOF
provider "google" {
    project = "my-project"
    region  = "us-central1"
}
EOF
$ gcloud compute disks list > disks.txt
$ terraformer_google_compute_disk.py --project my-project < disks.txt > disks.tf
$ terraformer_google_compute_disk.py --project my-project --tfstate < disks.txt > terraform.tfstate
```

You should now have a working terraform environment \o/. If you haven't
modified anything, running `terraform plan` should list each disk and say it
has nothing to do. You may need to set credentials in the `provider.tf`. See
[Google Cloud Provider][2] for more information.

Note: In the steps above I redirected the output to `disks.txt`. You don't
have to initially have terraform managing everything, so you can go in there
and delete the lines which you don't want managed. I usually delete all the
instance disks from management, and just leave the persistent disks I care
about.

## Limitations

This currently is hacked up to support my use case, so may generate weird
output if you use disks differently to me. Pull Requests welcome

[1]: https://www.terraform.io
[2]: https://github.com/dtan4/terraforming
[3]: https://www.terraform.io/docs/providers/google/index.html
