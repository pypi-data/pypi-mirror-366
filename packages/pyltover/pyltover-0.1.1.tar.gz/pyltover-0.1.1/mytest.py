import asyncio
from pyltover import Pyltover


with open(".devkey", "r") as f:
    token = f.read()


async def main():
    pyltover = Pyltover(token)
    await pyltover.init_champions_db()

    resp = await pyltover.euw.v4.get_total_champion_mastery_score(
        "ZcIG4rdQ5B70ykqcHAqmTWHBNYnxSEX8z0ZvmJA-Q43iTNYOMG82E_jy3WZxBLTQ4DK-xon4VIyLoQ"
    )
    print(resp)

    resp = await pyltover.europe.v1.get_account_by_puuid(
        "ZcIG4rdQ5B70ykqcHAqmTWHBNYnxSEX8z0ZvmJA-Q43iTNYOMG82E_jy3WZxBLTQ4DK-xon4VIyLoQ"
    )
    print(resp)


asyncio.run(main())
