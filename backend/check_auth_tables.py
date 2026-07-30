import asyncio
import asyncpg


DATABASE_URL = (
    "postgresql://postgres:Sujal%401303@localhost:5432/aura"
)


async def check():

    conn = await asyncpg.connect(
        DATABASE_URL
    )


    print("\nSessions:")

    sessions = await conn.fetch(
        """
        SELECT *
        FROM sessions;
        """
    )

    for row in sessions:
        print(dict(row))


    print("\nRefresh Tokens:")

    tokens = await conn.fetch(
        """
        SELECT
            id,
            user_id,
            session_id,
            is_revoked,
            expires_at
        FROM refresh_tokens;
        """
    )


    for row in tokens:
        print(dict(row))


    await conn.close()



asyncio.run(check())