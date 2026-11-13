import pandas as pd
import pytest

from solution import add_virtual_column


def test_sum_of_two_columns():
    df = pd.DataFrame([[1, 1]] * 2, columns = ["label_one", "label_two"])
    df_expected = pd.DataFrame([[1, 1, 2]] * 2, columns = ["label_one", "label_two", "label_three"])
    df_result = add_virtual_column(df, "label_one+label_two", "label_three")
    assert df_result.equals(df_expected), f"The function should sum the columns: label_one and label_two.\n\nResult:\n\n{df_result}\n\nExpected:\n\n{df_expected}"


def test_multiplication_of_two_columns():
    df = pd.DataFrame([[1, 1]] * 2, columns = ["label_one", "label_two"])
    df_expected = pd.DataFrame([[1, 1, 1]] * 2, columns = ["label_one", "label_two", "label_three"])
    df_result = add_virtual_column(df, "label_one * label_two", "label_three")
    assert df_result.equals(df_expected), f"The function should multiply the columns: label_one and label_two.\n\nResult:\n\n{df_result}\n\nExpected:\n\n{df_expected}"


def test_subtraction_of_two_columns():
    df = pd.DataFrame([[1, 1]] * 2, columns = ["label_one", "label_two"])
    df_expected = pd.DataFrame([[1, 1, 0]] * 2, columns = ["label_one", "label_two", "label_three"])
    df_result = add_virtual_column(df, "label_one - label_two", "label_three")
    assert df_result.equals(df_expected), f"The function should subtract the columns: label_one and label_two.\n\nResult:\n\n{df_result}\n\nExpected:\n\n{df_expected}"


def test_empty_result_when_invalid_labels():
    df = pd.DataFrame([[1, 2]] * 3, columns = ["label_one", "label_two"])
    df_result = add_virtual_column(df, "label_one + label_two", "label3")
    assert df_result.empty, f"Should return an empty df when the \"new_column\" is invalid.\n\nResult:\n\n{df_result}\n\nExpected:\n\nEmpty df"


def test_empty_result_when_invalid_rules():
    df = pd.DataFrame([[1, 1]] * 2, columns = ["label_one", "label_two"])
    df_result = add_virtual_column(df, "label&one + label_two", "label_three")
    assert df_result.empty, f"Should return an empty df when the role have invalid character: '&'.\n\nResult:\n\n{df_result}\n\nExpected:\n\nEmpty df"
    df_result = add_virtual_column(df, "label_five + label_two", "label_three")
    assert df_result.empty, f"Should return an empty df when the role have a column which isn't in the df: 'label_five'.\n\nResult:\n\n{df_result}\n\nExpected:\n\nEmpty df"


def test_when_extra_spaces_in_rules():
    df = pd.DataFrame([[1, 1]] * 2, columns = ["label_one", "label_two"])
    df_expected = pd.DataFrame([[1, 1, 2]] * 2, columns = ["label_one", "label_two", "label_three"])
    df_result = add_virtual_column(df, "label_one + label_two ", "label_three")
    assert df_result.equals(df_expected), f"Should work when the role have spaces between the operation and the column.\n\nResult:\n\n{df_result}\n\nExpected:\n\n{df_expected}"
    df_result = add_virtual_column(df, "  label_one + label_two ", "label_three")
    assert df_result.equals(df_expected), f"Should work when the role have extra spaces in the start/end.\n\nResult:\n\n{df_result}\n\nExpected:\n\n{df_expected}"

# New tests

def test_empty_result_when_invalid_new_column_name():
    df = pd.DataFrame([[1, 2]], columns=["label_one", "label_two"])

    result = add_virtual_column(df, "label_one + label_two", "label-three")

    assert result.empty


def test_add_virtual_column_does_not_modify_input():
    df = pd.DataFrame([[2, 3]], columns=["label_one", "label_two"])

    add_virtual_column(df, "label_one * label_two", "label_three")

    assert list(df.columns) == ["label_one", "label_two"]


def test_power_operator():
    df = pd.DataFrame([[2, 3], [4, 2]], columns=["label_one", "label_two"])

    result = add_virtual_column(df, "label_one ** label_two", "label_three")

    expected = pd.DataFrame(
        [[2, 3, 8], [4, 2, 16]],
        columns=["label_one", "label_two", "label_three"],
    )
    pd.testing.assert_frame_equal(result, expected)


def test_division_operator():
    df = pd.DataFrame([[6, 3], [9, 2]], columns=["label_one", "label_two"])

    result = add_virtual_column(df, "label_one / label_two", "label_three")

    expected = pd.DataFrame(
        [[6, 3, 2.0], [9, 2, 4.5]],
        columns=["label_one", "label_two", "label_three"],
    )
    pd.testing.assert_frame_equal(result, expected)


def test_parentheses_change_operation_order():
    df = pd.DataFrame([[2, 3], [4, 5]], columns=["label_one", "label_two"])

    result = add_virtual_column(
        df,
        "(label_one + label_two) * 2",
        "label_three",
    )

    expected = pd.DataFrame(
        [[2, 3, 10], [4, 5, 18]],
        columns=["label_one", "label_two", "label_three"],
    )
    pd.testing.assert_frame_equal(result, expected)


def test_expression_can_add_numeric_constant():
    df = pd.DataFrame([[2], [4]], columns=["label_one"])

    result = add_virtual_column(df, "label_one + 10", "label_two")

    expected = pd.DataFrame(
        [[2, 12], [4, 14]],
        columns=["label_one", "label_two"],
    )
    pd.testing.assert_frame_equal(result, expected)


def test_complex_expression_with_parentheses_and_constants():
    df = pd.DataFrame(
        [[2, 3], [4, 5]],
        columns=["label_one", "label_two"],
    )

    result = add_virtual_column(
        df,
        "(label_one + 10) * (label_two - 1) / 2",
        "label_three",
    )

    expected = pd.DataFrame(
        [[2, 3, 12.0], [4, 5, 28.0]],
        columns=["label_one", "label_two", "label_three"],
    )
    pd.testing.assert_frame_equal(result, expected)


@pytest.mark.parametrize("role", ["sin(label_one)", "sqrt(label_one)"])
def test_math_functions_are_rejected(role):
    df = pd.DataFrame([[1, 4]], columns=["label_one", "label_two"])

    result = add_virtual_column(df, role, "label_three")

    assert result.empty