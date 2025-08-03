A Python implementation of the author

## Installing

```
pip install pyjwtv2
```

## Usage

```
>>> import jwt
>>> encoded = jwt.encode({"some": "payload"}, "secret", algorithm="HS256")
>>> print(encoded)
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb21lIjoicGF5bG9hZCJ9.4twFt5NiznN84AWoo1d7KO1T_yoc0Z6XOpOVswacPZg
>>> jwt.decode(encoded, "secret", algorithms=["HS256"])
{'some': 'payload'}
```