import typing as t
from datetime import date, datetime

import polars as pl

from foundry_sdk.db_mgmt.sql_db_alchemy import SQLAlchemyDatabase

from .dataloader import DataLoader
from .validation import DataValidator

#########################################################################################################
#################################### Write nodes ########################################################
#########################################################################################################

#################################### Data input validation ########################################


def check_data_inputs(
    company_name: str,
    dataset_type: str,
    min_date: datetime | date,
    max_date: datetime | date,
    frequency: int,
    store_region_map: pl.DataFrame,
    categories_dict: dict,
    categories_level_description: pl.DataFrame,
    products: pl.DataFrame,
    time_sku_data: pl.DataFrame,
    time_sku_feature_description_map: pl.DataFrame,
    flags: pl.DataFrame,
    store_feature_description_map: pl.DataFrame,
    store_feature_map: pl.DataFrame,
    product_feature_description_map: pl.DataFrame,
    product_feature_map: pl.DataFrame,
    sku_feature_description_map: pl.DataFrame,
    sku_feature_map: pl.DataFrame,
    time_product_feature_description_map: pl.DataFrame,
    time_product_feature_map: pl.DataFrame,
    time_region_feature_description_map: pl.DataFrame,
    time_region_feature_map: pl.DataFrame,
    time_store_feature_description_map: pl.DataFrame,
    time_store_feature_map: pl.DataFrame,
) -> bool:
    # Data validation logic will be implemented here

    db = SQLAlchemyDatabase.from_kedro()
    with DataValidator(db) as data_validator:
        data_validator.check_company_name(company_name)
        data_validator.check_dataset_type(dataset_type, company_name)
        data_validator.check_date_range(min_date, max_date)
        data_validator.check_frequency(frequency)
        data_validator.check_store_region_map(store_region_map)
        data_validator.check_products_and_categories(categories_dict, categories_level_description, products)
        data_validator.check_time_sku_data(time_sku_data, time_sku_feature_description_map)
        data_validator.check_flags(flags)
        data_validator.check_store_feature_data(store_feature_description_map, store_feature_map)
        data_validator.check_product_feature_data(product_feature_description_map, product_feature_map)
        data_validator.check_sku_feature_data(sku_feature_description_map, sku_feature_map)
        data_validator.check_time_product_feature_data(time_product_feature_description_map, time_product_feature_map)
        data_validator.check_time_region_feature_data(time_region_feature_description_map, time_region_feature_map)
        data_validator.check_time_store_feature_data(time_store_feature_description_map, time_store_feature_map)

    return True


#################################### Mandatory data ############################################


def node_write_company(
    data_loader: DataLoader,
    company_name: str,
    dataset_type: str,
    description: str,
    min_date: datetime | date,
    max_date: datetime | date,
    frequency: int,
    *,
    check_passed: bool,
) -> t.Any:
    return data_loader.write_company(
        check_passed, company_name, dataset_type, description, min_date, max_date, frequency
    )


def node_write_stores(
    data_loader: DataLoader,
    store_region_map: pl.DataFrame,
    company: t.Any,
    *,
    check_passed: bool,
) -> t.Any:
    return data_loader.write_stores(check_passed, store_region_map, company)


def node_write_categories(
    data_loader: DataLoader,
    company: t.Any,
    categories_dict: dict,
    level_names: pl.DataFrame,
    *,
    check_passed: bool,
) -> t.Any:
    return data_loader.write_categories(check_passed, company, categories_dict, level_names)


def node_write_products(
    data_loader: DataLoader,
    products: pl.DataFrame,
    company_object: t.Any,
    *,
    check_passed: bool,
) -> tuple[t.Any, pl.DataFrame]:
    return data_loader.write_products(check_passed, products, company_object)


def node_write_product_categories(
    data_loader: DataLoader,
    products: pl.DataFrame,
    unique_products_df: pl.DataFrame,
    company_object: t.Any,
    category_object: t.Any,
    product_object: t.Any,
    *,
    check_passed: bool,
) -> t.Any:
    return data_loader.write_product_categories(
        check_passed, products, unique_products_df, company_object, category_object, product_object
    )


def node_write_skus(
    data_loader: DataLoader,
    time_sku_data: pl.DataFrame,
    store_object: t.Any,
    product_object: t.Any,
    company_object: t.Any,
    *,
    check_passed: bool,
) -> t.Any:
    return data_loader.write_skus(check_passed, time_sku_data, store_object, product_object, company_object)


def node_write_datapoints(
    data_loader: DataLoader,
    time_sku_data_with_sku_id: pl.DataFrame,
    *,
    check_passed: bool,
) -> t.Any:
    return data_loader.write_datapoints(check_passed, time_sku_data_with_sku_id)


def node_write_time_sku_data(
    data_loader: DataLoader,
    time_sku_feature_description_map: pl.DataFrame,
    time_sku_data_with_datapoint_id: pl.DataFrame,
    company_object: t.Any,
    *,
    create_new_time_sku_table: bool,
    check_passed: bool,
) -> t.Any:
    return data_loader.write_time_sku_data(
        check_passed,
        time_sku_feature_description_map,
        time_sku_data_with_datapoint_id,
        company_object,
        create_new_time_sku_table,
    )


def node_write_flags(
    data_loader: DataLoader,
    flags: pl.DataFrame,
    company_object: t.Any,
    time_sku_data_with_datapoint_id: pl.DataFrame,
    *,
    check_passed: bool,
) -> t.Any:
    return data_loader.write_flags(check_passed, flags, company_object, time_sku_data_with_datapoint_id)


#################################### Optional data #############################################


def node_write_store_data(
    data_loader: DataLoader,
    store_feature_description_map: pl.DataFrame,
    store_feature_map: pl.DataFrame,
    store_object: t.Any,
    company_object: t.Any,
    *,
    check_passed: bool,
) -> t.Any:
    return data_loader.write_store_data(
        check_passed, store_feature_description_map, store_feature_map, store_object, company_object
    )


def node_write_product_data(
    data_loader: DataLoader,
    product_feature_description_map: pl.DataFrame,
    product_feature_map: pl.DataFrame,
    product_object: t.Any,
    company_object: t.Any,
    *,
    check_passed: bool,
) -> t.Any:
    return data_loader.write_product_data(
        check_passed, product_feature_description_map, product_feature_map, product_object, company_object
    )


def node_write_sku_data(
    data_loader: DataLoader,
    sku_feature_description_map: pl.DataFrame,
    sku_feature_map: pl.DataFrame,
    sku_object: t.Any,
    company_object: t.Any,
    *,
    check_passed: bool,
) -> t.Any:
    return data_loader.write_sku_data(
        check_passed, sku_feature_description_map, sku_feature_map, sku_object, company_object
    )


def node_write_time_product_data(
    data_loader: DataLoader,
    time_product_feature_description_map: pl.DataFrame,
    time_product_feature_map: pl.DataFrame,
    product_object: t.Any,
    company_object: t.Any,
    *,
    check_passed: bool,
) -> t.Any:
    return data_loader.write_time_product_data(
        check_passed, time_product_feature_description_map, time_product_feature_map, product_object, company_object
    )


def node_write_time_region_data(
    data_loader: DataLoader,
    time_region_feature_description_map: pl.DataFrame,
    time_region_feature_map: pl.DataFrame,
    company_object: t.Any,
    *,
    check_passed: bool,
) -> t.Any:
    return data_loader.write_time_region_data(
        check_passed, time_region_feature_description_map, time_region_feature_map, company_object
    )


def node_write_time_store_data(
    data_loader: DataLoader,
    time_store_feature_description_map: pl.DataFrame,
    time_store_feature_map: pl.DataFrame,
    store_object: t.Any,
    company_object: t.Any,
    *,
    check_passed: bool,
) -> t.Any:
    return data_loader.write_time_store_data(
        check_passed, time_store_feature_description_map, time_store_feature_map, store_object, company_object
    )
