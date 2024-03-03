# SPDX-FileCopyrightText: Copyright (c) 2024 Ray Bernard ray.bernard@outlook.com All rights reserved.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


import streamlit as st
import paramiko
import os
import json
import time
import select 
from datetime import datetime
import sqlite3 


# AI  = "call_openai"
## command out below if ou use call_openai 
# DEFAULT_SYSTEM_MESSAGE  = "Note we are using Nvidia's cumulus Linux distribution, just describe the commands you see.   Please keep your responses short and precise."
# Define file paths
local_app_data = os.getenv('LOCALAPPDATA')
DATABASE_PATH = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "sshcommander.db")
# Define file paths
CHAT_LOGS = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "chat_logs.jsonl")


chat_logs_file_path = CHAT_LOGS
# Function to connect to the SQLite database
def refresh_server_list_from_db():
    conn = connect_database(DATABASE_PATH)
    st.session_state.servers = load_servers_from_db(conn)
    conn.close()

def load_servers_from_db(conn):
    cursor = conn.cursor()
    # Simplified SQL query without ROW_NUMBER
    cursor.execute("""
        SELECT 
            id,
            session_id,
            query,
            address,
            username,
            password,
            timestamp,
            config_description,
            commands
        FROM servers
        ORDER BY id
    """)
    servers = cursor.fetchall()
    servers_list = []

    # Loop to populate servers_list with server details without row number
    for server in servers:
        server_dict = {
            'id': server[0],
            'session_id': server[1],
            'query': server[2],
            'address': server[3],
            'username': server[4],
            'password': server[5],
            'timestamp': server[6],
            'config_description': server[7],
            'commands': server[8]
        }
        servers_list.append(server_dict)
    # Update session_state with servers_list
    st.session_state['servers'] = servers_list
    cursor.close()
    conn.close()
    return st.session_state

   

# Function to connect to the SQLite database
def connect_database(db_path):
    return sqlite3.connect(db_path)

def display_ui():
    col1, col2 = st.columns([1, 15])
    with col1:
        st.image(os.path.join("ui", "assets", "sshcommander.png"), width=42)
    with col2:
        st.markdown("""
        <style>
        .font {
            font-size:30px;
        }
        </style>
        <div class="font">
            SSH Commander with RTX<br>
        </div>
        """, unsafe_allow_html=True)



# Initialize session state variables
def init_session_variables():
    if 'editing_index' not in st.session_state:
        st.session_state.editing_index = None
    if 'id' not in st.session_state:
        st.session_state.id = None
    if 'hostname' not in st.session_state:
        st.session_state.hostname = ''
    if 'port' not in st.session_state:
        st.session_state.port = 22
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'password' not in st.session_state:
        st.session_state.password = ''
    if 'key_filename_path' not in st.session_state:
        st.session_state.key_filename_path = None
    if 'servers' not in st.session_state:
        st.session_state.servers = []
    if 'timestamp' not in st.session_state:
        st.session_state.timestamp = ''
    if 'editing_index' not in st.session_state:
        st.session_state.editing_index = None
    if 'tests' not in st.session_state:
        st.session_state.tests = []
    if 'editing_test_index' not in st.session_state:
        st.session_state.editing_test_index = None
    if 'show_configuration_buttons' not in st.session_state:
        st.session_state.show_configuration_buttons = True 
    if 'show_edit_configs' not in st.session_state:
        st.session_state.show_edit_configs = False



def ssh_conn_form():
    # SSH Connection Information
    with st.expander("Add SSH Connection Information"):
        st.session_state.hostname = st.text_input("Hostname (Original Server)", st.session_state.hostname).strip(" ")
        st.session_state.port = st.number_input("Port (Original Server)", min_value=1, max_value=65535, value=st.session_state.port)
        st.session_state.username = st.text_input("Username (Original Server)", st.session_state.username).strip(" ")
        key_filename = st.file_uploader("Private Key File (Original Server)", type=['pem'])
        st.session_state.password = st.text_input("Password (Original Server, if required)", type="password", help="Leave empty if using a private key")

        # Save the uploaded private key file
    if key_filename is not None:
        st.session_state.key_filename_path = save_uploaded_file(key_filename)
    # Initialize session state for server details
    if 'server_address' not in st.session_state:
        st.session_state.server_address = ''
    if 'server_username' not in st.session_state:
        st.session_state.server_username = ''
    if 'server_password' not in st.session_state:
        st.session_state.server_password = ''
    # Configuration Section
        
    if st.session_state.show_edit_configs:  # Check if the expander should be shown
        with st.expander("Edit configs -- Please click on the below servers to edit them here"):            
            server_input_form(st.session_state.servers, st.session_state.editing_index, 'server_form', "Configure your devices", save_server_to_db)

# Define the add_configuration function here
def add_configuration(server, title, description, commands):
    if 'configurations' not in server:
        server['configurations'] = []
    server['configurations'].append({
        'description': description,
        'commands': commands
    })
        

# Function to handle file upload and save it temporarily
def save_uploaded_file(uploaded_file):
    try:
        if not os.path.exists('tempDir'):
            os.makedirs('tempDir')
        with open(os.path.join("tempDir", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        return os.path.join("tempDir", uploaded_file.name)
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

# SSH Functions
def create_ssh_client(hostname, port, username, password=None, key_filename=None):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add the server's host key without confirmation
    try:
        if key_filename:
            if not os.path.exists(key_filename):
                st.error("Private key file not found.")
                return None
            ssh_client.connect(hostname, port=port, username=username, key_filename=key_filename, look_for_keys=False, allow_agent=False)
        elif password:
            ssh_client.connect(hostname, port=port, username=username, password=password, look_for_keys=False, allow_agent=False)
        else:
            st.error("No authentication method provided. Please provide a password or a key file.")
            return None
    except paramiko.AuthenticationException:
        st.error("Authentication failed, please verify your credentials")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return None
    return ssh_client

def run_commands(ssh_client, server):
    address = server['address']
    username = server['username']
    server_password = server.get('password')
    config_description = server['config_description']
    commands = server['commands']
    st.markdown(f"<h4 style='font-weight:bold;'>{config_description}</h4>", unsafe_allow_html=True)
    ssh_cmd = f"ssh -o StrictHostKeyChecking=no {username}@{address}"
    if server_password:
        ssh_cmd = f"sshpass -p {server_password} {ssh_cmd}"
    
    shell = ssh_client.invoke_shell()
    shell.setblocking(0)
    shell.send(f"{ssh_cmd}\n")
    shell.send(f"{commands}\n")
    time.sleep(2)
    output = ""
    while not output.strip().endswith("$"):  # Adjust the ending prompt as per your server's command prompt
        ready, _, _ = select.select([shell], [], [], 0.5)
        if ready:
            output += shell.recv(10000).decode()  # Adjust buffer size as needed
        else:
            # Handle timeout or no data scenario
            break
    st.text(output)

    shell.send("exit\n")
    output = ""
    while not output.strip().endswith("$"):  # Adjust the ending prompt as per your server's command prompt
        ready, _, _ = select.select([shell], [], [], 0.5)
        if ready:
            output += shell.recv(10000).decode()  # Adjust buffer size as needed
        else:
            # Handle timeout or no data scenario
            break
    st.text(output)

    shell.close()
        
def save_server_to_db(servers):
    print("line 227 trying to save my servers!")
    print("line 228 here is my servers I am trying to save == ", servers)
    conn = connect_database(DATABASE_PATH)
    cursor = conn.cursor()
    id = 0
    for server in servers:
        if not isinstance(server, dict) or 'commands' not in server:
            print(f"Error: Invalid server data format or missing 'commands' key: {server}")
            continue

        # Remove 'bash' from the beginning of the commands string if present
        commands = server['commands']
        if commands.startswith('bash'):
            commands = commands[len('bash'):].strip()

        address_value = server.get('address', 'default_value_if_missing')
        username_value = server.get('username', 'default_value_if_missing')
        password_value = server.get('password', 'default_value_if_missing')
        server_id = server.get('id')  # Assuming there's an ID field
        id += 1  # Note: This assumes id is manually managed and increments. Make sure it aligns with your DB's id handling.
        
        try:
            cursor.execute("""
                UPDATE servers SET address = ?, username = ?, password = ?, commands = ?
                WHERE id = ?""",
                (address_value, username_value, password_value, commands, id))
            print(f"Updated server with id {server_id}")
        except Exception as e:
            print(f"An error occurred while updating: {e}")
    conn.commit()
    cursor.close()

    cursor.close()

# Server Information Input
def server_input_form(servers, editing_index, key, title,  save_server_to_db):
    with st.form(key=key):
        st.subheader(title)
        editing_server = servers[editing_index] if editing_index is not None else {}
        current_timestamp = datetime.now().timestamp()

        # If editing, use the existing timestamp, otherwise generate a new one for new entries
        # current_timestamp = editing_server.get("timestamp", datetime.now().isoformat())
        print("line 417 current_timestamp", current_timestamp)
        
        address = st.text_input("Address of server/device", value=editing_server.get("address", "")).strip()
        server_username = st.text_input("Username", value=editing_server.get("username", "")).strip()
        server_password = st.text_input("Password (optional)", type="password", value=editing_server.get("password", "")).strip()

        commands = st.text_area("Commands (one per line)", value="".join(editing_server.get("commands", ""))).strip()
        # save_server_to_db(servers)
        submit_button = st.form_submit_button("Save configuration")
        
    
    if submit_button:
        # Update session state with the new values
        st.session_state.server_address = address
        st.session_state.server_username = server_username
        st.session_state.server_password = server_password
        st.session_state.commands = commands


        # Gather server information
        server_info = {
            "address": address,
            "username": server_username,
            "password": server_password,
            "timestamp": current_timestamp,  # Use the existing or new timestamp
            "config_description": "",
            "commands": commands 
        }

        # Save or update the server information
        if editing_index is not None:
            servers[editing_index] = server_info
        else:
            servers.append(server_info)
        save_server_to_db(servers)
        st.session_state.show_edit_configs = False
        st.success("Server saved successfully")
        st.rerun()


def buttons():
    if st.session_state.show_configuration_buttons:
        with st.expander("View Saved Configurations and or Edit/Delete"):
            display_servers(st.session_state.servers, 'editing_index', 'config', delete_server_from_db, save_server_to_db, st.rerun)
    # Action Button for Configuration
    if st.button("Start Configuration"):
        with st.spinner("Configuring devices..."):
            try:
                # Create SSH client to the original server
                original_ssh_client = create_ssh_client(
                    st.session_state.hostname,
                    st.session_state.port,
                    st.session_state.username,
                    st.session_state.password,
                    st.session_state.key_filename_path
                )
                if original_ssh_client is None:
                    st.error("Failed to create SSH client to the original server.")
                    st.stop()

                # Run commands on each server through the original server
                for server in st.session_state.servers:
                    st.write(f"Configuring {server['address']} through {st.session_state.hostname}...")
                    run_commands(original_ssh_client, server)

                st.success("Configuration completed successfully!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
            finally:
                if 'original_ssh_client' in locals() and original_ssh_client is not None:
                    original_ssh_client.close()

def refactordb():
    # Connect to your SQLite database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    # Step 1: Create a temporary table to store the current data
    cursor.execute("""CREATE TEMPORARY TABLE tmp_servers AS SELECT * FROM servers;""")

    # Step 2: Drop the original 'servers' table
    cursor.execute("""DROP TABLE servers;""")

    # Step 3: Recreate the 'servers' table with the updated structure, including all specified columns
    cursor.execute("""
    CREATE TABLE "servers" (
        "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
        "session_id" TEXT NOT NULL,
        "query" TEXT NOT NULL,
        "address"   TEXT NOT NULL,
        "username"  TEXT NOT NULL,
        "password"  TEXT NOT NULL,
        "timestamp" REAL NOT NULL UNIQUE,
        "config_description" TEXT NOT NULL,
        "commands"  TEXT
    );
    """)

    # Step 4: Copy data from the temporary table to the 'servers' table with new primary keys
    # Ensure all columns including 'query' are correctly listed in both the INSERT INTO and SELECT parts
    cursor.execute("""
    INSERT INTO servers (session_id, query, address, username, password, timestamp, config_description, commands)
    SELECT session_id, query, address, username, password, timestamp, config_description, commands FROM tmp_servers;
    """)

    # Step 5: Drop the temporary table
    cursor.execute("""DROP TABLE tmp_servers;""")

    # Commit changes and close connection
    conn.commit()
    conn.close()


def delete_server_from_db(server):
    print("!!!!!!!***Delete server from db , line 383, server id to be deleted = ", server['id'])

    conn = connect_database(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM servers WHERE id = ?", (server['id'],))  # Pass ID as a tuple
    conn.commit()
    cursor.close()
    conn.close()

    # refresh_server_list_from_db()
    refactordb()


def display_servers(servers, editing_index_key, section,  delete_server_from_db, save_server_to_db, rerun_function):
    for i, server in enumerate(servers):
        st.write(f"Server {i+1}: {server['address']}")
        st.write(f"Username: {server['username']}")
        st.write("Commands:")
        st.text(server['commands'])

        with st.container():
            col1, col2, col3 = st.columns([1, 1, 1])
            edit_button = col1.button("Edit", key=f"edit_{section}_{i}")
            delete_button = col2.button("Delete", key=f"delete_{section}_{i}")
            # refresh_server_list_from_db()
            # Handle edit button press
            if edit_button:
                # Safely retrieve the timestamp, providing a default if not found
                # Update the session state to indicate which server is being edited
                
                st.session_state[editing_index_key] = i
                st.session_state.show_edit_configs = True  # Trigger the expander to show

                save_server_to_db(server)
                rerun_function()  # Rerun the app to load the editing form
                st.session_state.clear()
                refresh_server_list_from_db()


            # Handle delete button press separately
            if delete_button:
                print("Delete button line 420 servers == ", server)
                print("Delete button line 421 server id = ", server['id'])
                print("Delete button line 422, = ", servers[i])
                  # Directly call delete_server_from_db with the server to be deleted
                delete_server_from_db(server)  # Pass the correct server object

                del servers[i]
                # st.rerun()  # Rerun the app to reflect change

                # Assuming you want to refresh or update the list/display after deletion
                # servers.remove(server)  # Remove the server from the list if it's stored in memory
                # st.session_state.servers = servers  # Update the session state if needed
                # st.session_state.clear()
                st.rerun()  # Rerun the app to reflect change
        st.write("---")


# process config to markdown 
def display_servers_as_markdown(servers):
    markdown_text = ""
    # print("437 servers markdown === ", servers)
    if servers and 'servers' in servers:
        for server in servers['servers']:
            # Adding server details and description
            markdown_text += f"**Server ID:** {server['id']}\n\n"
            markdown_text += f"**Session ID:** `{server['session_id']}`\n\n"
            markdown_text += f"**Query:** {server['query']}\n\n"
            markdown_text += f"**Configuration Note:**\n\n> {server['config_description']}\n\n"
            markdown_text += "**Commands:**\n\n```bash\n"
            
            # Assuming commands are stored as a single string with newline characters
            markdown_text += f"{server['commands']}\n```\n\n"
            
            markdown_text += "---\n\n"  # Separator between server configurations
    else:
        markdown_text += "No servers configured.\n"

    return markdown_text
# create a markdown of the contents of the config.json file
def markdown_file(servers):
    st.sidebar.button('Read Config', on_click=lambda: st.session_state.update({'read_config': True}))

    markdown_text = display_servers_as_markdown(servers)
    st.markdown(markdown_text)
    # Generate a download button for the markdown content
    st.sidebar.download_button(
        label="Download Markdown",
        data=markdown_text,
        file_name="server_config.md",
        mime="text/markdown"
    )

# Function to close the database connection
def close_database_connection(conn):
    conn.close()


# Main Application Logic
def Startup():
    # st.session_state.clear()
    
    display_ui()

    # Check if the database file exists
    if os.path.exists(DATABASE_PATH):
        conn = connect_database(DATABASE_PATH)
        init_session_variables()
        print(f"The database file '{DATABASE_PATH}' exists.")
        
        servers = load_servers_from_db(conn)
        ssh_conn_form()
        buttons()
        markdown_file(servers)
        close_database_connection(conn)
    else:
        print(f"The database file '{DATABASE_PATH}' does not exist.  ")
        st.write("Please Wait until Chat with SSH Commander RTX Opens to continue")


    
if __name__ == "__main__":
    Startup()
