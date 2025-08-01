import pytest

from snowflake.core.api_integration import ApiIntegration, GitHook
from tests.integ.fixtures.constants import UUID
from tests.integ.utils import random_string


@pytest.fixture(scope="module", autouse=True)
def setup(api_integrations):
    names = [random_string(10, f"test_api_integration_iter_a_{UUID}_")]
    for _ in range(2):
        names.append(random_string(10, f"test_api_integration_iter_b_{UUID}_"))
    for _ in range(3):
        names.append(random_string(10, f"test_api_integration_iter_c_{UUID}_"))
    try:
        print(names)
        for name in names:
            ai_def = ApiIntegration(
                name=name,
                api_hook=GitHook(),
                api_allowed_prefixes=["https://github.com"],
                enabled=True,
                comment="created by test_iter",
            )
            api_integrations.create(ai_def)
        yield
    finally:
        for name in names:
            api_integrations[name].drop(if_exists=True)


def test_iter(api_integrations):
    assert len(list(api_integrations.iter())) >= 6


def test_iter_like(api_integrations):
    assert len(list(api_integrations.iter(like=f"test_api_integration_iter_x_{UUID}_%"))) == 0
    assert len(list(api_integrations.iter(like=f"test_api_integration_iter_a_{UUID}_%"))) == 1
    assert len(list(api_integrations.iter(like=f"test_api_integration_iter_b_{UUID}_%"))) == 2
    assert len(list(api_integrations.iter(like=f"test_api_integration_iter_c_{UUID}_%"))) == 3
