import streamlit as st
import paramiko
import os
import json
import time
import select

# Constants
CONFIG_FILE = "config.json"
TEST_FILE = "test.json"
CONFIG_AI_FILE = "config_ai.json"
DEFAULT_AI = "call_nvidia"  # Corrected typo
DEFAULT_SYSTEM_MESSAGE = "Note we are using Nvidia's Cumulus Linux distribution. Please describe the commands you see. Keep responses short and precise."

def main():
    init_session_variables()
    display_ui()
    load_config()
    config_ai_interface()
    load_tests()
    ssh_conn_form()
    buttons()
    test_form()
    markdown_file()

def display_ui():
    col1, col2 = st.columns([1, 15])
    with col1:
        st.image(os.path.join("ui", "assets", "nvidia_logo.png"), width=42)
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

def init_session_variables():
    if 'editing_index' not in st.session_state:
        st.session_state.editing_index = None
    # Initialize other session state variables as needed

def load_config():
    # Implementation for loading configuration from CONFIG_FILE

def config_ai_interface():
    st.sidebar.title("AI Configuration")
    config = load_json(CONFIG_AI_FILE, default={"AI": DEFAULT_AI, "SYSTEM_MESSAGE": DEFAULT_SYSTEM_MESSAGE})
    system_message = st.sidebar.text_area("System Message", value=config.get('SYSTEM_MESSAGE', DEFAULT_SYSTEM_MESSAGE))
    if st.sidebar.button("Save Configuration"):
        config['SYSTEM_MESSAGE'] = system_message
        save_json(CONFIG_AI_FILE, config)
        st.sidebar.success("AI Configuration saved!")

def load_tests():
    # Implementation for loading tests from TEST_FILE

def ssh_conn_form():
    # Implementation for SSH connection form

def buttons():
    # Implementation for action buttons

def test_form():
    # Implementation for test form

def markdown_file():
    # Implementation for reading and displaying server configuration as markdown

def load_json(filename, default=None):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        st.error(f"Failed to load {filename}: {e}")
        return default

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    st.success("Configuration saved successfully.")

# Additional functions like create_ssh_client, run_commands, etc.

if __name__ == "__main__":
    main()