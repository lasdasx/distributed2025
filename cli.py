import click
import requests
import socket
import json
import node
def get_local_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

LOCAL_NODE = f"{node.get_adress()}"  # Always start with the local node

@click.group()
def cli():
    """CLI for DHT Operations"""
    pass

# Insert Command
@cli.command()
@click.argument('key')
@click.argument('value')
def insert(key, value):
    """Insert a key-value pair"""
    response = requests.post(f"http://{LOCAL_NODE}/insert/{key}", json={"value": value})
    click.echo(response.json())

# Query Command
@cli.command()
@click.argument('key')
def query(key):
    """Query a value by key"""
    response = requests.get(f"http://{LOCAL_NODE}/query/{key}")
    click.echo(response.json())

# Delete Command
@cli.command()
@click.argument('key')
def delete(key):
    """Delete a key-value pair"""
    response = requests.delete(f"http://{LOCAL_NODE}/delete/{key}")
    click.echo(response.json())

if __name__ == '__main__':
    cli()
