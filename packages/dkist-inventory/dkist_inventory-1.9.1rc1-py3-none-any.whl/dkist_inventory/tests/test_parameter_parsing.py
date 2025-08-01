import datetime

import pytest

from dkist_inventory.parameter_parsing import ParameterParser


@pytest.fixture
def input_data_list():
    # Fixture with two parameters, one with two values
    return [
        {
            "parameterName": "parameter_1",
            "parameterValues": [
                {
                    "parameterValue": "value1",
                    "parameterValueId": 1,
                    "parameterValueStartDate": "2023-01-01T00:00:00",
                },
                {
                    "parameterValue": "value2",
                    "parameterValueId": 2,
                    "parameterValueStartDate": "2023-02-01T00:00:00",
                },
                {
                    "parameterValue": "value3",
                    "parameterValueId": 3,
                    "parameterValueStartDate": "2023-05-01T00:00:00",
                },
            ],
        },
        {
            "parameterName": "parameter_2",
            "parameterValues": [
                {
                    "parameterValue": "value3",
                    "parameterValueId": 4,
                    "parameterValueStartDate": "2023-03-01T00:00:00",
                }
            ],
        },
    ]


@pytest.fixture
def input_json_string():
    # Fixture with two parameters, one with two values as a JSON string
    return """[
        {
            "parameterName": "parameter_1",
            "parameterValues": [
                {"parameterValue": "value1", "parameterValueId": 1, "parameterValueStartDate": "2023-01-01T00:00:00"},
                {"parameterValue": "value2", "parameterValueId": 2, "parameterValueStartDate": "2023-02-01T00:00:00"}
            ]
        },
        {
            "parameterName": "parameter_2",
            "parameterValues": [
                {"parameterValue": "value4", "parameterValueId": 3, "parameterValueStartDate": "2023-03-01T00:00:00"}
            ]
        }
    ]"""


@pytest.fixture
def input_data_multiple_values():
    # Fixture with one parameter with two values, and multiple values
    return [
        {
            "parameterName": "visp_background_continuum_index",
            "parameterValues": [
                {
                    "parameterValue": '{"values": [1, 2, 3], "wavelength": [100, 200, 300]}',
                    "parameterValueId": 1,
                    "parameterValueStartDate": "2023-01-01T00:00:00",
                },
                {
                    "parameterValue": '{"values": [4, 5, 6], "wavelength": [100, 200, 300]}',
                    "parameterValueId": 2,
                    "parameterValueStartDate": "2023-02-01T00:00:00",
                },
            ],
        }
    ]


@pytest.fixture
def dataset_date_str():
    """Fixture with a dataset start date as a string"""
    return "2023-02-15T00:00:00"


@pytest.fixture
def dataset_date_datetime():
    """Fixture with a dataset start date as a datetime object"""
    return datetime.datetime(2023, 2, 15, 0, 0, 0)


@pytest.fixture
def dataset_date_late_datetime():
    """Fixture with a dataset start date as a datetime object"""
    return datetime.datetime(2024, 2, 15, 0, 0, 0)


@pytest.fixture
def dataset_date_early_datetime():
    """Fixture with a dataset start date as a datetime object"""
    return datetime.datetime(2022, 2, 15, 0, 0, 0)


@pytest.fixture
def dataset_date_exact_datetime():
    """Fixture with a dataset start date as a datetime object"""
    return datetime.datetime(2023, 2, 1, 0, 0, 0)


# Tests
def test_filter_one_valid_with_list(input_data_list, dataset_date_str):
    """
    Test that filters with one valid and one invalid parameter value.

    :Given: Two parameters, one with multiple parameter values in a JSON object.
    :When: Earlier values for the parameter value and values later than dataset start date are filtered out.
    :Then: The JSON object contains only one valid parameter.
    """
    # Given
    expected_output = [
        {
            "parameterName": "parameter_1",
            "parameterValues": [
                {
                    "parameterValue": "value2",
                    "parameterValueId": 2,
                    "parameterValueStartDate": "2023-02-01T00:00:00",
                }
            ],
        },
    ]

    # When/Then
    # Date used 2023-02-15T00:00:00
    assert (
        ParameterParser(
            parameters=input_data_list, dataset_date=dataset_date_str
        ).filtered_parameters
        == expected_output
    )


# Tests
def test_filter_all_valid_with_list(input_data_list, dataset_date_late_datetime):
    """
    Test that filters with two parameter values, both with valid values.

    :Given: Two parameters, both with multiple parameter values in a JSON object.
    :When: Earlier values for the parameter value are filtered out.
    :Then: The JSON object contains two valid parameters.
    """
    # Given
    expected_output = [
        {
            "parameterName": "parameter_1",
            "parameterValues": [
                {
                    "parameterValue": "value3",
                    "parameterValueId": 3,
                    "parameterValueStartDate": "2023-05-01T00:00:00",
                }
            ],
        },
        {
            "parameterName": "parameter_2",
            "parameterValues": [
                {
                    "parameterValue": "value3",
                    "parameterValueId": 4,
                    "parameterValueStartDate": "2023-03-01T00:00:00",
                }
            ],
        },
    ]

    # When/Then
    # Date used 2024-02-15T00:00:00
    assert (
        ParameterParser(
            parameters=input_data_list,
            dataset_date=dataset_date_late_datetime,
        ).filtered_parameters
        == expected_output
    )


def test_filter_latest_with_datetime(input_data_list, dataset_date_datetime):
    """
    Test that ensures filtering works with a dataset date provided as a datetime object.

    :Given: Two parameters, one with multiple parameter values.
    :When: Filtering is applied with a dataset start date as a datetime object.
    :Then: The correct latest parameter value before the dataset date is returned.
    """
    # Given
    expected_output = [
        {
            "parameterName": "parameter_1",
            "parameterValues": [
                {
                    "parameterValue": "value2",
                    "parameterValueId": 2,
                    "parameterValueStartDate": "2023-02-01T00:00:00",
                }
            ],
        },
    ]

    # When/Then
    # Date used 2023-02-15T00:00:00
    assert (
        ParameterParser(
            parameters=input_data_list, dataset_date=dataset_date_datetime
        ).filtered_parameters
        == expected_output
    )


def test_filter_latest_with_empty_list(input_data_list):
    """
    Test that ensures an empty list input returns an empty list.

    :Given: An empty list as input.
    :When: The filter_latest_parameter_values method is called.
    :Then: The output should be an empty list.
    """
    assert (
        ParameterParser(parameters=[], dataset_date="2023-02-15T00:00:00").filtered_parameters == []
    )


def test_filter_latest_with_earlier_dataset_date(input_data_list, dataset_date_early_datetime):
    """
    Test that ensures filtering works correctly when the dataset date is earlier than all parameter values.

    :Given: A dataset date before all parameter start dates.
    :When: The filter_latest_parameter_values method is called.
    :Then: The output should be an empty list since no values exist before the dataset date.
    """

    # When/Then
    # Date used 2022-02-15T00:00:00
    assert (
        ParameterParser(
            parameters=input_data_list,
            dataset_date=dataset_date_early_datetime,
        ).filtered_parameters
        == []
    )


def test_filter_latest_with_exact_match(input_data_list, dataset_date_exact_datetime):
    """
    Test that ensures filtering correctly selects a parameter value that exactly matches the dataset start date.

    :Given: A dataset date matching a parameter value's start date.
    :When: The filter_latest_parameter_values method is called.
    :Then: The exact matching value should be selected.
    """
    # Given
    expected_output = [
        {
            "parameterName": "parameter_1",
            "parameterValues": [
                {
                    "parameterValue": "value2",
                    "parameterValueId": 2,
                    "parameterValueStartDate": "2023-02-01T00:00:00",
                }
            ],
        },
    ]

    # When/Then
    # Date used 2022-02-01T00:00:00
    assert (
        ParameterParser(
            parameters=input_data_list,
            dataset_date=dataset_date_exact_datetime,
        ).filtered_parameters
        == expected_output
    )
