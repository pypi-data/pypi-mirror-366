from pydantic import BaseModel
from pydantic import model_validator


class Fundamentals(BaseModel):
    """
    reported_earnings: float
    Reported earnings refer to the net income
    disclosed in financial statements as per regulatory standards
    (e.g., GAAP or IFRS). It reflects what the company officially
    "reports" to stakeholders.

    number_of_shares: int
    number of outstanding shares of the company.
    Treasury shares are shared bought by company and kept in
    treasury are not part of this.

    enterprise_value: float
    When you buy a company you own its “good things”
    (equity) and “bad things” (debt). The amount of “theoretical”
    money you need to buy a company and pays all its debit is called
    Enterprise value.


    """

    reported_earnings: float
    number_of_shares: int
    share_price: float
    reported_earnings_before_interest_tax_depreciation_amortization: float
    cash_and_cash_equivalents: float
    total_debt: float
    enterprise_value: float

    @model_validator(mode="before")
    def handle_enterprise_value(
        cls, values: dict[str, int | float]
    ) -> dict[str, int | float]:
        if "enterprise_value" not in values:
            values["enterprise_value"] = (
                values["number_of_shares"] * values["share_price"]
                + values["total_debt"]
                - values["cash_and_cash_equivalent"]
            )
        return values

    @property
    def market_capitalization(self) -> float:
        """Market Capitalization: The total value of a
        company's outstanding shares of stock.
        It's calculated by multiplying the current share price
        by the total number of outstanding shares.

        The `shares` attribute in Fundamentals is actually
        the "outstanding shares" of the company.
        """
        return self.number_of_shares * self.share_price

    @property
    def EBITDA(self) -> float:
        return (
            self.reported_earnings_before_interest_tax_depreciation_amortization  # noqa: E501
        )

    @property
    def enterprise_value_to_EBITDA_ratio(self) -> float:
        return (
            self.enterprise_value
            / self.reported_earnings_before_interest_tax_depreciation_amortization  # noqa: E501
        )

    @property
    def earnings_per_share(self) -> float:
        return self.reported_earnings / self.number_of_shares

    @property
    def EPS(self) -> float:
        """Returns earnings per share"""
        return self.earnings_per_share

    @property
    def price_to_earnings_ratio(self) -> float:
        return self.share_price / self.earnings_per_share

    @property
    def PE(self) -> float:
        """Returns P/E (price to earnings per share)"""
        return self.price_to_earnings_ratio
