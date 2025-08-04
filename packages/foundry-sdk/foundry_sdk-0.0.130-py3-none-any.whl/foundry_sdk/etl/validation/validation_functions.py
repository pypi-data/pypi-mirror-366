import logging
from datetime import date, datetime
from types import TracebackType

import polars as pl

from foundry_sdk.db_mgmt.sql_db_alchemy import SQLAlchemyDatabase
from foundry_sdk.etl.constants import FREQUENCY_MAPPING, DatasetTypes

logger = logging.getLogger(__name__)


########################################################################################################
###################################### New validation functions ########################################
########################################################################################################


class DataValidator:
    def __init__(self, db: SQLAlchemyDatabase) -> None:
        self.db = db
        self.session = None

    def __enter__(self) -> "DataValidator":
        self.session = self.db.SessionLocal()
        return self

    def __exit__(
        self, _exc_type: type[BaseException] | None, _exc_val: BaseException | None, _exc_tb: TracebackType | None
    ) -> None:
        if self.session:
            self.session.close()
            self.session = None
            self.session = None

    def check_company_name(self, company_name: str) -> None:
        """
        Validate company name format.

        Requirements:
        - Must be all lowercase
        - No spaces allowed
        - Hyphens are allowed but discouraged (warning issued)
        """
        if not isinstance(company_name, str):
            msg = f"Company name must be a string. Got {type(company_name).__name__}: {company_name}"
            raise TypeError(msg)

        if not company_name:
            raise ValueError("Company name cannot be empty.")

        # Check for uppercase characters
        if not company_name.islower():
            raise ValueError("Company name must be all lowercase.")

        # Check for spaces
        if " " in company_name:
            raise ValueError("Company name cannot contain spaces. Use underscores instead.")

        # Check for hyphens and warn
        if "-" in company_name:
            logger.warning(
                "Company name '%s' contains hyphens. "
                "Consider using underscores instead of hyphens for better consistency, "
                "unless the first part encodes a set of company datasets",
                company_name,
            )

    def check_dataset_type(self, dataset_type: str, company_name: str) -> None:
        """
        Validate dataset type format and rules.

        Requirements:
        - Must be all lowercase
        - Must be one of the allowed types from DatasetTypes enum
        - If dataset_type is 'competition', company_name must contain at least one underscore
        """
        if not isinstance(dataset_type, str):
            msg = f"Dataset type must be a string. Got {type(dataset_type).__name__}: {dataset_type}"
            raise TypeError(msg)

        if not dataset_type:
            raise ValueError("Dataset type cannot be empty.")

        # Check for lowercase
        if not dataset_type.islower():
            raise ValueError("Dataset type must be all lowercase.")

        # Check if dataset type is allowed
        allowed_types = [dt.value for dt in DatasetTypes]
        if dataset_type not in allowed_types:
            msg = f"Dataset type '{dataset_type}' is not allowed. Allowed types are: {', '.join(allowed_types)}"
            raise ValueError(msg)

        # Special rule for competition datasets
        if dataset_type == DatasetTypes.COMPETITION.value and "_" not in company_name:
            msg = (
                f"For competition datasets, company name must contain at least one underscore. "
                f"The name should include the competition host or website name before '_'. "
                f"Got: '{company_name}'"
            )
            raise ValueError(msg)

    def check_date_range(self, min_date: datetime | date, max_date: datetime | date) -> None:
        """
        Validate date range.

        Requirements:
        - Both dates must be datetime or date objects
        - min_date must be before max_date
        - Dates should be reasonable (not too far in the past or future)
        - Warn if the date range is very large (> 10 years)
        """
        # Constants for date validation
        min_allowed_year = 1900
        max_allowed_year = 2100
        max_years_warning = 10

        if not isinstance(min_date, (datetime, date)):
            msg = f"min_date must be a datetime or date object. Got {type(min_date).__name__}: {min_date}"
            raise TypeError(msg)

        if not isinstance(max_date, (datetime, date)):
            msg = f"max_date must be a datetime or date object. Got {type(max_date).__name__}: {max_date}"
            raise TypeError(msg)

        # Check that min_date is before max_date
        if min_date >= max_date:
            msg = (
                f"min_date ({min_date}) must be before max_date ({max_date}). "
                f"Got a date range of {(max_date - min_date).days} days."
            )
            raise ValueError(msg)

        # Get year from either datetime or date objects
        min_year = min_date.year
        max_year = max_date.year

        # Check for reasonable date bounds
        if min_year < min_allowed_year:
            msg = f"min_date year ({min_year}) seems too early. Expected year >= {min_allowed_year}."
            raise ValueError(msg)

        if max_year > max_allowed_year:
            msg = f"max_date year ({max_year}) seems too far in the future. Expected year <= {max_allowed_year}."
            raise ValueError(msg)

        # Warn if date range is very large (more than 10 years)
        date_range_days = (max_date - min_date).days
        if date_range_days > max_years_warning * 365:  # approximately 10 years
            years = date_range_days / 365.25
            logger.warning(
                "Date range is very large: %.1f years (%d days). From %s to %s. Ensure this is on purpose.",
                years,
                date_range_days,
                min_date,
                max_date,
            )

    def check_frequency(self, frequency: int) -> None:
        """
        Validate frequency parameter.

        Args:
            frequency: The frequency integer to validate

        Raises:
            TypeError: If frequency is not an integer
            ValueError: If frequency is not in allowed values

        """
        if not isinstance(frequency, int):
            # Create a mapping for error message: {1: 'daily', 2: 'weekly', ...}
            value_to_name = {v: k for k, v in FREQUENCY_MAPPING.items()}
            allowed_values = list(FREQUENCY_MAPPING.values())
            allowed_mappings = [f"{v}={value_to_name[v]}" for v in allowed_values]
            msg = (
                f"frequency must be an integer, got {type(frequency).__name__}. "
                f"Allowed values: {', '.join(allowed_mappings)}"
            )
            raise TypeError(msg)

        allowed_values = list(FREQUENCY_MAPPING.values())
        if frequency not in allowed_values:
            # Create a mapping for error message: {1: 'daily', 2: 'weekly', ...}
            value_to_name = {v: k for k, v in FREQUENCY_MAPPING.items()}
            allowed_mappings = [f"{v}={value_to_name[v]}" for v in allowed_values]
            msg = f"frequency must be one of {allowed_values} ({', '.join(allowed_mappings)}), got {frequency}"
            raise ValueError(msg)

    def check_store_region_map(self, store_region_map: pl.DataFrame) -> None:
        print(store_region_map)

    def check_products_and_categories(
        self, categories_dict: dict, categories_level_description: pl.DataFrame, products: pl.DataFrame
    ) -> None:
        pass

    def check_time_sku_data(self, time_sku_data: pl.DataFrame, time_sku_feature_description_map: pl.DataFrame) -> None:
        pass

    def check_flags(self, flags: pl.DataFrame) -> None:
        pass

    def check_store_feature_data(
        self, store_feature_description_map: pl.DataFrame, store_feature_map: pl.DataFrame
    ) -> None:
        pass

    def check_product_feature_data(
        self, product_feature_description_map: pl.DataFrame, product_feature_map: pl.DataFrame
    ) -> None:
        pass

    def check_sku_feature_data(self, sku_feature_description_map: pl.DataFrame, sku_feature_map: pl.DataFrame) -> None:
        pass

    def check_time_product_feature_data(
        self, time_product_feature_description_map: pl.DataFrame, time_product_feature_map: pl.DataFrame
    ) -> None:
        pass

    def check_time_region_feature_data(
        self, time_region_feature_description_map: pl.DataFrame, time_region_feature_map: pl.DataFrame
    ) -> None:
        pass

    def check_time_store_feature_data(
        self, time_store_feature_description_map: pl.DataFrame, time_store_feature_map: pl.DataFrame
    ) -> None:
        pass
