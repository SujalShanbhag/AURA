import asyncio

import asyncpg


DATABASE_URL = (
    "postgresql://postgres:Sujal%401303@localhost:5432/aura"
)


async def test_database_tables():

    try:

        conn = await asyncpg.connect(
            DATABASE_URL
        )

        print("PostgreSQL Connected ✅")


        tables = await conn.fetch(
            """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname='public'
            ORDER BY tablename;
            """
        )


        print("\nAURA Database Tables:")

        if not tables:

            print("No tables found ❌")


        else:

            for table in tables:

                print(
                    "✔",
                    table["tablename"]
                )


        await conn.close()

        print(
            "\nDatabase verification completed ✅"
        )


    except Exception as e:

        print(
            "\nDatabase connection failed ❌"
        )

        print(e)



if __name__ == "__main__":

    asyncio.run(
        test_database_tables()
    )