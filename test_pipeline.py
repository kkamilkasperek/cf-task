import pandas as pd

from pipeline import prepare_numeric_columns


def test_prepare_numeric_columns_normalizes_values():
    df = pd.DataFrame(
        {
            "quantity": ["1 762", "-2", ""],
            "price": ["12,346", " 9.999 ", None],
        }
    )

    result = prepare_numeric_columns(df, ["quantity", "price"])

    expected = pd.DataFrame(
        {
            "quantity": [1762.00, 2.00, 0.00],
            "price": [12.35, 10.00, 0.00],
        }
    )
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


def test_prepare_numeric_columns_drops_invalid_numeric_rows():
    df = pd.DataFrame(
        {
            "quantity": ["1", "not-a-number"],
            "price": ["2", "3"],
        }
    )

    result = prepare_numeric_columns(df, ["quantity", "price"])

    expected_valid_row = pd.DataFrame(
        {"quantity": [1.0], "price": [2.0]},
        index=[0],
    )
    pd.testing.assert_frame_equal(result.loc[[0]], expected_valid_row)
    assert 1 not in result.index
