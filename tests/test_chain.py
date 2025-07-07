from collections.abc import AsyncGenerator, Generator
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient

from fastapi_di_chain.chain import DependsChain

# --- Helpers for order tracking ---
order: list[str] = []


def reset_order() -> None:
    order.clear()


# --- Sync and async callables ---
def sync_dep() -> str:
    order.append("sync")
    return "sync"


async def async_dep() -> str:
    order.append("async")
    return "async"


# --- Sync and async generators ---
def sync_gen_dep() -> Generator[str, None, None]:
    order.append("sync_gen_start")
    yield "sync_gen"
    order.append("sync_gen_end")


async def async_gen_dep() -> AsyncGenerator[str, None]:
    order.append("async_gen_start")
    yield "async_gen"
    order.append("async_gen_end")


# --- Chaining with Depends ---
def base_dep() -> str:
    order.append("base")
    return "base"


# --- Additional dependencies for new tests ---
class ClassDep:
    def __init__(self) -> None:
        pass

    def __call__(self) -> str:
        order.append("class_call")
        return "class_dep"


# Async class dependency
class AsyncClassDep:
    def __init__(self) -> None:
        pass

    async def __call__(self) -> str:
        order.append("async_class_call")
        return "async_class_dep"


# Dependency with another dependency (e.g., Request)
def dep_with_request(request: Request) -> str:
    order.append("with_request")
    return f"request:{request.method}"


# --- Test FastAPI integration ---
app = FastAPI()


@app.get("/sync")
def endpoint_sync(result: Annotated[str, DependsChain() | sync_dep]) -> dict:
    return {"result": result}


@app.get("/async")
async def endpoint_async(result: Annotated[str, DependsChain() | async_dep]) -> dict:
    return {"result": result}


@app.get("/sync-gen")
def endpoint_sync_gen(result: Annotated[str, DependsChain() | sync_gen_dep]) -> dict:
    return {"result": result}


@app.get("/async-gen")
async def endpoint_async_gen(result: Annotated[str, DependsChain() | async_gen_dep]) -> dict:
    return {"result": result}


@app.get("/depends")
def endpoint_dep(result: Annotated[str, DependsChain() | Depends(base_dep) | sync_dep]) -> dict:
    return {"result": result}


@app.get("/order")
def endpoint_order(
    result: Annotated[
        str,
        DependsChain() | Depends(base_dep) | async_gen_dep | sync_dep | sync_gen_dep | async_dep,
    ],
) -> dict:
    return {"result": result}


@app.get("/order2")
def endpoint_order2(
    result: Annotated[
        str,
        DependsChain() | sync_dep | ClassDep() | AsyncClassDep() | async_dep,
    ],
) -> dict:
    return {"result": result}


@app.get("/class-dep")
def endpoint_class_dep(result: Annotated[str, DependsChain() | ClassDep()]) -> dict:
    return {"result": result}


@app.get("/async-class-dep")
async def endpoint_async_class_dep(
    result: Annotated[str, DependsChain() | AsyncClassDep()],
) -> dict:
    return {"result": result}


@app.get("/with-request")
def endpoint_with_request(result: Annotated[str, DependsChain() | dep_with_request]) -> dict:
    return {"result": result}


client = TestClient(app)


# --- Dependency override example ---
def override_sync_dep() -> str:
    order.append("override_sync")
    return "override"


# --- Tests ---
def test_sync() -> None:
    reset_order()
    resp = client.get("/sync")
    assert resp.status_code == 200
    assert resp.json()["result"] == "sync"
    assert order == ["sync"]


def test_async() -> None:
    reset_order()
    resp = client.get("/async")
    assert resp.status_code == 200
    assert resp.json()["result"] == "async"
    assert order == ["async"]


def test_sync_gen() -> None:
    reset_order()
    resp = client.get("/sync-gen")
    assert resp.status_code == 200
    assert resp.json()["result"] == "sync_gen"
    assert order == ["sync_gen_start", "sync_gen_end"]


def test_async_gen() -> None:
    reset_order()
    resp = client.get("/async-gen")
    assert resp.status_code == 200
    assert resp.json()["result"] == "async_gen"
    assert order == ["async_gen_start", "async_gen_end"]


def test_depends() -> None:
    reset_order()
    resp = client.get("/depends")
    assert resp.status_code == 200
    assert resp.json()["result"] == "sync"
    assert order == ["base", "sync"]


def test_order() -> None:
    reset_order()
    resp = client.get("/order")
    assert resp.status_code == 200
    assert resp.json()["result"] == "async"
    assert order == [
        "base",
        "async_gen_start",
        "sync",
        "sync_gen_start",
        "async",
        "sync_gen_end",
        "async_gen_end",
    ]


def test_order2() -> None:
    reset_order()
    resp = client.get("/order2")
    assert resp.status_code == 200
    assert resp.json()["result"] == "async"
    assert order == [
        "sync",
        "class_call",
        "async_class_call",
        "async",
    ]


def test_class_dep() -> None:
    reset_order()
    resp = client.get("/class-dep")
    assert resp.status_code == 200
    assert resp.json()["result"] == "class_dep"
    assert order == ["class_call"]


def test_async_class_dep() -> None:
    reset_order()
    resp = client.get("/async-class-dep")
    assert resp.status_code == 200
    assert resp.json()["result"] == "async_class_dep"
    assert order == ["async_class_call"]


def test_dep_with_request() -> None:
    reset_order()
    resp = client.get("/with-request")
    assert resp.status_code == 200
    assert resp.json()["result"] == "request:GET"
    assert order == ["with_request"]


def test_dependency_override() -> None:
    reset_order()
    app.dependency_overrides[sync_dep] = override_sync_dep
    resp = client.get("/sync")
    assert resp.status_code == 200
    assert resp.json()["result"] == "override"
    assert order == ["override_sync"]
    app.dependency_overrides = {}  # Reset overrides
