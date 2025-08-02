import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import fsolve  # type: ignore

from xarizmi.fundamentals.data_models import FormulaTuple


def generate_discounted_cash_formula(
    year: int, cf: float, kind: str | None = None
) -> FormulaTuple:
    if kind is None:
        formula_string = f"{cf}/(1+r)^{year}"

        def discount_cash_formula(r: float) -> float:
            return cf / (1 + r) ** year

        return FormulaTuple(discount_cash_formula, formula_string)
    elif kind == "perpetuity":
        formula_string = f"{cf}/r/(1+r)^{year - 1}"

        def discount_cash_formula(r: float) -> float:
            return cf / r / (1 + r) ** (year - 1)

        return FormulaTuple(discount_cash_formula, formula_string)
    else:
        raise NotImplementedError()


def generate_terminal_compounding_cash_formula(
    year: int, cf: float, terminal_year: int, kind: str | None = None
) -> FormulaTuple:
    if kind is None:
        formula_string = f"{cf} * (1+r)^{terminal_year - year}"

        def compounding_formula(r: float) -> float:
            return cf * (1 + r) ** (terminal_year - year)

        return FormulaTuple(compounding_formula, formula_string)
    elif kind == "perpetuity":
        formula_string = f"{cf}/r * (1+r)^{terminal_year - year - 1}"

        def compounding_formula(r: float) -> float:
            return cf / r * (1 + r) ** (terminal_year - year - 1)

        return FormulaTuple(compounding_formula, formula_string)
    else:
        raise NotImplementedError()


class IRR:

    def __init__(
        self,
        years: list[int],
        cfs: list[float],
        kinds: list[str | None] | None = None,
        opportunity_cost: None | float = None,
    ) -> None:
        if kinds is None:
            kinds = [None] * len(years)
        assert len(years) == len(cfs) and len(cfs) == len(kinds)
        self._years = years
        self._cfs = cfs
        self._kinds = kinds
        self._opportunity_cost = opportunity_cost
        self._formula_tuple = self._process()

    @property
    def years(self) -> list[int]:
        return self._years

    @property
    def opportunity_cost(self) -> None | float:
        return self._opportunity_cost

    @property
    def cfs(self) -> list[float]:
        return self._cfs

    @property
    def kinds(self) -> list[str | None]:
        return self._kinds

    @property
    def formula(self) -> FormulaTuple:
        return self._formula  # type: ignore

    @property
    def formula_string(self) -> str:
        return self._formula_string  # type: ignore

    def _process(self) -> FormulaTuple:
        func_list = []
        func_string_list = []
        for year, cf, kind in zip(self.years, self.cfs, self.kinds):
            func_list.append(
                generate_discounted_cash_formula(year, cf, kind).formula
            )
            func_string_list.append(
                generate_discounted_cash_formula(year, cf, kind).formula_string
            )
        formula_string = "+".join(func_string_list)

        def formula(r: float) -> float:
            return sum(f(r) for f in func_list)  # type: ignore

        formula_tuple = FormulaTuple(formula, formula_string)
        self._formula = formula_tuple.formula
        self._formula_string = formula_tuple.formula_string
        return formula_tuple

    def find_mirr(self, precision: int = 4) -> float:
        """Returns Modified IRR"""
        if self.opportunity_cost is None:
            raise ValueError(
                "To calculate MIRR you need to provide"
                " opportunity cost in IRR constructor"
            )
        func_list = []
        terminal_year = max(self.years)
        initial_investment = abs(
            sum(cf for year, cf in zip(self.years, self.cfs) if year == 0)
        )
        for year, cf, kind in zip(self.years, self.cfs, self.kinds):
            if year == 0:
                continue
            func_list.append(
                generate_terminal_compounding_cash_formula(
                    year, cf, terminal_year, kind
                ).formula
            )

        def F(r: float) -> float:
            return sum(f(r) for f in func_list)  # type: ignore

        mirr = (F(self.opportunity_cost) / initial_investment) ** (
            1 / terminal_year
        ) - 1
        return round(mirr, precision)  # type: ignore

    def __str__(self) -> str:
        return f"Formula = {self.formula_string}"

    def __repr__(self) -> str:
        s = "IRRFormula(\n"
        s += f"years={self.years},\n"
        s += f"cfs={self.cfs},\n"
        s += f"kinds={self.kinds},\n"
        s += ")"
        return s

    def find(self, initial_guess: float = 0.1, precision: int = 4) -> float:
        solution = fsolve(self._formula, initial_guess)[0]
        return round(solution, precision)  # type: ignore

    def find_all(
        self,
        min_r: float | int = 0,
        max_r: float | int = 1,
        max_n_roots: int = 2,
        precision: int = 4,
    ) -> list[set[float]]:
        initial_guesses = np.linspace(min_r, max_r, max_n_roots)
        solutions = fsolve(self._formula, initial_guesses)
        solutions = [round(item, precision) for item in solutions]
        return list(set(solutions))

    def get_yield_curve(
        self, min_r: float | int = 0, max_r: float | int = 1, points: int = 100
    ) -> tuple[list[float], list[float]]:
        assert min_r < max_r
        assert type(points) is int
        xs = np.linspace(min_r, max_r, points)
        ys = self.formula(xs)  # type: ignore
        return xs.tolist(), ys.tolist()

    def plot(
        self,
        min_r: float = 0,
        max_r: float = 1,
        points: int = 100,
        figsize: tuple[int | float, int | float] = (10, 5),
        title: str = "Yield Curve",
        plot_label: str = "Yield",
        y_label: str = "NPV",
        x_label: str = "Return Rate",
        color: str = "blue",
        x_in_percentage: bool = True,
        grid: bool = True,
    ) -> None:
        xs, ys = self.get_yield_curve(min_r=min_r, max_r=max_r, points=points)
        if x_in_percentage:
            xs = [100 * x for x in xs]
            x_label = x_label + " (%)"
        fig, ax = plt.subplots(figsize=figsize)
        _ = ax.plot(xs, ys, label=plot_label, color=color)
        _ = ax.set_title(title)
        _ = ax.set_ylabel(y_label)
        _ = ax.set_xlabel(x_label)
        if grid is True:
            ax.grid()
        return fig, ax  # type: ignore
