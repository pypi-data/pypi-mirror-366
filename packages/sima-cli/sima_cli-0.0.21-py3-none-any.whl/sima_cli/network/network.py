from InquirerPy import inquirer
import subprocess
import os
import re
import time
from sima_cli.utils.env import is_sima_board

IP_CMD = "/sbin/ip"

def extract_interface_index(name):
    """Extract numeric index from interface name for sorting (e.g., end0 → 0)."""
    match = re.search(r'(\d+)$', name)
    return int(match.group(1)) if match else float('inf')

def get_interfaces():
    interfaces = []
    ip_output = subprocess.check_output([IP_CMD, '-o', 'link', 'show']).decode()
    for line in ip_output.splitlines():
        match = re.match(r'\d+: (\w+):', line)
        if match:
            iface = match.group(1)
            if iface.startswith('lo'):
                continue
            try:
                with open(f"/sys/class/net/{iface}/carrier") as f:
                    carrier = f.read().strip() == "1"
            except FileNotFoundError:
                carrier = False

            try:
                ip_addr = subprocess.check_output([IP_CMD, '-4', 'addr', 'show', iface]).decode()
                ip_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', ip_addr)
                ip = ip_match.group(1) if ip_match else "IP Not Assigned"
            except subprocess.CalledProcessError:
                ip = "IP Not Assigned"

            # Check internet connectivity only if carrier is up
            internet = False
            if carrier:
                try:
                    result = subprocess.run(
                        ["ping", "-I", iface, "-c", "1", "-W", "1", "8.8.8.8"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    internet = result.returncode == 0
                except Exception:
                    internet = False

            interfaces.append({
                "name": iface,
                "carrier": carrier,
                "ip": ip,
                "internet": internet
            })

    interfaces.sort(key=lambda x: extract_interface_index(x["name"]))
    return interfaces

def move_network_file(iface, mode):
    try:
        networkd_dir = "/etc/systemd/network"
        files = os.listdir(networkd_dir)

        # Match any static file for this iface
        pattern = re.compile(r"(\d+)-(%s)-static\.network" % re.escape(iface))
        static_file = next((f for f in files if pattern.match(f)), None)
        if not static_file:
            print(f"⚠️ No static .network file found for {iface}")
            return

        src = os.path.join(networkd_dir, static_file)
        desired_prefix = "02" if mode == "static" else "20"
        dst_file = f"{desired_prefix}-{iface}-static.network"
        dst = os.path.join(networkd_dir, dst_file)

        if static_file == dst_file:
            print(f"✅ Interface {iface} is already set to {mode.upper()}. No changes made.")
        else:
            print(f"🔧 Changing mode of {iface} to {mode.upper()}...")
            subprocess.run(["sudo", "mv", src, dst], check=True)

        # Modify content only if going to static
        if mode == "static":
            # Read as normal user
            with open(dst, "r") as f:
                lines = f.readlines()
            cleaned = [line for line in lines if "KernelCommandLine=!netcfg=dhcp" not in line]

            # Only write if change is needed
            if len(cleaned) != len(lines):
                temp_path = f"/tmp/{iface}-static.network"
                with open(temp_path, "w") as tmpf:
                    tmpf.writelines(cleaned)
                subprocess.run(["sudo", "cp", temp_path, dst], check=True)
                os.remove(temp_path)
                print(f"✂️ Removed KernelCommandLine override from {dst_file}")
            else:
                print(f"✅ No KernelCommandLine override found — file already clean.")

        # Restart networkd
        subprocess.run(["sudo", "systemctl", "restart", "systemd-networkd"])
        time.sleep(2)
    except Exception as e:
        print(f"❌ Unable to change configuration, error: {e}")

def get_gateway_for_interface(ip):
    """Guess the gateway from the IP address, assuming .1 is the router."""
    if ip == "IP Not Assigned":
        return None
    parts = ip.split('.')
    parts[-1] = "1"
    return ".".join(parts)

def set_default_route(iface, ip):
    gateway = get_gateway_for_interface(ip)
    if not gateway:
        print(f"❌ Cannot set default route — IP not assigned for {iface}")
        return

    print(f"🔧 Setting default route via {iface} ({gateway})")

    try:
        # Delete all existing default routes
        subprocess.run(["sudo", "/sbin/ip", "route", "del", "default"], check=False)

        # Add new default route for this iface
        subprocess.run(
            ["sudo", "/sbin/ip", "route", "add", "default", "via", gateway, "dev", iface],
            check=True
        )
        print(f"✅ Default route set via {iface} ({gateway})")
    except subprocess.CalledProcessError:
        print(f"❌ Failed to set default route via {iface}")

def network_menu():
    if not is_sima_board():
        print("❌ This command only runs on the DevKit")
        return

    while True:
        interfaces = get_interfaces()
        choices = ["🚪 Quit Menu"]
        iface_map = {}

        for iface in interfaces:
            status_icon = "carrier (✅)" if iface["carrier"] else "carrier (❌)"
            internet_icon = "internet (🌐)" if iface.get("internet") else "internet (🚫)"
            label = f"{iface['name']:<10} {status_icon} {internet_icon}  {iface['ip']:<20}"
            choices.append(label)
            iface_map[label] = iface

        try:
            iface_choice = inquirer.fuzzy(
                message="Select Ethernet Interface:",
                choices=choices,
                instruction="(Type or use ↑↓)",
            ).execute()
        except KeyboardInterrupt:
            print("\nExiting.")
            break

        if iface_choice is None or iface_choice == "🚪 Quit Menu":
            print("Exiting.")
            break

        selected_iface = iface_map[iface_choice]

        try:
            second = inquirer.select(
                message=f"Configure {selected_iface['name']}:",
                choices=[
                    "Set to DHCP",
                    "Set to Default Static IP",
                    "Set as Default Route",
                    "Back to Interface Selection"
                ]
            ).execute()
        except KeyboardInterrupt:
            print("\nExiting.")
            break

        if second == "Set to DHCP":
            move_network_file(selected_iface["name"], "dhcp")
        elif second == "Set to Default Static IP":
            move_network_file(selected_iface["name"], "static")
        elif second == "Set as Default Route":
            set_default_route(selected_iface["name"], selected_iface["ip"])            
        else:
            continue 

if __name__ == '__main__':
    network_menu()