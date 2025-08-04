from asyncio import sleep as async_sleep
from time import sleep as sync_sleep

from transfunctions import superfunction, sync_context, async_context, await_it


@superfunction(tilde_syntax=False)  # type: ignore[misc]
def supersleep(number: int) -> None:
    with sync_context:  # pragma: no cover
        sync_sleep(number)

    with async_context:  # pragma: no cover
        await_it(async_sleep(number))
