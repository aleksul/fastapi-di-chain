from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from fastapi_di_chain.chain import DependsChain

app = FastAPI()

order: list[str] = []


def reset_order() -> None:
    global order  # noqa: PLW0603
    order = []


def dep1() -> str:
    order.append("dep1")
    return "dep1-value"


def dep2() -> str:
    order.append("dep2")
    return "dep2-value"


def dep3() -> str:
    order.append("dep3")
    return "dep3-value"


chain = DependsChain | dep1 | dep2 | dep3


@app.get("/test")
def route(
    chain_value: Annotated[str, chain],
    dep2_value: Annotated[str, Depends(dep2)],
    dep3_value: Annotated[str, Depends(dep3)],
) -> dict:
    return {
        "dep2_value": dep2_value,
        "dep3_value": dep3_value,
        "chain_value": chain_value,
    }


@app.get("/test2")
def route2(
    dep2_value: Annotated[str, Depends(dep2)],
    dep3_value: Annotated[str, Depends(dep3)],
    chain_value: Annotated[str, chain],
) -> dict:
    return {
        "dep2_value": dep2_value,
        "dep3_value": dep3_value,
        "chain_value": chain_value,
    }


def test_dependency_not_called_twice() -> None:
    reset_order()
    client = TestClient(app)
    response = client.get("/test")
    data = response.json()
    assert data["dep2_value"] == "dep2-value"
    assert data["dep3_value"] == "dep3-value"
    assert data["chain_value"] == "dep3-value"
    assert order == ["dep1", "dep2", "dep3"]


def test_dependency_not_called_twice_broken_order() -> None:
    reset_order()
    client = TestClient(app)
    response = client.get("/test2")
    data = response.json()
    assert data["dep2_value"] == "dep2-value"
    assert data["dep3_value"] == "dep3-value"
    assert data["chain_value"] == "dep3-value"
    assert order == ["dep2", "dep3", "dep1"]
