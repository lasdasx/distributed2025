import click
import requests

BASE_URL = "http://localhost:5000"  # Change if your server runs on a different host/port

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
    response = requests.post(f"{BASE_URL}/insert", json={"key": key, "value": value})
    click.echo(response.json())

# Query Command
@cli.command()
@click.argument('key')
def query(key):
    """Query a value by key"""
    response = requests.get(f"{BASE_URL}/query/{key}")
    click.echo(response.json())

# Delete Command
@cli.command()
@click.argument('key')
def delete(key):
    """Delete a key-value pair"""
    response = requests.delete(f"{BASE_URL}/delete/{key}")
    click.echo(response.json())

if __name__ == '__main__':
    cli()
