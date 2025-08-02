import subprocess
import click
from sima_cli.utils.env import is_modalix_devkit

def scan_nvme():
    try:
        nvme_list = subprocess.check_output("sudo nvme list", shell=True, text=True).strip()
        if "/dev/nvme0n1" in nvme_list:
            return nvme_list
    except subprocess.CalledProcessError:
        pass
    return None

def get_lba_format_index():
    try:
        lba_output = subprocess.check_output("sudo nvme id-ns -H /dev/nvme0n1 | grep 'Relative Performance'", shell=True, text=True)
        lbaf_line = lba_output.strip().split(":")[0]
        lbaf_index = lbaf_line.split()[-1]
        return lbaf_index
    except Exception:
        return None

def format_nvme(lbaf_index):
    cmds = [
        f"sudo nvme format /dev/nvme0n1 --lbaf={lbaf_index}",
        "sudo parted -a optimal /dev/nvme0n1 mklabel gpt",
        "sudo parted -a optimal /dev/nvme0n1 mkpart primary ext4 0% 100%",
        "sudo mkfs.ext4 /dev/nvme0n1p1",
        "sudo nvme smart-log -H /dev/nvme0n1"
    ]
    for cmd in cmds:
        subprocess.run(cmd, shell=True, check=True)

def add_nvme_to_fstab():
    """
    Add /dev/nvme0n1p1 to /etc/fstab for persistent mounting at /mnt/nvme.
    Only appends if the entry does not already exist.
    Requires root permission to modify /etc/fstab.
    """
    fstab_path = "/etc/fstab"
    nvme_entry = "/dev/nvme0n1p1  /mnt/nvme  ext4  defaults  0  2"

    try:
        # Check if the entry already exists
        with open(fstab_path, "r") as f:
            for line in f:
                if "/dev/nvme0n1p1" in line or "/mnt/nvme" in line:
                    click.echo("ℹ️  NVMe mount entry already exists in /etc/fstab.")
                    return

        # Append the entry as sudo
        append_cmd = f"echo '{nvme_entry}' | sudo tee -a {fstab_path} > /dev/null"
        subprocess.run(append_cmd, shell=True, check=True)
        click.echo("✅ /etc/fstab updated to include NVMe auto-mount.")
    except Exception as e:
        click.echo(f"❌ Failed to update /etc/fstab: {e}")

def mount_nvme():
    subprocess.run("sudo mkdir -p /mnt/nvme", shell=True, check=True)
    subprocess.run("sudo mount /dev/nvme0n1p1 /mnt/nvme", shell=True, check=True)

def nvme_format():
    if not is_modalix_devkit():
        click.echo("❌  This command can only be run on the Modalix DevKit.")
        return

    nvme_info = scan_nvme()
    if not nvme_info:
        click.echo("❌  No NVMe drive detected.")
        return
    click.echo(nvme_info)

    lbaf_index = get_lba_format_index()
    if lbaf_index is None:
        click.echo("❌  Failed to detect LBA format index.")
        return
    click.echo(f"ℹ️  Detected LBA format index: {lbaf_index}")

    if not click.confirm("⚠️  Are you sure you want to format /dev/nvme0n1? This will erase all data."):
        click.echo("❌ Aborted by user.")
        return

    try:
        # Unmount before formatting, ignore error if not mounted
        subprocess.run("sudo umount /mnt/nvme", shell=True, check=False)

        # Format and mount
        format_nvme(lbaf_index)
        mount_nvme()
        add_nvme_to_fstab()

        click.echo("✅  NVMe drive formatted and mounted at /mnt/nvme.")
    except subprocess.CalledProcessError:
        click.echo("❌ Formatting process failed.")


def nvme_remount():
    if not is_modalix_devkit():
        click.echo("❌ This command can only be run on the Modalix DevKit.")
        return

    try:
        # Ensure mount point exists
        subprocess.run("sudo mkdir -p /mnt/nvme", shell=True, check=True)
        # Mount the partition
        subprocess.run("sudo mount /dev/nvme0n1p1 /mnt/nvme", shell=True, check=True)

        # Add NVME to fstab
        add_nvme_to_fstab()

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to remount NVMe: {e}")