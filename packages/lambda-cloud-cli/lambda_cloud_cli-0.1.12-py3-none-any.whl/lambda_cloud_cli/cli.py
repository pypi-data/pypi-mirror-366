import os
import typer
from lambda_cloud_cli.lambda_api_client import LambdaAPIClient
from lambda_cloud_cli.config import load_api_key, save_api_key, delete_api_key

app = typer.Typer()
client=None

def get_client():
    global client
    if client is None:
        API_KEY = os.environ.get("API_KEY") or load_api_key()
        if not API_KEY:
            typer.echo("❌ No API key set. Run: lambda-cli login")
            raise typer.Exit(code=1)
        client = LambdaAPIClient(api_key=API_KEY)
    return client

@app.command(name="login")
def login():
    """Set your Lambda Cloud API key"""
    api_key = typer.prompt("🔐 Enter your Lambda Cloud API key", hide_input=True)
    save_api_key(api_key)
    typer.echo("✅ API key saved.")
    
@app.command(name="logout")
def logout():
    """Remove your stored API key"""
    if delete_api_key():
        typer.echo("✅ API key removed. You are now logged out.")
    else:
        typer.echo("ℹ️  No API key was stored.")

@app.command(name="list-instances")
def list_instances():
    instances = get_client().list_instances().get("data", [])
    for inst in instances:
        typer.echo(f"{inst['id']}: {inst['name']} ({inst['status']})")

@app.command(name="terminate")
def terminate(instance_id: str):
    result = get_client().terminate_instances([instance_id])
    typer.echo(result)

@app.command(name="launch-instance")
def launch_instance():
    typer.echo("This function requires a JSON payload. Add JSON input handling if needed.")

@app.command(name="update-instance-name")
def update_instance_name(instance_id: str, new_name: str):
    result = get_client().update_instance_name(instance_id, new_name)
    typer.echo(result)

@app.command(name="list-instance-types")
def list_instance_types():
    types_dict = get_client().list_instance_types().get("data", {})
    for type_data in types_dict.values():
        inst = type_data.get("instance_type", {})
        name = inst.get("name", "unknown")
        gpus = inst.get("specs", {}).get("gpus", "?")
        typer.echo(f"{name} ({gpus} GPUs)")

@app.command(name="get-firewall-rules")
def get_firewall_rules():
    rules = get_client().get_firewall_rules().get("data", [])
    for rule in rules:
        typer.echo(rule)

@app.command(name="get-firewall-rulesets")
def get_firewall_rulesets():
    rulesets = get_client().get_firewall_rulesets().get("data", [])
    for rs in rulesets:
        typer.echo(f"{rs['id']}: {rs['name']}")

@app.command(name="get-firewall-ruleset-by-id")
def get_firewall_ruleset_by_id(ruleset_id: str):
    result = get_client().get_firewall_ruleset_by_id(ruleset_id)
    typer.echo(result)

@app.command(name="delete-firewall-ruleset")
def delete_firewall_ruleset(ruleset_id: str):
    result = get_client().delete_firewall_ruleset(ruleset_id)
    typer.echo(result)

@app.command(name="create-firewall-ruleset")
def create_firewall_ruleset(name: str, region: str):
    rules = [
        {
            "protocol": "tcp",
            "port_range": [22, 22],
            "source_network": "0.0.0.0/0",
            "description": "Allow SSH from anywhere"
        }
    ]
    result = get_client().create_firewall_ruleset(name, region, rules)
    typer.echo(result)

@app.command(name="update-firewall-ruleset")
def update_firewall_ruleset(ruleset_id: str, name: str):
    rules = [
        {
            "protocol": "tcp",
            "port_range": [22, 22],
            "source_network": "0.0.0.0/0",
            "description": "Allow SSH from anywhere"
        }
    ]
    result = get_client().update_firewall_ruleset(ruleset_id, name, rules)
    typer.echo(result)

@app.command(name="patch-global-firewall")
def patch_global_firewall():
    rules = [
        {
            "protocol": "tcp",
            "port_range": [22, 22],
            "source_network": "0.0.0.0/0",
            "description": "Allow SSH from anywhere"
        }
    ]
    result = get_client().patch_global_firewall_ruleset(rules)
    typer.echo(result)

@app.command(name="get-global-firewall")
def get_global_firewall():
    result = get_client().get_global_firewall_ruleset()
    typer.echo(result)

@app.command(name="list-ssh-keys")
def list_ssh_keys():
    keys = get_client().list_ssh_keys().get("data", [])
    for key in keys:
        typer.echo(f"{key['id']}: {key['name']} - {key['public_key'][:40]}...")

@app.command(name="add-ssh-key")
def add_ssh_key(name: str, public_key: str):
    result = get_client().add_ssh_key(name, public_key)
    typer.echo(result)

@app.command(name="delete-ssh-key")
def delete_ssh_key(key_id: str):
    result = get_client().delete_ssh_key(key_id)
    typer.echo(result)

@app.command(name="list-file-systems")
def list_file_systems():
    filesystems = get_client().list_file_systems().get("data", [])
    for fs in filesystems:
        typer.echo(f"{fs['id']}: {fs['name']} in {fs['region']}")

@app.command(name="create-file-system")
def create_file_system(name: str, region: str):
    result = get_client().create_file_system(name, region)
    typer.echo(result)

@app.command(name="delete-file-system")
def delete_file_system(fs_id: str):
    result = get_client().delete_file_system(fs_id)
    typer.echo(result)

@app.command(name="list-images")
def list_images():
    images = get_client().list_images().get("data", [])
    for img in images:
        region = img.get("region", {}).get("name", "unknown")
        typer.echo(f"{img['id']}: {img['name']} ({region})")

if __name__ == "__main__":
    app()

