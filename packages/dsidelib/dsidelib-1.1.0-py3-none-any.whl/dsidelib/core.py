from disco import main as disco_main
from telega import main as telega_main

async def run():
    await disco_main()
    await telega_main()