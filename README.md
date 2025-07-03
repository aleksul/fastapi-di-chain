# fastapi-di-chain

Chain FastAPI dependencies without unused Depends!

## Overview

`fastapi-di-chain` provides a utility to chain FastAPI dependencies in a way that avoids
unused `Depends` parameters, making your dependency injection cleaner,
more maintainable and easier to integrade.

## Installation

```bash
pip install fastapi-di-chain
```

## Usage

Suppose you have several dependencies that you want to chain together:

```python
from fastapi import FastAPI, Depends
from fastapi_di_chain import DependsChain

app = FastAPI()

def my_rate_limiting_dependency() -> None:
    # e.g. checks rate limiting
    pass

def my_authentication_dependency() -> None:
    # e.g. checks that user is authenticated to do a request
    pass

dependency_chain = DependsChain | my_rate_limiting_dependency | my_authentication_dependency

@app.get("/profile", dependencies=[dependency_chain])
def profile() -> dict:
    return {"user": 123}
```

## License

**fastapi-di-chain** is distributed under the terms of the MIT license.
Please see [License.md] for more information.

[License.md]: https://github.com/aleksul/fastapi-di-chain/blob/main/LICENSE
