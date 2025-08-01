import click
import os
from .inspectors.uniq import UniqInspector
from .inspectors.numeric import NumericInspector



@click.group()
def cli():
    """Qualidator CLI - manage data quality checks."""
    pass

@cli.command()
def init():
    """Initialize the Qualidations directory."""
    dir_path = './.qualidations'
    
    if os.path.exists(dir_path):
        click.secho(f"Directory '{dir_path}' already exists.", fg='yellow')
    else:
        try:
            os.mkdir(dir_path)
            click.secho(f"✅ '{dir_path}' directory created successfully!", fg='green')
        except Exception as e:
            click.secho(f"❌ Failed to create directory: {e}", fg='red')



@cli.command(name='add')
@click.option('--name', required=True, help='Validation name to add.')
def add_validation(name):
    """Add validations to the suit."""

    if name.lower() == "is_not_null":
        column = click.prompt("Please enter the column name to check for NOT NULL")
        click.echo(f'✔ Will check that column "{column}" is not null.')

        query = (
            f"SELECT COUNT(*)\n"
            f"FROM ...\n"
            f"WHERE {column} IS NULL;\n"
        )
        with open(f'./.qualidations/{column.lower()}_{name.lower()}.sql', "w", encoding="utf-8") as f:
            f.write(query)

    elif name.lower() == 'column_values_are_unique':
        column = click.prompt("Please enter the column name to check for uniqueness")
        click.echo(f'✔ Will check that "{column}" column values are unique.')
        
        inspector = UniqInspector(column_name=column)
        query = inspector.column_values_are_unique()

        with open(f'./.qualidations/{column.lower()}_{name.lower()}.sql', "w", encoding="utf-8") as f:
            f.write(query)

    elif name.lower() == 'column_max_is_between':
        column = click.prompt("Please enter the column name to check for uniqueness")
        lower_bound = click.prompt("Please enter the lower bound:")
        upper_bound = click.prompt('Please enter the upper bound:')
        click.echo(f'✔ Will check that "{column}" column MAX values are between {lower_bound} and {upper_bound}')

        inspector = NumericInspector(column_name=column)
        query = inspector.column_max_is_between(lower_bound, upper_bound)

        with open(f'./.qualidations/{column.lower()}_{name.lower()}.sql', "w", encoding="utf-8") as f:
            f.write(query)
            
    else:
        pass

@cli.command(name='remove')
@click.option('--all', 'remove_all', is_flag=True, help='Remove all validations.')
@click.option('--name', help='Name of the validation to remove.')
def remove_validation(remove_all, name):
    """Remove validation(s) from the suite."""
    dir_path = './.qualidations'

    if not os.path.exists(dir_path):
        click.secho("❌ Validation directory does not exist. Run `qualidator init` first.", fg='yellow')
        return

    if remove_all:
        deleted = 0
        for file in os.listdir(dir_path):
            if file.endswith('.sql'):
                os.remove(os.path.join(dir_path, file))
                deleted += 1
        click.secho(f"🗑 Removed {deleted} validation(s).", fg='green')
        return

    if name:
        file_path = os.path.join(dir_path, f"{name}.sql")
        if os.path.exists(file_path):
            os.remove(file_path)
            click.secho(f"🗑 Removed validation '{name}'.", fg='green')
        else:
            click.secho(f"⚠ Validation '{name}' not found.", fg='yellow')
        return

    click.secho("❗ Please provide either --all or --name option.", fg='yellow')



@cli.command(name='show')
def show_validations():
    """Show already added validations"""
    i=1
    for file in os.listdir('./.qualidations/'):
        click.secho(f"{i}. {file.replace('.sql', '')}", fg='green')
        i+=1
       




if __name__ == '__main__':
    cli()
