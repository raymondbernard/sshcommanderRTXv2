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

# Setup logging
logging.basicConfig(level=logging.INFO, filename='process_logs_debug.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define file paths
local_app_data = os.getenv('LOCALAPPDATA')
CHAT_LOGS = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "chat_logs.jsonl")
DATABASE_PATH = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "sshcommander.db")

def parse_chat_logs(chat_logs_path):
    results = []
    with open(chat_logs_path, 'r') as file:
        for line in file:
            data = json.loads(line.strip())
            session_id, query, response, timestamp = data.get('session_id', ''), data.get('query', ''), data.get('response', ''), data.get('timestamp', '')
            command, description = '', ''
            if '```' in response:
                parts = response.split('```')
                command = parts[1].strip() if len(parts) > 1 else ""
                description = parts[2].strip() if len(parts) > 2 else ""
                # Remove 'bash' from the start of the command
                if command.startswith('bash '):  # Check if 'bash' is at the start and followed by a space
                    command = command[5:].strip()  # Remove 'bash ' (including the space)
                elif command.startswith('bash'):  # Check if 'bash' is at the start without a following space
                    command = command[4:].strip()
            results.append({'session_id': session_id, 'query': query, 'command': command, 'config_description': description, 'timestamp': timestamp})
    return results


def update_configuration(chat_log_entries, db_path):
    conn = connect_database(db_path)
    cursor = conn.cursor()
    try:
        for entry in chat_log_entries:
            try:
                cursor.execute("""
                    INSERT INTO servers (session_id, query, address, username, password, timestamp, config_description, commands) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (entry['session_id'], entry['query'], '', '', '', entry['timestamp'], entry['config_description'], entry['command']))
            except Exception as e:
                logging.error("Error updating configuration for entry %s: %s", entry.get('session_id'), e)
        conn.commit()
    except Exception as e:
        logging.error("Critical error updating configurations: %s", e)
        conn.rollback()
    finally:
        conn.close()


def connect_database(db_path):
    return sqlite3.connect(db_path)

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            query TEXT NOT NULL,
            address TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            timestamp REAL UNIQUE NOT NULL,
            config_description TEXT NOT NULL,
            commands TEXT 
        );
    """)
    conn.commit()


def Process_Data():
    conn = connect_database(DATABASE_PATH)
    create_tables(conn)
    conn.close()

    chat_log_entries = parse_chat_logs(CHAT_LOGS)
    update_configuration(chat_log_entries, DATABASE_PATH)
    logging.info("Configuration data has been successfully updated in the database.")
    


if __name__ == '__main__':
    Process_Data()

