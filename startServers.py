import paramiko

def ssh_execute(vm_host, command):
    """
    Connects to a remote VM and executes a single command via SSH.

    :param vm_host: SSH hostname (e.g., 'vm1')
    :param command: Command to execute
    :return: Dictionary with command outputs
    """
    results = {}

    try:
        # Create an SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Accept unknown host keys

        # Connect to the VM (assuming SSH keys are set up)
        client.connect(vm_host)

        print(f"Connected to {vm_host}")

        # Execute the command
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        results = {"output": output, "error": error}

    except Exception as e:
        results = {"output": "", "error": str(e)}

    finally:
        # Ensure the connection is closed
        client.close()
        print(f"Disconnected from {vm_host}")

    return results

# Example usage
if __name__ == "__main__":
    vm_hosts = ["team_35-vm2", "team_35-vm3", "team_35-vm4", "team_35-vm5"]

    commands = [
        "cd distributed2025 && python3 cli join --port 5000 --bootstrap -rf 1",
        "cd distributed2025 && python3 cli join --port 5001",
    ]

    # Execute on vm1 first
    for cmd in commands:
        output = ssh_execute("team_35-vm1", cmd)
        print(f"\nCommand: {cmd}")
        print(f"Output: {output['output']}")
        print(f"Error: {output['error']}")

    commands = [
        "cd distributed2025 && python3 cli join --port 5000 ",
        "cd distributed2025 && python3 cli join --port 5001",
    ]
    # Execute on other VMs
    for vm_host in vm_hosts:
        for cmd in commands:
            output = ssh_execute(vm_host, cmd)
            print(f"\nVM: {vm_host} | Command: {cmd}")
            print(f"Output: {output['output']}")
            print(f"Error: {output['error']}")
