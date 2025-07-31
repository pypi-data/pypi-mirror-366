#!/usr/bin/env python3
import os
import platform
import subprocess
import re
import sys
from getpass import getpass
from google import genai


def get_saved_api_key():
    import os

    config_dir = os.path.expanduser("~/.config/daagy")
    api_key_file = os.path.join(config_dir, "api_key.txt")

    if not os.path.exists(api_key_file):
        # Ask the user for API key
        api_key = input("API key not found. Please enter your Gemini API key. Its a one time process: ").strip()
        os.makedirs(config_dir, exist_ok=True)
        with open(api_key_file, "w") as f:
            f.write(api_key)
        print("API key saved successfully.")
    else:
        with open(api_key_file, "r") as f:
            api_key = f.read().strip()

    return api_key


api_key = get_saved_api_key()
client = genai.Client(api_key=api_key)

# OS Detection
OS = platform.system()

# Shell command map
shell_cmds = {
    "Linux": {
        "pwd": "pwd",
        "ls": "ls",
        "make_file": "touch",
        "write": "echo",
    },
    "Windows": {
        "pwd": "cd",
        "ls": "dir",
        "make_file": "type nul >",
        "write": "echo",
    }
}

# Gemini system prompt
base_prompt = f"""
You are an OS-level assistant on {OS}.
Rules:
1. Only output raw {OS} shell commands. No backticks, no quotes.
2. Do not assume any framework (Node.js, Express, etc.) unless asked clearly.
3. Don’t repeat the same command.
4. Don’t create files/folders unless instructed.
5. If asked to install or uninstall anything then include '-y' only when required.
"""

def clean_output(text):
    return text
#    return re.sub(r'^[`"\']+|[`"\']+$', '', text.strip())

def get_command(task, history):
    full_prompt = f"{base_prompt}\nPrevious: {history[-2:]}\nTask: {task}\nCommand:"
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=full_prompt
    )
    return clean_output(response.text)

def get_answer(question):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=question
    )
    return response.text.strip()

def run_command(cmd):
    import subprocess
    import sys

    try:
        if "sudo" in cmd:
            from getpass import getpass
            sudo_password = getpass("Enter your sudo password (hidden): ")

            # Remove 'sudo' from each line
            commands = cmd.strip().split('\n')
            cleaned_commands = [
                c.replace('sudo ', '', 1).strip() if c.strip().startswith("sudo") else c.strip()
                for c in commands if c.strip()
            ]
            command_block = " && ".join(cleaned_commands)

            # Construct full sudo command
            cmd = f"echo {sudo_password} | sudo -S bash -c \"{command_block}\""

        print(f"Running: {cmd}")
#        print(f"Running: {command_block}")
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # Print output line by line as it arrives
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                print(line.strip())

        if process.returncode != 0:
            return f"Error: Command failed with return code {process.returncode}"
        return "Command executed successfully."

    except Exception as e:
        return f"Error: {str(e)}"






def task_loop(task, max_steps=5):
    history = []
    for _ in range(max_steps):
        command = get_command(task, history)
        if not command or (history and command == history[-1]):
            print("Stopping — no command or repetition detected.")
            break
        history.append(command)
        output = run_command(command)
        print(f"Result:\n{output}")
        if "Error" in output:
            task = f"Fix this error and proceed: {output}"
        else:
            break
    print("Task finished.")


def main():
    if len(sys.argv) < 2:
        print("Usage:\n  daagy <your shell task>\n  daagy ques <your question>")
        sys.exit(1)

    if sys.argv[1].lower() == "ques":
        question = " ".join(sys.argv[2:])
        answer = get_answer(question)
        print(f"Answer:\n{answer}")
    else:
        task = " ".join(sys.argv[1:])
        task_loop(task)

if __name__ == "__main__":
    main()
