import asyncio
import asyncpg


async def test():

    try:

        conn = await asyncpg.connect(
            "postgresql://postgres:Sujal%401303@localhost:5432/aura"
        )

        print("PostgreSQL Connected ✅")

        await conn.close()

    except Exception as e:

        print("Database Connection Failed ❌")
        print(e)



asyncio.run(test())