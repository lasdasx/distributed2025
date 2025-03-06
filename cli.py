import click
import requests
import socket
import sys
import threading
import subprocess
import time

@click.group()
def cli():
    """CLI for DHT Operations"""
    pass

# Insert Command
@cli.command()
@click.argument('key')
@click.argument('value')
@click.argument('targetNode')
def insert(key, value, targetNode):
    """Insert a key-value pair"""
    response = requests.post(f"http://{targetNode}/insert/{key}", json={"value": value})
    click.echo(response.json())

# Query Command
@cli.command()
@click.argument('key')
@click.argument('targetNode')
def query(key,targetNode):
    """Query a value by key"""
    response = requests.get(f"http://{targetNode}/query/{key}")
    click.echo(response.json())

# Delete Command
@cli.command()
@click.argument('key')
@click.argument('targetNode')
def delete(key,targetNode):
    """Delete a key-value pair"""
    response = requests.delete(f"http://{targetNode}/delete/{key}")
    click.echo(response.json())

@click.command
@click.argument('targetNode')
def overlay(targetNode):
    response = requests.get(f"http://{targetNode}/overlay")
    click.echo(response.json())

@cli.command()
@click.argument('targetNode')
def depart(targetNode):
    response = requests.delete(f"http://{targetNode}/depart")
    click.echo(response.json())


@cli.command()
@click.option('--port', default=5000, help='Port to start the server on')
@click.option('--bootstrap', is_flag=True, help='Start as a bootstrap node')
@click.option('-rf', type=int, help='Replication factor')
@click.option('-e', is_flag=True, help='Set consistency mode to eventual')
def join(port, bootstrap, rf, e):
    """
    Starts the Flask server (from app.py) and shows the output it produces in the terminal.
    """
    # Build the command to run app.py with the provided arguments
    command = ['python', 'app.py', '--port', str(port)]
    
    if bootstrap:
        command.append('--bootstrap')
    
    if rf:
        command.extend(['-rf', str(rf)])
    
    if e:
        command.append('-e')

    print(f"Starting the server on port {port}...")

    # Run app.py with the given arguments and show the output
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Continuously capture and print the output in real-time
    while True:
        # Read stdout line by line
        output = process.stdout.readline()
        if output:
            print(output.strip())  # Print the output in the terminal
            sys.stdout.flush()  # Flush the output immediately

        # Break when the process completes
        if process.poll() is not None:
            break

    # Ensure we read all remaining stderr if the process ends
    stderr_output = process.stderr.read()
    if stderr_output:
        print(f"Final Error: {stderr_output.strip()}")
        sys.stdout.flush()  # Flush remaining error output

    # Wait for the process to complete
    process.wait()



if __name__ == '__main__':
    cli()
