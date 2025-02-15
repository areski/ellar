import os

import pytest
from pydantic.json import ENCODERS_BY_TYPE
from starlette.responses import JSONResponse

from ellar.constants import ELLAR_CONFIG_MODULE
from ellar.core.conf import Config, ConfigDefaultTypesMixin
from ellar.core.conf.config import ConfigRuntimeError
from ellar.core.versioning import DefaultAPIVersioning, UrlPathAPIVersioning
from ellar.exceptions import APIException, RequestValidationError


class ConfigTesting(ConfigDefaultTypesMixin):
    DEBUG: bool = True

    SECRET_KEY: str = "your-secret-key-changed"

    INJECTOR_AUTO_BIND = True

    JINJA_TEMPLATES_OPTIONS = {"auto_reload": DEBUG}

    VERSIONING_SCHEME = UrlPathAPIVersioning()
    REDIRECT_SLASHES: bool = True
    STATIC_MOUNT_PATH: str = "/static-changed"


overriding_settings_path = "tests.test_conf.test_default_conf:ConfigTesting"


def test_default_configurations():
    config = Config()

    assert config.DEBUG is False
    assert config.DEFAULT_JSON_CLASS == JSONResponse
    assert config.SECRET_KEY == "your-secret-key"
    assert config.INJECTOR_AUTO_BIND is False

    assert config.JINJA_TEMPLATES_OPTIONS == {}

    assert isinstance(config.VERSIONING_SCHEME, DefaultAPIVersioning)
    assert config.REDIRECT_SLASHES is False

    assert config.STATIC_FOLDER_PACKAGES == []
    assert config.STATIC_MOUNT_PATH == "/static"

    assert config.MIDDLEWARE == []

    assert RequestValidationError in config.EXCEPTION_HANDLERS
    assert APIException in config.EXCEPTION_HANDLERS

    assert callable(config.DEFAULT_NOT_FOUND_HANDLER)
    assert config.DEFAULT_LIFESPAN_HANDLER is None

    assert config.SERIALIZER_CUSTOM_ENCODER == ENCODERS_BY_TYPE


def test_configuration_export_to_os_environment():
    os.environ.setdefault(ELLAR_CONFIG_MODULE, overriding_settings_path)
    config = Config()

    assert config.DEBUG
    assert config.SECRET_KEY == "your-secret-key-changed"
    assert config.INJECTOR_AUTO_BIND is True
    assert config.JINJA_TEMPLATES_OPTIONS == {"auto_reload": True}
    assert isinstance(config.VERSIONING_SCHEME, UrlPathAPIVersioning)
    assert config.REDIRECT_SLASHES is True
    assert config.STATIC_MOUNT_PATH == "/static-changed"

    del os.environ[ELLAR_CONFIG_MODULE]


def test_configuration_raise_runtime_error_for_invalid_settings_module_path():
    os.environ.setdefault(ELLAR_CONFIG_MODULE, "tests.somewrongpath.settings")
    with pytest.raises(ConfigRuntimeError):
        Config()

    del os.environ[ELLAR_CONFIG_MODULE]

    with pytest.raises(ConfigRuntimeError):
        Config(config_module="tests.somewrongpath.settings")

    with pytest.raises(Exception):
        Config(STATIC_FOLDER_PACKAGES=[("package",)])

    with pytest.raises(Exception):
        Config(STATIC_FOLDER_PACKAGES=[("package", "static", "some_whatever")])


def test_configuration_settings_can_be_loaded_through_constructor():
    config = Config(config_module=overriding_settings_path)
    assert config.DEBUG
    assert config.SECRET_KEY == "your-secret-key-changed"
    assert config.INJECTOR_AUTO_BIND is True
    assert config.JINJA_TEMPLATES_OPTIONS == {"auto_reload": True}
    assert isinstance(config.VERSIONING_SCHEME, UrlPathAPIVersioning)
    assert config.REDIRECT_SLASHES is True
    assert config.STATIC_MOUNT_PATH == "/static-changed"


def test_configuration_can_be_changed_during_instantiation():
    config = Config(
        config_module=overriding_settings_path,
        DEBUG=False,
        SOME_NEW_CONFIGS="some new configuration values",
        JINJA_TEMPLATES_OPTIONS={"auto_reload": False},
    )

    assert config.DEBUG is False
    assert config.JINJA_TEMPLATES_OPTIONS == {"auto_reload": False}
    assert config.SOME_NEW_CONFIGS == "some new configuration values"


def test_can_set_defaults_a_configuration_instance_once():
    config = Config(config_module=overriding_settings_path)
    with pytest.raises(Exception):
        config.SOME_NEW_CONFIGS
    config.setdefault("SOME_NEW_CONFIGS", "some new configuration values")
    assert config.SOME_NEW_CONFIGS == "some new configuration values"

    config.setdefault("SOME_NEW_CONFIGS", "some new configuration values changed")
    assert config.SOME_NEW_CONFIGS == "some new configuration values"


def test_can_change_configuration_values_after_instantiation():
    config = Config(config_module=overriding_settings_path)
    assert config.DEBUG

    config["DEBUG"] = False
    assert config.DEBUG is False

    config["SOME_NEW_CONFIGS"] = "some new configuration values"
    assert config.SOME_NEW_CONFIGS == "some new configuration values"

    config["SOME_NEW_CONFIGS"] = "some new configuration values changed"
    assert config.SOME_NEW_CONFIGS == "some new configuration values changed"

    config.config_module = "somethings"
    assert config.config_module == "somethings"


def test_can_export_configuration_values():
    config = Config()
    values = list(config.values)

    assert len(values) > 7
