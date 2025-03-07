import subprocess
import multiprocessing
import time

# List of command files (one per process)
command_files = [
    "insert_00_part.txt",
    "insert_01_part.txt",
    "insert_02_part.txt",
    "insert_03_part.txt",
    "insert_04_part.txt",
    "insert_05_part.txt",    
    "insert_06_part.txt",
    "insert_07_part.txt",
    "insert_08_part.txt",
    "insert_09_part.txt",
]

# Corresponding nodes (one per process)
nodes = [
    "10.0.42.248:5000", "10.0.42.23:5000", "10.0.42.173:5000",
    "10.0.42.188:5000", "10.0.42.57:5000", "10.0.42.248:5001",
    "10.0.42.23:5001", "10.0.42.173:5001", "10.0.42.188:5001",
    "10.0.42.57:5001"
]

def execute_commands_from_file(filename, node):
    """Reads a file and executes each command, measuring execution time and throughput."""
    try:
        with open("expirements/inserts/" + filename, 'r') as file:
            commands = [line.strip() for line in file if line.strip()]  # Read all non-empty commands

        total_commands = len(commands)
        if total_commands == 0:
            print(f"[{filename}] No commands found.")
            return filename, node, 0, 0  # Return zero throughput if no commands exist

        start_time = time.time()  # Start timing

        for command in commands:
            full_command = f"python3 cli.py insert \"{command}\" value {node}"
            process = subprocess.run(full_command, shell=True, capture_output=True, text=True)

            if process.stdout:
                print(f"[{filename} -> {node}] Output:\n{process.stdout}")
            if process.stderr:
                print(f"[{filename} -> {node}] Error:\n{process.stderr}")

        end_time = time.time()  # End timing
        elapsed_time = end_time - start_time
        throughput = total_commands / elapsed_time if elapsed_time > 0 else 0  # Avoid division by zero

        print(f"[{filename} -> {node}] Completed in {elapsed_time:.2f} seconds, Throughput: {throughput:.2f} cmds/sec")

        return filename, node, elapsed_time, throughput  # Return results

    except FileNotFoundError:
        print(f"[{filename}] Error: File not found.")
        return filename, node, 0, 0  # Return zero throughput in case of file errors
    except Exception as e:
        print(f"[{filename}] Unexpected error: {e}")
        return filename, node, 0, 0  # Return zero throughput in case of other errors

if __name__ == "__main__":
    with multiprocessing.Pool(processes=10) as pool:
        results = pool.starmap(execute_commands_from_file, zip(command_files, nodes))

    # Print summary results
    print("\n===== Execution Summary =====")
    for filename, node, time_taken, throughput in results:
        print(f"[{filename} -> {node}] Time: {time_taken:.2f}s | Throughput: {throughput:.2f} cmds/sec")
