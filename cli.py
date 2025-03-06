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
@click.argument('targetnode')
def insert(key, value, targetnode):
    """Insert a key-value pair"""
    response = requests.post(f"http://{targetnode}/insert/{key}", json={"value": value})
    click.echo(response.json())

# Query Command
@cli.command()
@click.argument('key')
@click.argument('targetnode')
def query(key,targetnode):
    """Query a value by key"""
    response = requests.get(f"http://{targetnode}/query/{key}")
    click.echo(response.json())

# Delete Command
@cli.command()
@click.argument('key')
@click.argument('targetnode')
def delete(key,targetnode):
    """Delete a key-value pair"""
    response = requests.delete(f"http://{targetnode}/delete/{key}")
    click.echo(response.json())

@cli.command()
@click.argument('targetnode')
def overlay(targetnode):
    response = requests.get(f"http://{targetnode}/overlay")
    click.echo(response.json())

@cli.command()
@click.argument('targetnode')
def depart(targetnode):
    response = requests.delete(f"http://{targetnode}/depart")
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


@cli.command()
@click.argument('command', required=False)
def help(command):
    """Show help for commands"""
    if command:
        try:
            ctx = cli.get_command(cli, command)
            if ctx:
                click.echo(ctx.get_help(click.Context(ctx)))
            else:
                click.echo(f"Unknown command: {command}")
        except Exception as e:
            click.echo(f"Error fetching help: {e}")
    else:
        click.echo(cli.get_help(click.Context(cli)))

if __name__ == '__main__':
    cli()
