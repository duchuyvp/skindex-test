import os
import pathlib
from typing import Any, Generator

import pytest
from chat_service import bootstrap
import core
import utils
from core.adapters import sqlalchemy_adapter
from fastapi import testclient
from core.adapters import create_component_factory
from chat_service.entrypoints.rest.app import app


@pytest.fixture(scope="session")
def project_path() -> Generator[pathlib.Path, Any, None]:
    yield pathlib.Path(__file__).parents[1]


@pytest.fixture(scope="session")
def config_path(project_path: pathlib.Path) -> str:
    return str(project_path / ".configs")


@pytest.fixture(scope="session")
def config(
    project_path: pathlib.Path, config_path: str
) -> Generator[dict[str, Any], Any, None]:
    os.environ["CONFIG_PATH"] = config_path
    os.environ["ENVIRONMENT"] = "test"
    os.environ["TEST_OTP_RESULT"] = str(project_path / "otp.json")
    config = utils.load_config(str(project_path / ".configs"))
    config = config | utils.load_config(config_path)
    yield config


@pytest.fixture(scope="session")
def bus(config: dict[str, Any]) -> Generator[core.MessageBus, Any, None]:
    bus = bootstrap.bootstrap()
    yield bus


@pytest.fixture(scope="session")
def rest_client(config: dict[str, Any]) -> Generator[testclient.TestClient, Any, None]:
    component_factory = create_component_factory(config["database"])
    assert isinstance(component_factory, sqlalchemy_adapter.ComponentFactory)

    registry = component_factory.create_orm_registry()
    registry.metadata.drop_all(bind=component_factory.engine)
    registry.metadata.create_all(bind=component_factory.engine)

    yield testclient.TestClient(app)

    registry.metadata.drop_all(bind=component_factory.engine)
