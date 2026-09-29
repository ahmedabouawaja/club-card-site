"""
Admin bootstrap command — registered on the app in app/__init__ via
`app.cli.add_command`. Usage:

    flask create-admin

Prompts for details and hashes the password properly; there is no
route anywhere that can create an admin account, on purpose.
"""
import click
from flask.cli import with_appcontext

from app.extensions import db
from app.models import User


@click.command("create-admin")
@click.option("--email", prompt=True)
@click.option("--name", prompt=True)
@click.password_option()
@with_appcontext
def create_admin(email, name, password):
    if User.query.filter_by(email=email.lower().strip()).first():
        click.echo("A user with that email already exists.")
        return
    user = User(name=name, email=email.lower().strip(), is_admin=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f"Admin account created for {email}.")
