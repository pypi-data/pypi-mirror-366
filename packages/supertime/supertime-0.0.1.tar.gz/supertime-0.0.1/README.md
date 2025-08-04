# supertime: a living example of the superfunctions

The [transfunctions])https://github.com/pomponchik/transfunctions library introduces a new type of function: `superfunction`. They can behave both as regular and asynchronous functions, depending on the context, that is, on how the user uses them. This micro-library demonstrates the smallest example of this concept that I could come up with.

Install it:

```bash
pip install supertime
```

And try:

```python
from asyncio import run
from supertime import supersleep

supersleep(5)  # sleeps 5 sec.
run(supersleep(5))  # sleeps 5 sec., but ASYNCHRONOUSLY.
```

As you can see, the superfunction can automatically adjust to how the calling code uses it.
