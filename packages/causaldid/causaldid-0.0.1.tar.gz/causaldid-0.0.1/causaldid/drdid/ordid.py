"""Wrapper for outcome regression DiD estimators."""

from typing import Any, Literal, NamedTuple

import numpy as np
import pandas as pd

from .estimators.reg_did_panel import reg_did_panel
from .estimators.reg_did_rc import reg_did_rc
from .print import print_did_result
from .utils import preprocess_drdid


class ORDIDResult(NamedTuple):
    """Result from the outcome regression DiD estimator."""

    att: float
    se: float
    uci: float
    lci: float
    boots: np.ndarray | None
    att_inf_func: np.ndarray | None
    call_params: dict[str, Any]
    args: dict[str, Any]


ORDIDResult = print_did_result(ORDIDResult)


def ordid(
    data: pd.DataFrame,
    y_col: str,
    time_col: str,
    treat_col: str,
    id_col: str | None = None,
    covariates_formula: str | None = None,
    panel: bool = True,
    weights_col: str | None = None,
    boot: bool = False,
    boot_type: Literal["weighted", "multiplier"] = "weighted",
    n_boot: int = 999,
    inf_func: bool = False,
) -> ORDIDResult:
    r"""Wrap the outcome regression DiD estimators for the ATT.

    This function is a wrapper for outcome regression DiD estimators.
    It calls the appropriate estimator based on the panel argument and
    performs pre-processing for the data.

    Parameters
    ----------
    data : pd.DataFrame
        The input data containing outcome, time, unit ID, treatment,
        and optionally covariates and weights.
    y_col : str
        Name of the column containing the outcome variable.
    time_col : str
        Name of the column containing the time periods (must have exactly 2 periods).
    treat_col : str
        Name of the column containing the treatment group indicator.
        For panel data: time-invariant indicator (1 if ever treated, 0 if never treated).
        For repeated cross-sections: treatment status in the post-period.
    id_col : str | None, default None
        Name of the column containing the unit ID. Required if panel=True.
    covariates_formula : str | None, default None
        A formula for the covariates to include in the model.
        Should be of the form "~ X1 + X2" (intercept is always included).
        If None, equivalent to "~ 1" (intercept only).
    panel : bool, default True
        Whether the data is panel (True) or repeated cross-sections (False).
        Panel data should be in long format with each row representing
        a unit-time observation.
    weights_col : str | None, default None
        Name of the column containing sampling weights.
        If None, all observations have equal weight.
        Weights are normalized to have mean 1.
    boot : bool, default False
        Whether to compute bootstrap standard errors.
    boot_type : {"weighted", "multiplier"}, default "weighted"
        Type of bootstrap to perform (only relevant if boot=True).
    n_boot : int, default 999
        Number of bootstrap repetitions (only relevant if boot=True).
    inf_func : bool, default False
        Whether to return the influence function values.

    Returns
    -------
    ORDIDResult
        NamedTuple containing:

        - *att*: The OR DiD point estimate.
        - *se*: The OR DiD standard error.
        - *uci*: The upper bound of a 95% confidence interval.
        - *lci*: The lower bound of a 95% confidence interval.
        - *boots*: Bootstrap draws of the ATT if boot=True.
        - *att_inf_func*: Influence function values if inf_func=True.
        - *call_params*: Original function call parameters.
        - *args*: Arguments used in the estimation.

    Examples
    --------
    Estimate the average treatment effect on the treated (ATT) using outcome regression
    with panel data from a job training program. The outcome regression approach models
    the conditional expectation of the outcome given covariates.

    .. ipython::

        In [1]: import causaldid
           ...: from causaldid.data import load_nsw
           ...:
           ...: nsw_data = load_nsw()
           ...:
           ...: att_result = causaldid.ordid(
           ...:     data=nsw_data,
           ...:     y_col="re",
           ...:     time_col="year",
           ...:     treat_col="experimental",
           ...:     id_col="id",
           ...:     panel=True,
           ...:     covariates_formula="~ age + educ + black + married + nodegree + hisp + re74",
           ...: )

        In [2]: print(att_result)

    For more robust inference, we can use weighted-bootstrap standard errors with
    propensity score trimming to handle extreme weights.

    .. ipython::
        :okwarning:

        In [3]: att_result_rc_boot = causaldid.ordid(
           ...:     data=nsw_data,
           ...:     y_col="re",
           ...:     time_col="year",
           ...:     treat_col="experimental",
           ...:     id_col="id",
           ...:     panel=True,
           ...:     covariates_formula="~ age + educ + black + married + nodegree + hisp + re74",
           ...:     boot=True,
           ...: )

        In [4]: print(att_result_rc_boot)

    Notes
    -----
    The outcome regression DiD estimator is based on a linear regression model for
    the outcome conditional on covariates, time period, and treatment status. For
    panel data, it estimates the ATT by comparing the change in outcomes for treated
    units to the predicted change for control units based on their covariate values.

    This estimator assumes that the conditional expectation function is correctly
    specified and that the parallel trends assumption holds conditional on covariates.
    Unlike the doubly robust estimator, it is not robust to misspecification of the
    outcome regression model.

    See Also
    --------
    drdid : Doubly robust DiD estimator.
    ipwdid : Inverse propensity weighted DiD estimator.

    References
    ----------
    .. [1] Heckman, J., Ichimura, H., and Todd, P. (1997),
           "Matching as an Econometric Evaluation Estimator: Evidence from
           Evaluating a Job Training Programme", Review of Economic Studies,
           vol. 64(4), p. 605–654. https://doi.org/10.2307/2971733

    .. [2] Sant'Anna, P. H. C. and Zhao, J. (2020),
           "Doubly Robust Difference-in-Differences Estimators."
           Journal of Econometrics, Vol. 219 (1), pp. 101-122.
           https://doi.org/10.1016/j.jeconom.2020.06.003
    """
    if panel and id_col is None:
        raise ValueError("id_col must be provided when panel=True")

    call_params = {
        "y_col": y_col,
        "time_col": time_col,
        "treat_col": treat_col,
        "id_col": id_col,
        "covariates_formula": covariates_formula,
        "data_shape": data.shape,
        "panel": panel,
        "weights_col": weights_col,
        "boot": boot,
        "boot_type": boot_type,
        "n_boot": n_boot,
        "inf_func": inf_func,
    }

    dp = preprocess_drdid(
        data=data,
        y_col=y_col,
        time_col=time_col,
        id_col=id_col if panel else "dummy_id",  # Dummy ID for RC data
        treat_col=treat_col,
        covariates_formula=covariates_formula,
        panel=panel,
        weights_col=weights_col,
        boot=boot,
        boot_type=boot_type,
        n_boot=n_boot,
        inf_func=inf_func,
    )

    if panel:
        result = reg_did_panel(
            y1=dp["y1"],
            y0=dp["y0"],
            d=dp["D"],
            covariates=dp["covariates"],
            i_weights=dp["weights"],
            boot=boot,
            boot_type=boot_type,
            nboot=n_boot,
            influence_func=inf_func,
        )
    else:
        result = reg_did_rc(
            y=dp["y"],
            post=dp["post"],
            d=dp["D"],
            covariates=dp["covariates"],
            i_weights=dp["weights"],
            boot=boot,
            boot_type=boot_type,
            nboot=n_boot,
            influence_func=inf_func,
        )

    args = result.args.copy()
    args.update(
        {
            "panel": panel,
            "normalized": True,
            "boot": boot,
            "boot_type": boot_type,
            "nboot": n_boot,
            "type": "or",
        }
    )

    return ORDIDResult(
        att=result.att,
        se=result.se,
        uci=result.uci,
        lci=result.lci,
        boots=result.boots,
        att_inf_func=result.att_inf_func,
        call_params=call_params,
        args=args,
    )
