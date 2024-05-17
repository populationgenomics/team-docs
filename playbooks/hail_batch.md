# Hail: Batch playbook

## Batch

### Tool reports out of memory, but VM resources don't agree?

Some tools run inside they're own virtual machine, inside the virtual machine (like docker on your computer). You can configure these tools to:

- Use the system memory,
    - but often they don't know how much system memory there is, sometimes they keep allocating if they need it, without releasing memory back.
- Use a specific [lower, upper] amount of memory:
    - Sometimes this gets pre-allocated, for example Java with the `-xms` flag will immediately appear to consume that memory, because it's reserving it for the task.
    - Sometimes it uses it will allocate as required, up to some known limit (`-xmx`). This means Java may report out of memory, even though the host machine still has more memory to consume.

Linked discussions:

- [https://centrepopgen.slack.com/archives/C030X7WGFCL/p1712182771574679](https://centrepopgen.slack.com/archives/C030X7WGFCL/p1712182771574679)



## Python jobs


Context:

Hail Batch Python jobs are a little bit of black magic. It uses the python packages dill and pickle to capture all the scope that a function needs. This could include:

  - `inputs`: this is done by pickling the value in a very generic way, so is usually very space and memory inefficient,
  - `outputs`: similar to inputs,
  - `imports` (especially for type annotations)
      - This can be very bad, as some imports (like subprocess) are very system dependent, and trying to pickle and reattach an import on a new system will almost certainly fail,
  - _variables declared outside a function_
  - any other runtime information it needs,

This makes for a really smooth user experience when it works, but a nightmare to debug.

Pro tips, make sure your function that you're calling is as self sufficient as possible, consider:

  - REMOVING type annotations
  - ensuring all imports are INSIDE the function
  - NOT passing fully formed objects (dataframes, matrix tables, lists [which don't work anyway]),
      - instead write the file to cloud storage in an efficient format,
      - pass the PATH to the python job, and reload.

### Runs out of memory on job start-up

You're probably passing a fully formed object to a python job in a loop. Hail does something weird here:

```python
df = pd.DataFrame(...)

def my_function(df):
    # do something to the df
    return df

for i in 1_000_000:
    j = b.new_python_job(f'job {i+1}')
    # Hail in fact creates 1 million pickled dataframe objects,
    # one for each iteration of the loop :sweat:
    j.call(my_function, df)
```

This is awkward to resolve, our STRONG recommendation is to pass in a PATH to the object:

```python
df = pd.DataFrame(...)
# write the df to this location
df_tmp_path = "gs://tmp-location/df.ext
with AnyPath(df_tmp_path).open('w+') as f:
    df.write(f)

def my_function(df_path):
    # import here to avoid random pickling
    import pandas as pd
    from cloudpathlib import AnyPath
    with AnyPath(df_path).open() as f:
        # EXAMPLE ONLY
        df = pd.load_csv(df_path)

    # operate on df
    output_path = df_path + '-2.csv'
    with AnyPath(output_path.open('w+')) as f:
        f.write(df.to_csv())

    return output_path

for i in 1_000_000:
    j = b.new_python_job(f'job {i+1}')
    # pass the string here, which is much more manageable
    j.call(my_function, df_tmp_path)
```


### Some issue with pickling

```pytb
  [...]
    pickler._batch_setitems(iter(source.items()))
  File "/usr/local/lib/python3.10/pickle.py", line 998, in _batch_setitems
    save(v)
  File "/usr/local/lib/python3.10/site-packages/dill/_dill.py", line 414, in save
    StockPickler.save(self, obj, save_persistent_id)
  File "/usr/local/lib/python3.10/pickle.py", line 578, in save
    rv = reduce(self.proto)
NotImplementedError: object proxy must define __reduce_ex__()
```

You probably have something in your function that is relying on an import from outside the function. Import that function or module inside your called function.
