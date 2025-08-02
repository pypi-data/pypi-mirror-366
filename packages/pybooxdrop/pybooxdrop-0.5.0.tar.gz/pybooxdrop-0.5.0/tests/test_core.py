import gc
import warnings
from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest
from pydantic import SecretStr, ValidationError

from boox.api.config_users import ConfigUsersApi
from boox.api.users import UsersApi
from boox.core import Boox
from boox.models.enums import BooxUrl

if TYPE_CHECKING:
    from unittest.mock import Mock

    from faker import Faker
    from pytest_mock import MockerFixture

# pyright: reportPrivateUsage=false


def _shows_all_members(e: ValidationError) -> bool:
    errors = e.errors(include_url=False, include_context=False, include_input=False)
    return all(m.value in errors[0]["msg"] for m in list(BooxUrl))


def _cast_to_secret_str(u: str) -> SecretStr:
    return SecretStr(u)


def test_boox_initializes_with_defaults():
    assert Boox()


def test_boox_base_url_is_none_by_default():
    boox = Boox()
    assert boox.base_url is None


@pytest.mark.parametrize("url", list(BooxUrl))
def test_boox_base_url_inferred_from_client(mocked_client: "Mock", url: BooxUrl):
    mocked_client.base_url = url
    boox = Boox(client=mocked_client)
    assert boox.base_url is url


def test_explicit_base_url_takes_precedence(mocked_client: "Mock"):
    url_taking_precedence = BooxUrl.EUR
    boox = Boox(client=mocked_client, base_url=url_taking_precedence)
    assert boox.base_url is url_taking_precedence


def test_client_base_url_overrides_constructor_value(mocked_client: "Mock"):
    url_taking_precedence = BooxUrl.EUR
    url_not_taking_precedence = BooxUrl.PUSH
    mocked_client.base_url = url_taking_precedence
    boox = Boox(client=mocked_client, base_url=url_not_taking_precedence)
    assert boox.base_url is url_taking_precedence


def test_boox_raises_validation_error_for_invalid_url(mocked_client: "Mock"):
    mocked_client.base_url = "http://random.url"
    with pytest.raises(ValidationError, match="Input should be", check=_shows_all_members):
        Boox(client=mocked_client)


@pytest.mark.parametrize("url", list(BooxUrl))
def test_boox_base_url_can_be_set(mocked_client: "Mock", url: BooxUrl):
    boox = Boox(client=mocked_client)
    boox.base_url = url
    assert boox.base_url == url.value


def test_boox_base_url_set_raises_on_invalid_url(mocked_client: "Mock"):
    boox = Boox(client=mocked_client)
    with pytest.raises(ValidationError, match="Input should be", check=_shows_all_members):
        boox.base_url = "http://random.url"  # pyright: ignore[reportAttributeAccessIssue]


def test_boox_is_not_closed_after_init(mocked_client: "Mock"):
    boox = Boox(client=mocked_client)
    assert boox.is_closed is False


def test_boox_is_closed_after_context_exit(mocked_client: "Mock"):
    with Boox(client=mocked_client) as boox:
        pass
    assert boox.is_closed


def test_boox_client_exposed_in_context(mocked_client: "Mock"):
    with Boox(client=mocked_client) as boox:
        assert boox.client is mocked_client


def test_warning_when_neither_with_nor_close_used():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        def create_boox():
            return Boox()

        boox = create_boox()
        del boox
        gc.collect()

    assert any(str(w.message).startswith("Boox client was not closed explicitly") for w in w)


def test_no_warning_with_context_manager():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        with Boox():
            pass

    assert not any(str(w.message).startswith("Boox client was not closed explicitly") for w in w)


def test_no_warning_with_manual_close():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        boox = Boox()
        boox.close()
        del boox
        gc.collect()

    assert not any(str(w.message).startswith("Boox client was not closed explicitly") for w in w)


def test_boox_close_calls_internal_method(mocker: "MockerFixture", mocked_client: "Mock"):
    boox = Boox(client=mocked_client)
    mock_close = mocker.patch.object(boox, "close")

    boox.close()
    mock_close.assert_called_once()


def test_boox_raises_on_closed_client(mocked_client: "Mock"):
    mocked_client.is_closed = True

    with pytest.raises(ValueError, match="Cannot initialize Boox with a closed connection"):
        Boox(client=mocked_client)


def test_close_calls_client_and_sets_flag(mocker: "MockerFixture", mocked_client: "Mock"):
    boox = Boox(client=mocked_client)
    spy = mocker.spy(mocked_client, "close")

    boox.close()
    spy.assert_called_once()
    assert boox._is_closed


def test_close_skips_if_already_closed(mocker: "MockerFixture", mocked_client: "Mock"):
    boox = Boox(client=mocked_client)
    spy = mocker.spy(mocked_client, "close")
    boox._is_closed = True

    boox.close()
    spy.assert_not_called()


def test_close_skips_if_client_missing(mocker: "MockerFixture", mocked_client: "Mock"):
    boox = Boox(client=mocked_client)
    spy = mocker.spy(mocked_client, "close")
    del boox.client

    boox.close()
    spy.assert_not_called()
    assert not boox._is_closed


def test_boox_client_is_assigned_properly(mocked_client: "Mock"):
    boox = Boox(client=mocked_client)
    assert boox.client is mocked_client


def test_boox_users_api_is_initialized(mocked_client: "Mock"):
    boox = Boox(client=mocked_client)
    assert isinstance(boox.users, UsersApi)


def test_boox_config_users_api_is_initiated(mocked_client: "Mock"):
    boox = Boox(client=mocked_client)
    assert isinstance(boox.config_users, ConfigUsersApi)


def test_boox_sets_default_headers(mocked_client: "Mock"):
    boox = Boox(client=mocked_client)
    assert boox.client.headers == {"Content-Type": "application/json"}


def test_boox_token_is_unset_by_default():
    boox = Boox()
    assert not boox.token
    assert not boox.client.headers.get("Authorization")


def test_boox_token_is_extracted_from_client_headers(faker: "Faker", mocked_client: "Mock"):
    token = faker.uuid4()
    mocked_client.headers.update({"Authorization": f"Bearer {token}"})
    boox = Boox(client=mocked_client)
    assert boox.token == token
    assert boox.client.headers.get("Authorization") == f"Bearer {token}"


def test_client_token_takes_precedence_over_inline_token(faker: "Faker", mocked_client: "Mock"):
    client_token = faker.uuid4()
    inline_token = faker.uuid4()
    mocked_client.headers.update({"Authorization": f"Bearer {client_token}"})
    boox = Boox(client=mocked_client, token=inline_token)
    assert boox.token == client_token
    assert boox.client.headers.get("Authorization") == f"Bearer {client_token}"


@pytest.mark.parametrize("wrapper", [str, _cast_to_secret_str])
def test_boox_constructor_accepts_str_and_secretstr_in_constructor(
    faker: "Faker",
    wrapper: Callable[[str], str | SecretStr],
):
    token = faker.uuid4()
    boox = Boox(token=wrapper(token))
    assert boox.token == str(token)
    assert boox.client.headers.get("Authorization") == f"Bearer {token!s}"


@pytest.mark.parametrize("wrapper", [str, _cast_to_secret_str])
def test_token_setter_accepts_str_and_secretstr(
    faker: "Faker",
    wrapper: Callable[[str], str | SecretStr],
):
    token = faker.uuid4()
    boox = Boox()
    boox.token = wrapper(token)
    assert boox.token == str(token)
    assert boox.client.headers.get("Authorization") == f"Bearer {token!s}"
