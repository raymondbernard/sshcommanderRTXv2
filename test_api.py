import requests
import json 
# Define the base URL for the API
base_url = "http://127.0.0.1:8081"

# Define a function to request chat completions
def request_chat_completion(prompt, system_message="", stream=False, temperature=1.0):
    endpoint = "/chat/completions"
    url = base_url + endpoint
    headers = {"Content-Type": "application/json"}
    data = {
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "stream": stream,
        "temperature": temperature
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.text)
        return None

# Example usage
if __name__ == "__main__":

    system_message = "Take my Json and return another json with the keys of 'discription' and commands' . The  commands be betweem ``` ```` "
    prompt = json.dumps({"session_id": "3e964f37-ed87-4ea7-8f5e-bd10cdaa2e8b", "query": "Let's run the Cumulus Linuzx test drive.  just provide the set of commands to run the labs", "response": "To run the Cumulus Linux test drive, follow the steps below:\n\nLab 1: Verifying Lab Connectivity\n--------------------------------\n\n1. Connect to the oob-mgmt-server:\n```\nssh ubuntu@oob-mgmt-server\n```\n2. Change directories to the Test-Drive-Automation folder:\n```\ncd Test-Drive-Automation\n```\n3. Perform a git pull to sync/fetch changes:\n```\ngit pull\n```\n4. Run the start-lab.yml Ansible playbook:\n```\nansible-playbook start-lab.yml\n```\n\nLab 2: Interface Configuration\n------------------------------\n\n1. Configure loopback addresses on leaf01 and leaf02:\n```\nnv set interface lo ip address 10.255.255.1/32\nnv config apply\n```\n\n```\nnv set interface lo ip address 10.255.255.2/32\nnv config apply\n```\n\n2. Configure bond between leaf01 and leaf02:\n```\nnv set interface bond0 bond member swp49-50\nnv config apply\n```\n\n3. Configure bridge and access ports on leaf01:\n```\nnv set bridge domain br_default vlan 10,20\nnv set interface swp1,bond0 bridge domain br_default\nnv set interface swp1 bridge domain br_default access 10\nnv config apply\n```\n\n4. Configure bridge and access ports on leaf02:\n```\nnv set bridge domain br_default vlan 10,20\nnv set interface swp2,bond0 bridge domain br_default\nnv set interface swp2 bridge domain br_default access 20\nnv config apply\n```\n\n5. Configure SVIs and VRR on leaf01 and leaf02:\n```\nnv set interface vlan10 ip address 10.0.10.2/24\nnv set interface vlan10 ip vrr address 10.0.10.1/24\nnv set interface vlan10 ip vrr mac-address 00:00:00:00:1a:10\nnv set interface vlan10 ip vrr state up\nnv set interface vlan20 ip vrr address 10.0.20.1/24\nnv set interface vlan20 ip vrr mac-address 00:00:00:00:1a:20\nnv set interface vlan20 ip vrr state up\nnv config apply\n```\n\nLab 3: FRR & BGP Unnumbered\n--------------------------\n\n1. Apply loopback address to spine01:\n```\nnv set interface lo ip address 10.255.255.101/32\nnv config apply\n```\n\n2. Configure BGP unnumbered on spine01:\n```\nnv set vrf default router bgp autonomous-system 65201\nnv set vrf default router bgp path-selection multipath aspath-ignore on\nnv set router bgp router-id 10.255.255.101\nnv set vrf default router bgp neighbor swp1 remote-as external\nnv set vrf default router bgp neighbor swp2 remote-as external\nnv config apply\n```\n\n3. Configure BGP unnumbered on leaf01:\n```\nnv set vrf default router bgp autonomous-system 65101\nnv set vrf default router bgp path-selection multipath aspath-ignore on\nnv set router bgp router-id 10.255.255.1\nnv set vrf default router bgp neighbor swp1 remote-as external\nnv config apply\n```\n\n4. Configure BGP unnumbered on leaf02:\n```\nnv set vrf default router bgp autonomous-system 65102\nnv set vrf default router bgp path-selection multipath aspath-ignore on\nnv set router bgp router-id 10.255.255.2\nnv set vrf default router bgp neighbor swp1 remote-as external\nnv config apply", "timestamp": 1709481544.3202758})
    completion = request_chat_completion(prompt, system_message)
    if completion:
        # content = completion['choices'][0]['message']['response']
        # print("Completion:", content)
        response_data = completion['choices'][0]['message']['content'].split('* `response`: ')[-1].split('</s>')[0]
        print(response_data)

