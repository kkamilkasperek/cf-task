import pandas as pd

from solution import add_virtual_column


def prepare_numeric_columns(
    frame: pd.DataFrame,
    numeric_columns: list[str],
) -> pd.DataFrame:
    prepared = frame.copy()

    for column in numeric_columns:
        values = (
            prepared[column].astype("string").str.strip()
            .str.replace(r"\s+", "", regex=True)
        )
        empty_values = values.isna() | values.eq("")
        converted = pd.to_numeric(
            values.str.replace(",", ".", regex=False),
            errors="coerce",
        )
        prepared[column] = (
            converted.mask(empty_values, 0).abs().round(2).astype("float64")
        )

    return prepared.dropna(subset=numeric_columns)


def main() -> None:
    sales = pd.read_csv("sales.csv")
    sales.columns = sales.columns.str.strip().str.replace(" ", "_", regex=False)

    # Delete rows, containing duplicated header
    sales = sales.loc[
        ~sales["Order_ID"].astype("string").str.strip().eq("Order_ID")
    ].copy()

    # Delete the last row, which contains aggregated values
    sales = sales.iloc[:-1].copy()

    sales["Region"] = sales["Region"].astype("string").str.strip().str.capitalize()

    numeric_columns = ["Quantity", "Unit_Price", "Discount"]
    sales = prepare_numeric_columns(sales, numeric_columns)

    sales = add_virtual_column(
        sales,
        "Quantity * Unit_Price - Discount",
        "Revenue",
    )
    sales["Revenue"] = sales["Revenue"]

    revenue_by_region = sales.groupby("Region", as_index=False)["Revenue"].sum()
    revenue_by_region.to_csv("revenue_by_region.csv", index=False)

    print(sales)


if __name__ == "__main__":
    main()
