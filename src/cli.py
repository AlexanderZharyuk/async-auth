from asyncio import run as aiorun

import typer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from src.core.config import settings
from src.v1.users.models import User

app = typer.Typer(help="Awesome CLI user manager.")


@app.command("create_super_admin", help="Create a new super_admin user.")
def create_super_admin():
    async def _async_create_user(user: User) -> None:
        engine = create_async_engine(settings.pg_dsn)
        async with AsyncSession(engine, expire_on_commit=False) as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
        print(f"Created super_admin user: {user!r}")

    print("Creating a new super_admin user:")
    username = typer.prompt("What's super_admin username?")
    password = typer.prompt("What's super_admin password?", hide_input=True)
    email = typer.prompt("What's super_admin email?")
    full_name = typer.prompt("What's super_admin full name?")

    # TODO: hash password
    # password = hashlib.sha256(password.encode()).hexdigest()

    super_admin = User(
        username=username,
        password=password,
        email=email,
        full_name=full_name,
        is_superuser=True,
    )
    aiorun(_async_create_user(user=super_admin))


if __name__ == "__main__":
    app()
