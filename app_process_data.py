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
import json
import os
import logging
import sqlite3

# Setup logging to include console and file output
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('process_logs_debug.log', mode='w'),
                        logging.StreamHandler()
                    ])

# Define file paths
local_app_data = os.getenv('LOCALAPPDATA')
CHAT_LOGS = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "chat_logs.jsonl")
DATABASE_PATH = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "sshcommander.db")

def parse_chat_logs(chat_logs_path):
    results = []
    with open(chat_logs_path, 'r') as file:
        for line in file:
            # Skip empty lines or lines with only whitespace
            if not line.strip():
                continue
            try:
                data = json.loads(line.strip())
            except json.JSONDecodeError:
                logging.error(f"Skipping invalid JSON line: {line.strip()}")
                continue  # Skip lines that cannot be parsed as JSON

            session_id, query, response, timestamp = data.get('session_id', ''), data.get('query', ''), data.get('response', ''), data.get('timestamp', '')
            commands = []
            descriptions = []
            if '```' in response:
                parts = response.split('```')
                for i in range(1, len(parts), 2):
                    command = parts[i].strip()
                    description = parts[i+1].strip() if i+1 < len(parts) else ""
                    command = command.removeprefix('bash ').strip()
                    commands.append(command)
                    descriptions.append(description)
            results.append({'session_id': session_id, 'query': query, 'commands': commands, 'config_descriptions': descriptions, 'timestamp': timestamp})
    return results

def update_configuration(chat_log_entries, db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        for entry in chat_log_entries:
            commands_concatenated = '; '.join(entry['commands'])  # Concatenate all commands
            descriptions_concatenated = ' | '.join(entry['config_descriptions'])  # Concatenate all descriptions
            try:
                cursor.execute("""
                    INSERT INTO servers (session_id, query, address, username, password, timestamp, config_description, commands) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (entry['session_id'], entry['query'], '', '', '', entry['timestamp'], descriptions_concatenated, commands_concatenated))
            except sqlite3.IntegrityError:
                logging.error(f"Duplicate entry for timestamp {entry['timestamp']}. Skipping.")
            except Exception as e:
                logging.error(f"Error updating configuration for entry {entry.get('session_id')}: {e}")
        conn.commit()

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            query TEXT NOT NULL,
            address TEXT,
            username TEXT,
            password TEXT,
            timestamp REAL UNIQUE NOT NULL,
            config_description TEXT,
            commands TEXT 
        );
    """)
    conn.commit()

def Process_Data():
    create_tables(sqlite3.connect(DATABASE_PATH))
    chat_log_entries = parse_chat_logs(CHAT_LOGS)
    update_configuration(chat_log_entries, DATABASE_PATH)
    logging.info("Configuration data has been successfully updated in the database.")

def Cleanup_Chatlog():
        # Define the file path
    file_path = 'chat_log.json'
    # Define an empty dictionary
    empty_data = {}
    # Open the file in write mode and clear its content by writing the empty dictionary
    with open(file_path, 'w') as file:
        json.dump(empty_data, file)
    print("Contents of 'chat_log.json' cleared.")


if __name__ == '__main__':
    Cleanup_Chatlog()
    Process_Data()
    Cleanup_Chatlog()

