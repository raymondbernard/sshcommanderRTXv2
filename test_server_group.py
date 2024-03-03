import re

def extract_commands(response):
    commands = []
    # Regular expression to find commands enclosed within ```
    pattern = r'```([\s\S]*?)```'
    matches = re.findall(pattern, response)
    for match in matches:
        commands.append(match.strip())
    return commands

def organize_commands(commands):
    command_groups = {}
    current_group = None
    for command in commands:
        if command.startswith("ssh"):
            current_group = "oob-mgmt-server"
        elif command.startswith("nv set interface"):
            current_group = "leaf01 and leaf02"
        elif command.startswith("nv set vrf"):
            current_group = "spine01"
        elif command.startswith("nv set router"):
            current_group = "leaf01"
        elif command.startswith("nv set vrf"):
            current_group = "leaf02"
        if current_group not in command_groups:
            command_groups[current_group] = []
        command_groups[current_group].append(command)
    return command_groups

# Example data
data = {
    "session_id": "3e964f37-ed87-4ea7-8f5e-bd10cdaa2e8b",
    "query": "Let's run the Cumulus Linuzx test drive.  just provide the set of commands to run the labs",
    "response": "To run the Cumulus Linux test drive, follow the steps below:\n\nLab 1: Verifying Lab Connectivity\n--------------------------------\n\n1. Connect to the oob-mgmt-server:\n```\nssh ubuntu@oob-mgmt-server\n```\n2. Change directories to the Test-Drive-Automation folder:\n```\ncd Test-Drive-Automation\n```\n3. Perform a git pull to sync/fetch changes:\n```\ngit pull\n```\n4. Run the start-lab.yml Ansible playbook:\n```\nansible-playbook start-lab.yml\n```\n\nLab 2: Interface Configuration\n------------------------------\n\n1. Configure loopback addresses on leaf01 and leaf02:\n```\nnv set interface lo ip address 10.255.255.1/32\nnv config apply\n```\n\n```\nnv set interface lo ip address 10.255.255.2/32\nnv config apply\n```\n\n2. Configure bond between leaf01 and leaf02:\n```\nnv set interface bond0 bond member swp49-50\nnv config apply\n```\n\n3. Configure bridge and access ports on leaf01:\n```\nnv set bridge domain br_default vlan 10,20\nnv set interface swp1,bond0 bridge domain br_default\nnv set interface swp1 bridge domain br_default access 10\nnv config apply\n```\n\n4. Configure bridge and access ports on leaf02:\n```\nnv set bridge domain br_default vlan 10,20\nnv set interface swp2,bond0 bridge domain br_default\nnv set interface swp2 bridge domain br_default access 20\nnv config apply\n```\n\n5. Configure SVIs and VRR on leaf01 and leaf02:\n```\nnv set interface vlan10 ip address 10.0.10.2/24\nnv set interface vlan10 ip vrr address 10.0.10.1/24\nnv set interface vlan10 ip vrr mac-address 00:00:00:00:1a:10\nnv set interface vlan10 ip vrr state up\nnv set interface vlan20 ip vrr address 10.0.20.1/24\nnv set interface vlan20 ip vrr mac-address 00:00:00:00:1a:20\nnv set interface vlan20 ip vrr state up\nnv config apply\n```\n\nLab 3: FRR & BGP Unnumbered\n--------------------------\n\n1. Apply loopback address to spine01:\n```\nnv set interface lo ip address 10.255.255.101/32\nnv config apply\n```\n\n2. Configure BGP unnumbered on spine01:\n```\nnv set vrf default router bgp autonomous-system 65201\nnv set vrf default router bgp path-selection multipath aspath-ignore on\nnv set router bgp router-id 10.255.255.101\nnv set vrf default router bgp neighbor swp1 remote-as external\nnv set vrf default router bgp neighbor swp2 remote-as external\nnv config apply\n```\n\n3. Configure BGP unnumbered on leaf01:\n```\nnv set vrf default router bgp autonomous-system 65101\nnv set vrf default router bgp path-selection multipath aspath-ignore on\nnv set router bgp router-id 10.255.255.1\nnv set vrf default router bgp neighbor swp1 remote-as external\nnv config apply\n```\n\n4. Configure BGP unnumbered on leaf02:\n```\nnv set vrf default router bgp autonomous-system 65102\nnv set vrf default router bgp path-selection multipath aspath-ignore on\nnv set router bgp router-id 10.255.255.2\nnv set vrf default router bgp neighbor swp1 remote-as external\nnv config apply",
    "timestamp": 1709481544.3202758
}

# Extract commands
commands = extract_commands(data["response"])
# Organize commands into command groups
command_groups = organize_commands(commands)

# Print command groups
for server_group, command_group in command_groups.items():
    print(f"Server Group: {server_group}")
    for command in command_group:
        print(f"Command: {command}")
    print()