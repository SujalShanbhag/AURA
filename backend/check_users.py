import asyncio
import asyncpg


DATABASE_URL = (
    "postgresql://postgres:Sujal%401303@localhost:5432/aura"
)


async def check_users():

    conn = await asyncpg.connect(
        DATABASE_URL
    )

    users = await conn.fetch(
        """
        SELECT 
            id,
            email,
            username,
            created_at
        FROM users;
        """
    )


    print("\nUsers in AURA database:\n")


    for user in users:

        print(
            dict(user)
        )


    await conn.close()



if __name__ == "__main__":

    asyncio.run(
        check_users()
    )