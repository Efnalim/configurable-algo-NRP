import pytest
from unittest.mock import patch
from src.nsp_solver.validator.conf_validator import ConfigValidator, CONF_EVAL


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "mocked_choice": CONF_EVAL.CONTINUE_EVEN_THOUGH,
                "changes_to_conf": [("h1", False)],
            },
            {"retval": CONF_EVAL.OK, "called_mocked": 0},
        ),
        (
            {
                "mocked_choice": CONF_EVAL.CONTINUE_EVEN_THOUGH,
                "changes_to_conf": [("h10", False)],
            },
            {"retval": CONF_EVAL.OK, "called_mocked": 0},
        ),
        (
            {
                "mocked_choice": CONF_EVAL.CONTINUE_EVEN_THOUGH,
                "changes_to_conf": [("h1", False), ("h10", False)],
            },
            {"retval": CONF_EVAL.OK, "called_mocked": 0},
        ),
        (
            {
                "mocked_choice": CONF_EVAL.CONTINUE_EVEN_THOUGH,
            },
            {"retval": CONF_EVAL.CONTINUE_EVEN_THOUGH, "called_mocked": 1},
        ),
        (
            {
                "mocked_choice": CONF_EVAL.STOP,
            },
            {"retval": CONF_EVAL.STOP, "called_mocked": 1},
        ),
        (
            {
                "mocked_choice": CONF_EVAL.CONTINUE_EVEN_THOUGH,
                "changes_to_conf": [("h1", False)],
                "changes_to_sc_data": [
                    ("minimalFreePeriod", 3),
                    ("maximumNumberOfConsecutiveDaysOffHard", 2),
                ],
            },
            {"retval": CONF_EVAL.CONTINUE_EVEN_THOUGH, "called_mocked": 1},
        ),
        (
            {
                "mocked_choice": CONF_EVAL.STOP,
                "changes_to_conf": [("h1", False)],
                "changes_to_sc_data": [
                    ("minimalFreePeriod", 3),
                    ("maximumNumberOfConsecutiveDaysOffHard", 2),
                ],
            },
            {"retval": CONF_EVAL.STOP, "called_mocked": 1},
        ),
        (
            {
                "mocked_choice": CONF_EVAL.STOP,
                "changes_to_conf": [("h1", False), ("h6", False)],
                "changes_to_sc_data": [
                    ("minimalFreePeriod", 3),
                    ("maximumNumberOfConsecutiveDaysOffHard", 2),
                ],
            },
            {"retval": CONF_EVAL.OK, "called_mocked": 0},
        ),
        (
            {
                "mocked_choice": CONF_EVAL.STOP,
                "changes_to_conf": [("h1", False), ("h9", False)],
                "changes_to_sc_data": [
                    ("minimalFreePeriod", 3),
                    ("maximumNumberOfConsecutiveDaysOffHard", 2),
                ],
            },
            {"retval": CONF_EVAL.OK, "called_mocked": 0},
        ),
        (
            {
                "mocked_choice": CONF_EVAL.CONTINUE_EVEN_THOUGH,
                "changes_to_conf": [("h1", False)],
                "changes_to_sc_data": [
                    ("maximumNumberOfConsecutiveWorkingDaysHard", 3),
                    ("minimumNumberOfConsecutiveWorkingDays", 4),
                ],
            },
            {"retval": CONF_EVAL.CONTINUE_EVEN_THOUGH, "called_mocked": 1},
        ),
        (
            {
                "mocked_choice": CONF_EVAL.STOP,
                "changes_to_conf": [("h1", False)],
                "changes_to_sc_data": [
                    ("maximumNumberOfConsecutiveWorkingDaysHard", 3),
                    ("minimumNumberOfConsecutiveWorkingDays", 4),
                ],
            },
            {"retval": CONF_EVAL.STOP, "called_mocked": 1},
        ),
        (
            {
                "mocked_choice": CONF_EVAL.STOP,
                "changes_to_conf": [("h1", False), ("h5", False)],
                "changes_to_sc_data": [
                    ("maximumNumberOfConsecutiveWorkingDaysHard", 3),
                    ("minimumNumberOfConsecutiveWorkingDays", 4),
                ],
            },
            {"retval": CONF_EVAL.OK, "called_mocked": 0},
        ),
        (
            {
                "mocked_choice": CONF_EVAL.STOP,
                "changes_to_conf": [("h1", False), ("s2", False)],
                "changes_to_sc_data": [
                    ("maximumNumberOfConsecutiveWorkingDaysHard", 3),
                    ("minimumNumberOfConsecutiveWorkingDays", 4),
                ],
            },
            {"retval": CONF_EVAL.OK, "called_mocked": 0},
        ),
    ],
)
def test_method_of_class(input_data, expected, data_for_1_nurse):
    with patch.object(
        ConfigValidator, "_get_user_choice", return_value=input_data["mocked_choice"]
    ) as mock_method:
        # Arrange
        validator = ConfigValidator()
        if "changes_to_conf" in input_data:
            for constraint, value in input_data["changes_to_conf"]:
                data_for_1_nurse["configuration"][constraint] = value
        if "changes_to_sc_data" in input_data:
            for var, value in input_data["changes_to_sc_data"]:
                data_for_1_nurse["sc_data"]["contracts"][-1][var] = value

        # Execute
        result = validator.evaluate_configuration(data_for_1_nurse)

        # Assert
        assert result == expected["retval"]
        if expected["called_mocked"] == 0:
            mock_method.assert_not_called()
        if expected["called_mocked"] == 1:
            mock_method.assert_called_once()
        if expected["called_mocked"] == 2:
            mock_method.assert_called()
