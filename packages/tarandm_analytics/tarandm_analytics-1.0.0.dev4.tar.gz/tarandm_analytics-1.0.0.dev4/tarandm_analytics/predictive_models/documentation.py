from typing import Optional, List, Tuple, TYPE_CHECKING, cast

import structlog

from tarandm_analytics.predictive_models.attribute_preprocessing.attribute_binning import (
    AbstractAttributeBin,
    AttributeBinCategorical,
    AttributeBinNumerical,
    AttributeDataType,
    PredictiveModelBinName,
)
from tarandm_analytics.models.extended_predictive_model import ExtendedPredictiveModel
from tarandm_analytics_utils.predictive_models.extended_predictive_model import PredictiveModelType

if TYPE_CHECKING:
    import pandas as pd


logger = structlog.get_logger(__name__)


def logistic_regression_output(
    model: ExtendedPredictiveModel, data: "pd.DataFrame", target: str, value_is_woe: bool = True
) -> "pd.DataFrame":
    import numpy as np

    scorecard = []
    if model.predictive_model_type != PredictiveModelType.LOGISTIC_REGRESSION:
        raise TypeError("Model must be of class ModelLogisticRegression.")

    # models's beta coefficients
    betas = model.get_external_model_coefficients()

    # add attributes and their bins to the scorecard
    i = 0
    for attribute in model.attributes:
        matched_binnings = [
            binning for binning in model.attribute_preprocessing.binning if binning.attribute == attribute
        ]
        if len(matched_binnings) == 0:
            # if no binning for attribute is found, add only one line with beta coefficient
            scorecard += [(attribute, betas[i], "-", np.nan, np.nan, np.nan, np.nan)]
            i += 1
            continue

        bins_to_card = []
        binning = matched_binnings[0]
        for b in binning.attribute_binning:
            bin_name = b.name
            bin_value = b.value
            bin_bads, bin_freq, bin_dr = get_bin_stats(
                data=data,
                attribute=attribute,
                bin=b,
                attribute_data_type=binning.attribute_data_type,
                target=target,
            )
            bins_to_card += [(attribute, betas[i], bin_name, bin_value, bin_bads, bin_freq, bin_dr)]

        scorecard += bins_to_card  # type: ignore
        i += 1

    import pandas as pd

    scorecard = pd.DataFrame(
        scorecard,
        columns=[
            "Predictor",
            "Coeff",
            "Bin",
            "WOE" if value_is_woe else "Value",
            "Bad count",
            "Total count",
            "Default rate",
        ],
    )
    return scorecard


def get_bin_stats(
    data: "pd.DataFrame",
    attribute: str,
    bin: AbstractAttributeBin,
    attribute_data_type: AttributeDataType,
    target: str,
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    import numpy as np

    if bin.name not in [
        PredictiveModelBinName.DEFAULT,
        PredictiveModelBinName.DEFINED_DEFAULT,
        PredictiveModelBinName.SYSTEM_DEFAULT,
        PredictiveModelBinName.NULL,
    ]:
        if attribute_data_type == AttributeDataType.NUMERICAL:
            bin = cast(AttributeBinNumerical, bin)
            temp = data[(data[attribute] > bin.lower_bound) & (data[attribute] <= bin.upper_bound)]
        elif attribute_data_type == AttributeDataType.CATEGORICAL:
            bin = cast(AttributeBinCategorical, bin)
            temp = data[data[attribute].isin(bin.categories)]
        else:
            return None, np.nan, np.nan
    else:
        if bin.name == PredictiveModelBinName.NULL:
            temp = data[data[attribute].isnull()]
        else:
            return None, np.nan, np.nan

    bin_freq = len(temp)
    bin_bads = temp[target].sum()
    bin_dr = temp[target].sum() / len(temp)

    return bin_bads, bin_freq, bin_dr


def plot_hist_with_default_rates(
    dt: "pd.DataFrame",
    col_target_count: str,
    col_total_count: str,
    col_target_rate: str,
    col_bin_name: str,
    attribute: str,
    add_score_calibration: bool = False,
    col_expected_target_rate: str = "expected_target_rate",
    save_to_path: Optional[str] = None,
) -> None:
    import matplotlib.pyplot as plt

    ax1 = plt.subplot(111)
    ax1.bar(range(len(dt)), dt[col_target_count], color="coral", label="bads")
    ax1.bar(
        range(len(dt)),
        dt[col_total_count] - dt[col_target_count],
        bottom=dt[col_target_count],
        color="lightblue",
        label="goods",
    )
    rotation = 90 if len(dt) > 10 else 45
    plt.xticks(range(len(dt)), dt[col_bin_name], rotation=rotation)
    ax1.tick_params(axis="x", colors="gray")
    ax1.tick_params(axis="y", colors="gray")
    ax1.spines["top"].set_visible(False)
    ax1.set_ylabel("Observation count".upper(), verticalalignment="center_baseline", y=0.75, labelpad=12)

    plt.title(attribute, pad=20)
    plt.legend(loc="upper left", frameon=False)

    from matplotlib.axes import Axes

    ax2: Axes = ax1.twinx()
    ax2.spines["top"].set_visible(False)
    ax2.spines["left"].set_color("lightgray")
    ax2.spines["right"].set_color("lightgray")
    ax2.spines["bottom"].set_color("lightgray")
    ax2.tick_params(axis="x", colors="gray")
    ax2.tick_params(axis="y", colors="gray")

    ax2.plot(range(len(dt)), dt[col_target_rate], ls="--", marker="o", color="red")
    if add_score_calibration:
        ax2.plot(range(len(dt)), dt[col_expected_target_rate], ls="--", color="gray")

    ax2.set_ylabel("Default rate".upper(), color="red", verticalalignment="center_baseline", y=0.84, labelpad=-40)

    if save_to_path is not None:
        plt.savefig(save_to_path)

    xlim = ax1.get_xlim()
    ax2.set_xlim((xlim[0], xlim[1] + (xlim[1] - xlim[0]) * 0.03))
    plt.show()


def attribute_binning_plot(scorecard: "pd.DataFrame", attribute: str, save_to_path: Optional[str] = None) -> None:
    dt = scorecard[(scorecard["Predictor"] == attribute) & (scorecard["Total count"] > 0)]
    if len(dt) == 0:
        raise ValueError(f"No binning found in scorecard for attribute {attribute}.")

    plot_hist_with_default_rates(
        dt=dt,
        col_target_count="Bad count",
        col_total_count="Total count",
        col_target_rate="Default rate",
        col_bin_name="Bin",
        attribute=attribute,
        save_to_path=save_to_path,
    )


def attribute_histogram(
    data: "pd.DataFrame",
    attribute: str,
    target: str,
    n_bins: int = 25,
    add_score_calibration: bool = False,
    save_to_path: Optional[str] = None,
) -> None:
    dt = data[data[attribute].notnull()]
    equidist = [
        dt[attribute].min() + i * (dt[attribute].max() - dt[attribute].min()) / n_bins for i in range(n_bins + 1)
    ]
    equidist[-1] += 0.0001

    import pandas as pd

    dt["bin"] = pd.cut(dt[attribute], equidist)

    dt_grp = dt.groupby("bin").agg(bad_cnt=(target, sum), tot_cnt=(target, len), predictor_mean=(attribute, "mean"))
    if add_score_calibration:
        import numpy as np

        dt_grp["expected_target_rate"] = 1 / (1 + np.exp(dt_grp["predictor_mean"]))

    dt_grp["target_rate"] = dt_grp["bad_cnt"] / dt_grp["tot_cnt"]
    dt_grp.reset_index(inplace=True)

    plot_hist_with_default_rates(
        dt=dt_grp,
        col_target_count="bad_cnt",
        col_total_count="tot_cnt",
        col_target_rate="target_rate",
        col_bin_name="bin",
        attribute=attribute,
        add_score_calibration=add_score_calibration,
        col_expected_target_rate="expected_target_rate",
        save_to_path=save_to_path,
    )


def plot_roc(data: "pd.DataFrame", score: str, target: str, save_to_path: Optional[str] = None) -> None:
    """
    Method plots Receiver Operating Curve (ROC) for given variable.

    :param data: Data frame with data.
    :param score: Variable used for sorting.
    :param target: Name of the target.
    :param save_to_path: Path where the figure should be saved. If None, figure is not saved to disk.
    :return: None
    """
    import matplotlib.pyplot as plt

    dt = data[(data[score].notnull()) & (data[target].notnull())][[score, target]]
    dt = dt.sort_values(score)

    dt["cdf_bad"] = dt[target].cumsum() / dt[target].sum()
    dt["cdf_good"] = (1 - dt[target]).cumsum() / (1 - dt[target]).sum()

    plt.figure(figsize=(5, 5))
    ax1 = plt.subplot(111)
    ax1.plot(dt["cdf_bad"], dt["cdf_good"])
    ax1.plot([0, 1], [0, 1], ls="--", color="gray")
    ax1.fill_between(dt["cdf_bad"], 0, dt["cdf_good"], color="lightblue", alpha=0.1)
    ax1.set_xlim((0, 1))
    ax1.set_ylim((0, 1))
    ax1.spines["top"].set_color("lightgray")
    ax1.spines["left"].set_color("lightgray")
    ax1.spines["right"].set_color("lightgray")
    ax1.spines["bottom"].set_color("lightgray")
    ax1.tick_params(axis="x", colors="gray")
    ax1.tick_params(axis="y", colors="gray")

    ax1.set_xlabel("CDF of bads".upper(), horizontalalignment="right", x=1, color="red")
    ax1.set_ylabel("CDF of goods".upper(), verticalalignment="center_baseline", y=0.86, labelpad=10, color="g")

    ax1.set_title("Receiver Operation Curve", pad=10)

    if save_to_path is not None:
        plt.savefig(save_to_path)

    plt.show()


def plot_roc_multiple_samples(
    data: "pd.DataFrame",
    col_sample: str,
    score: str,
    target: str,
    samples_to_plot: Optional[List[str]] = None,
    save_to_path: Optional[str] = None,
) -> None:
    """
    Method plots Receiver Operating Curve (ROC) for given variable and multiple samples (training/validation/test/...).

    :param data: Data frame with data.
    :param col_sample: Name of the columns that holds information about sample type.
    :param score: Variable used for sorting.
    :param target: Name of the target.
    :param samples_to_plot: List of selected samples to be plotted.
    :param save_to_path: Path where the figure should be saved. If None, figure is not saved to disk.
    :return: None
    """
    import matplotlib.pyplot as plt

    plt.figure(figsize=(5, 5))
    ax1 = plt.subplot(111)

    # if no samples to plot were selected, all available will be plotted
    if samples_to_plot is None:
        samples_to_plot = list(data[col_sample].drop_duplicates())

    for sample in samples_to_plot:
        dt = data[(data[score].notnull()) & (data[target].notnull()) & (data[col_sample] == sample)][[score, target]]
        dt = dt.sort_values(score)

        dt["cdf_bad"] = dt[target].cumsum() / dt[target].sum()
        dt["cdf_good"] = (1 - dt[target]).cumsum() / (1 - dt[target]).sum()

        ax1.plot(dt["cdf_bad"], dt["cdf_good"], label=sample)

    ax1.plot([0, 1], [0, 1], ls="--", color="gray")
    ax1.set_xlim((0, 1))
    ax1.set_ylim((0, 1))
    ax1.spines["top"].set_color("lightgray")
    ax1.spines["left"].set_color("lightgray")
    ax1.spines["right"].set_color("lightgray")
    ax1.spines["bottom"].set_color("lightgray")
    ax1.tick_params(axis="x", colors="gray")
    ax1.tick_params(axis="y", colors="gray")
    ax1.legend(loc="lower right", frameon=False)

    ax1.set_xlabel("CDF of bads".upper(), horizontalalignment="right", x=1, color="red")
    ax1.set_ylabel("CDF of goods".upper(), verticalalignment="center_baseline", y=0.86, labelpad=10, color="g")

    ax1.set_title("Receiver Operation Curve", pad=10)

    if save_to_path is not None:
        plt.savefig(save_to_path)

    plt.show()


def plot_ks(data: "pd.DataFrame", score: str, target: str, save_to_path: Optional[str] = None) -> None:
    dt = data[(data[score].notnull()) & (data[target].notnull())][[score, target]]
    dt = dt.sort_values(score)

    dt["cdf_bad"] = dt[target].cumsum() / dt[target].sum()
    dt["cdf_good"] = (1 - dt[target]).cumsum() / (1 - dt[target]).sum()
    dt["ks"] = dt["cdf_good"] - dt["cdf_bad"]
    ks = dt[dt["ks"] == dt["ks"].max()].iloc[0]
    ks_max = ks["ks"]
    ks_max_loc = ks["score"]

    import matplotlib.pyplot as plt

    plt.figure(figsize=(7, 5))
    ax1 = plt.subplot(111)
    ax1.plot(dt[score], dt["cdf_bad"], label="CDF bads", color="coral")
    ax1.plot(dt[score], dt["cdf_good"], label="CDF goods", color="lightblue")
    ax1.plot(dt[score], dt["ks"], label="KS", color="green")
    ax1.fill_between(dt[score], 0, dt["ks"], color="green", alpha=0.05)
    ax1.plot([ks_max_loc, ks_max_loc], [0, ks_max], color="red", ls="--")
    ax1.scatter([ks_max_loc], [ks_max], color="red")
    ax1.annotate("{:.2f}".format(ks_max), (ks_max_loc - 0.12, ks_max + 0.03), color="red", weight="bold")

    ax1.set_ylim((0, 1.05))

    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_color("lightgray")
    ax1.spines["bottom"].set_color("lightgray")
    ax1.tick_params(axis="x", colors="gray")
    ax1.tick_params(axis="y", colors="gray")
    ax1.legend(loc="upper left", frameon=False)

    ax1.set_xlabel(score.upper(), horizontalalignment="right", x=1)
    ax1.set_title("Kolmogorov-Smirnov", pad=10)

    if save_to_path is not None:
        plt.savefig(save_to_path)

    plt.show()


def plot_dr_vs_ar(data: "pd.DataFrame", score: str, target: str, save_to_path: Optional[str]) -> None:
    dt = data[data[score].notnull()]
    dt = dt.sort_values(score)
    dt["temp"] = 1
    dt["appr_cnt"] = dt["temp"].cumsum()
    dt["appr_rt"] = dt["appr_cnt"] / dt["temp"].sum()
    dt["def_rt"] = dt[target].cumsum() / dt["appr_cnt"]

    import matplotlib.pyplot as plt

    ax1 = plt.subplot(111)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_color("lightgray")
    ax1.spines["bottom"].set_color("lightgray")
    ax1.tick_params(axis="x", colors="gray")
    ax1.tick_params(axis="y", colors="gray")
    ax1.set_xlim((0, 1))
    ax1.set_xlabel("Approval rate".upper(), color="green", horizontalalignment="right", x=1, labelpad=10)
    ax1.set_ylabel("Default rate".upper(), color="red", verticalalignment="center_baseline", y=0.84, labelpad=10)
    ax1.set_title("Expected target rate given approval rate", pad=10)
    mask = dt["appr_rt"] > 0.05
    plt.plot(dt[mask]["appr_rt"], dt[mask]["def_rt"])

    if save_to_path is not None:
        plt.savefig(save_to_path)

    plt.show()


def plot_observations_count_in_time(
    data: "pd.DataFrame", col_time: str, col_target: str, col_sample: str, save_to_path: Optional[str] = None
) -> None:
    import matplotlib.pyplot as plt

    dt = data[data[col_target].notnull()]

    dt["month"] = dt[col_time].apply(lambda x: x.year * 100 + x.month)
    dt_grp = dt.groupby("month").agg(bad_cnt=(col_target, sum), tot_cnt=(col_target, len), def_rt=(col_target, "mean"))

    ax1 = plt.subplot(111)
    ax1.bar(range(len(dt_grp)), dt_grp["bad_cnt"], color="coral", label="bads")
    ax1.bar(
        range(len(dt_grp)),
        dt_grp["tot_cnt"] - dt_grp["bad_cnt"],
        bottom=dt_grp["bad_cnt"].values,
        color="lightblue",
        label="goods",
    )
    rotation = 90 if len(dt_grp) > 10 else 45
    plt.xticks(range(len(dt_grp)), dt_grp.index, rotation=rotation)
    ax1.tick_params(axis="x", colors="gray")
    ax1.tick_params(axis="y", colors="gray")
    ax1.spines["top"].set_visible(False)
    ax1.set_ylabel("Observation count".upper(), verticalalignment="center_baseline", y=0.75, labelpad=12)

    from matplotlib.axes import Axes

    ax2: Axes = ax1.twinx()

    samples = dt[col_sample].unique()
    if len(samples) > 1:
        for sample in samples:
            dt_grp2 = dt[dt[col_sample] == sample].groupby("month").agg(def_rt=(col_target, "mean"))

            if "def_rt" in dt_grp.columns:
                del dt_grp["def_rt"]
            dt_grp = dt_grp.join(dt_grp2, how="left")
            ax2.plot(range(len(dt_grp)), dt_grp["def_rt"], marker="o", ls="--", label=sample)
    else:
        ax2.plot(range(len(dt_grp)), dt_grp["def_rt"], marker="o", ls="--", label="Default rate")

    ax2.legend(loc="upper left", frameon=False)
    ax2.spines["top"].set_visible(False)
    ax2.spines["left"].set_color("lightgray")
    ax2.spines["right"].set_color("lightgray")
    ax2.spines["bottom"].set_color("lightgray")
    ax2.tick_params(axis="x", colors="gray")
    ax2.tick_params(axis="y", colors="gray")

    ax2.set_ylabel("Default rate".upper(), color="red", verticalalignment="center_baseline", y=0.84, labelpad=12)
    ax2.set_title("Development sample distribution in time", pad=10)

    if save_to_path is not None:
        plt.savefig(save_to_path)

    plt.show()


def coef_pie_chart(model: ExtendedPredictiveModel, save_to_path: Optional[str] = None) -> None:
    if model.predictive_model_type != PredictiveModelType.LOGISTIC_REGRESSION:
        logger.warning("coef_pie_chart is valid only for ModelLogisticRegression.")
        return None

    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 10))
    plt.pie(
        -1 * model.get_external_model_coefficients(),
        labels=model.attributes,
        autopct="%1.1f%%",
        shadow=False,
        startangle=90,
    )

    if save_to_path is not None:
        plt.savefig(save_to_path)

    plt.show()


def plot_lift_curves(
    data: "pd.DataFrame",
    col_score: str,
    col_target: str,
    col_sample: str,
    samples: Optional[List[str]] = None,
    save_to_path: Optional[str] = None,
) -> None:
    import matplotlib.pyplot as plt

    ax1 = plt.subplot(111)
    ax1.tick_params(axis="x", colors="gray")
    ax1.tick_params(axis="y", colors="gray")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_color("lightgray")
    ax1.spines["bottom"].set_color("lightgray")
    ax1.set_ylabel("Lift".upper(), verticalalignment="center_baseline", y=0.96, labelpad=12)
    ax1.set_xlabel("Population share".upper(), horizontalalignment="right", x=1, labelpad=10)
    ax1.set_title("Lift curves", pad=10)

    if samples is None or len(samples) == 0:
        samples = data[col_sample].unique()
        if samples is None or len(samples) == 0:
            raise ValueError(f"Column {col_sample} either not found in provided data or all its values are nulls.")

    for sample in samples:
        dt = data[(data[col_score].notnull()) & (data[col_target].notnull()) & (data[col_sample] == sample)]
        tot_dr = dt[col_target].sum() / len(dt)
        dt = dt.sort_values(col_score, ascending=False)
        dt["temp"] = 1
        dt["pop_share_cnt"] = dt["temp"].cumsum()
        dt["pop_share_perc"] = dt["pop_share_cnt"] / dt["temp"].sum()
        dt["def_rt"] = dt[col_target].cumsum() / dt["pop_share_cnt"]
        dt["lift"] = dt["def_rt"] / tot_dr

        mask = dt["pop_share_perc"] > 0.02
        ax1.plot(dt[mask]["pop_share_perc"], dt[mask]["lift"], label=sample)

    ax1.legend(loc="upper right", frameon=False)
    ax1.set_ylim((0, ax1.get_ylim()[1]))
    ax1.set_xlim((0, 1))
    ax1.plot([0, 1], [1, 1], ls="--", color="gray")

    if save_to_path is not None:
        plt.savefig(save_to_path)

    plt.show()
