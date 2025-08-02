
import click
from mtbs.mtbs import Mtbs


@click.group()
@click.pass_context
@click.option('--env', type=click.Choice(['preprod', 'prd', 'dev'], case_sensitive=True), default='dev', help='Environment to use (default: dev)')
@click.option('--cookie-file', type=click.Path(exists=True), help='Path to the Metabase cookie file, by default it will read from the Firefox cookies.')
@click.option('--format', type=click.Choice(['json', 'csv'], case_sensitive=False), default='json', help='Output format (default: json)')
def cli(ctx, env, cookie_file, format):
    """MTBS Command Line Interface."""
    """MTBS CLI - Command Line Interface for MTBS operations."""
    ctx.ensure_object(dict)
    ctx.obj['env'] = env
    ctx.obj['mtbs'] = Mtbs(env=env, cookie_file_path=cookie_file)
    ctx.obj['format'] = format
    # ctx.obj['version'] = '1.0.0'
    # ctx.obj['author'] = 'MTBS Team'
    # ctx.obj['description'] = 'MTBS CLI for managing MTBS operations.'
    # ctx.obj['license'] = 'MIT License'


@cli.command()
@click.pass_context
def database_list(ctx):
    """List available databases."""
    mtbs = ctx.obj['mtbs']
    databases = mtbs.databases_list()
    print(f'{databases}')
    # if not databases:
    #     click.echo("No databases found.")
    # else:
    #     for db in databases:
    #         click.echo(f"Database: {db['name']} (ID: {db['id']})")

@cli.command()
@click.pass_context
@click.option('--query', prompt='Your SQL query', help='The SQL query to execute.')
@click.option('--database', type=int, prompt='Database name', help='The database to execute the query against.')
def sql(ctx, query, database):
    """Execute a SQL query."""
    #click.echo(f"Executing SQL query in {ctx.obj['env']} environment:")
    #click.echo(query)
    mtbs = ctx.obj['mtbs']
    result = mtbs.send_sql(query=query, database=database, raw=False, cache_enabled=False)
    if ctx.obj['format'] == 'json':
        click.echo(result)
    elif ctx.obj['format'] == 'csv':
        import json, csv, sys
        # import pandas as pd
        # click.echo(pd.read_json(result).to_csv())
        output = csv.writer(sys.stdout)
        data = json.loads(result)
        output.writerow(data[0].keys())
        for row in data:
            output.writerow(row.values())
    else:
        # Default to JSON if format is not recognized
        # import json
        # import pandas as pd
        # click.echo(json.dumps(result, indent=2))
        click.echo(result)

if __name__ == '__main__':
    Mtbs(env="dev").databases_list()