# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "zarr>3",
# ]
# ///

import zarr
from zarr.storage import MemoryStore
from zarr.core.buffer import default_buffer_prototype
import asyncio

mem_a = {}
mem_b = {}

store_a = MemoryStore(mem_a)
store_b = MemoryStore(mem_b)

# create an array and fill it with values
array = zarr.create_array(store_a, name='foo', shape=(10,), dtype='float32')
array[:] = 1

# define an async function that lists the contents of the source store and copies each key, value pair to the dest store
async def copy_store(store_a, store_b):
    async for x in store_a.list():
        await store_b.set(x, await store_a.get(x, prototype=default_buffer_prototype()))
        print(f'setting {x} ')
    return None

# run that async function
asyncio.run(copy_store(store_a, store_b))

# check that the two dictionaries are identical, i.e. everything from mem_a is in mem_b
assert mem_a == mem_b