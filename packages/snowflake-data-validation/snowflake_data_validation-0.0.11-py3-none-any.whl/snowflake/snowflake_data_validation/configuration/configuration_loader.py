from pathlib import Path

from pydantic_yaml import parse_yaml_raw_as

from snowflake.snowflake_data_validation.configuration.model.configuration_model import (
    ConfigurationModel,
)
from snowflake.snowflake_data_validation.configuration.singleton import Singleton
from snowflake.snowflake_data_validation.utils.constants import (
    DATA_VALIDATION_CONFIGURATION_FILE_NAME,
    DATA_VALIDATION_CONFIGURATION_FILE_YAML,
    DATA_VALIDATION_CONFIGURATION_FILE_YML,
)


class ConfigurationLoader(metaclass=Singleton):

    """ConfigurationLoader class.

    This is a singleton class that reads the configuration.yaml file
    and provides an interface to get the configuration settings model.

    Args:
        metaclass (Singleton, optional): Defaults to Singleton.

    """

    def __init__(self, file_path: Path) -> None:
        self.configuration_model: ConfigurationModel = ConfigurationModel(
            source_platform="",
            target_platform="",
            output_directory_path="",
        )

        if file_path is None:
            raise ValueError("The configuration file path cannot be None value")

        if file_path.name not in DATA_VALIDATION_CONFIGURATION_FILE_NAME:
            raise Exception(
                f"{file_path.name} is not a valid configuration file name. "
                f"The correct file name are {DATA_VALIDATION_CONFIGURATION_FILE_YAML} "
                f"and {DATA_VALIDATION_CONFIGURATION_FILE_YML}"
            )

        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found in {file_path}")

        try:
            file_content = file_path.read_text()
            self.configuration_model = parse_yaml_raw_as(
                ConfigurationModel, file_content
            )

        except Exception as exception:
            error_msg = (
                f"An error occurred while loading the "
                f"{DATA_VALIDATION_CONFIGURATION_FILE_YAML} "
                f"or {DATA_VALIDATION_CONFIGURATION_FILE_YML} file:"
            )
            raise Exception(f"{error_msg}\n{exception}") from None

    def get_configuration_model(self) -> ConfigurationModel:
        """Get the configuration model.

        Returns:
            ConfigurationModel: The configuration model instance.

        """
        return self.configuration_model
