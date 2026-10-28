import time
from pathlib import Path
from typing import Iterable, Literal

import cartopy.feature as cf
import cartopy.crs as ccrs
from cartopy.mpl.geoaxes import GeoAxes
import networkx as nx
import numpy as np
from numpy.typing import NDArray
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FuncFormatter

from .utils.colors import flatuicolors
from .utils.styling import get_standard_colors, hide_and_move_axis
from .temporal_network import TemporalNetwork
from .weighted_network import WeightedNetwork


def _map_setup(ax: GeoAxes) -> None:
    """Apply the study-area extent, coastlines, and borders to a map axis.

    Args:
        ax: Map axis to configure.
    """
    ax.coastlines()
    ax.add_feature(cf.BORDERS, ls=":")
    ax.set_extent([4, 11.5, 44, 53.5])


def plot_temporal_evolution_of_governance(
    network: WeightedNetwork, output_folder: Path, normalize: bool = True
) -> None:
    """Plot Appendix Figure A1: secular and religious governance over time by community.

    Args:
        network: Weighted network containing community and edge data.
        output_folder: Directory where the figure is saved.
        normalize: Whether to plot shares rather than link counts.
    """
    fig, axarr = plt.subplots(2, 5, sharey=True, sharex=True, figsize=(8, 4))
    flatax = axarr.flatten()
    colors = get_standard_colors()

    communities = network.communities()
    edges = network.edges()
    if normalize:
        label = "Share of links\nin Community"
        filename = "timeseries_governance_relative.jpg"
    else:
        label = "Number of links\nin Community"
        filename = "timeseries_governance_absolute.jpg"

    for i, community in enumerate(communities):
        in_community = edges["from"].isin(community) & edges["to"].isin(community)
        timeseries = (
            edges[in_community]
            .groupby("Year")
            .ruling_party_category.value_counts()
            .unstack()
            .fillna(0)
        )

        if "R" not in timeseries.columns:
            timeseries["R"] = 0
        if "S" not in timeseries.columns:
            timeseries["S"] = 0

        if normalize:
            norm = timeseries.S + timeseries.R
        else:
            norm = 1

        flatax[i].plot(timeseries.index, timeseries.S / norm, label="Secular", c=colors[i])
        flatax[i].plot(
            timeseries.index, timeseries.R / norm, label="Religious", c=colors[i], ls="--"
        )
        hide_and_move_axis(flatax[i])

    flatax[i].legend(fontsize=8)

    for ax in axarr[1, :]:
        ax.set_xticks(range(1100, 1550, 100), range(1100, 1550, 100), rotation=90, size=6)
        ax.set_xlabel("Year")

    for ax in axarr[:, 0]:
        ax.set_ylabel(label)

    fig.tight_layout()
    fig.savefig(Path(output_folder) / filename, dpi=400)


def plot_pooled_sample(
    network: WeightedNetwork, crs: ccrs.CRS, output_folder: Path
) -> None:
    """Plot Figure 1: the pooled network and its community assignments.

    Args:
        network: Weighted network to plot.
        crs: Cartopy coordinate reference system for the maps.
        output_folder: Directory where the figure is saved.
    """
    fig, (network_ax, first_community_ax, second_community_ax) = plt.subplots(
        1, 3, figsize=(9.5, 6.5), subplot_kw={"projection": crs}
    )
    for ax in (network_ax, first_community_ax, second_community_ax):
        _map_setup(ax)

    graph = network.G()
    positions = network.position()
    communities = network.communities()
    nx.draw_networkx_edges(
        graph, positions, ax=network_ax, edge_color="0.35", alpha=0.08, width=0.35
    )
    nx.draw_networkx_nodes(
        graph,
        positions,
        nodelist=list(graph.nodes),
        node_size=7,
        node_color="0.65",
        node_shape="o",
        edgecolors="black",
        linewidths=0.3,
        ax=network_ax,
    )
    network_ax.set_title("Full network")
    markers = ["o", "s", "^", "v", "D", "p", "X", "<", ">", "*"]
    first_community_ax.set_title("Communities 1-3, 5")
    second_community_ax.set_title("Communities 4, 6-10")
    for ax, community_indices in (
        (first_community_ax, [0, 1, 2, 4]),
        (second_community_ax, [3, 5, 6, 7, 8, 9]),
    ):
        for i in community_indices:
            if i < len(communities):
                nx.draw_networkx_nodes(
                    graph,
                    positions,
                    nodelist=list(communities[i]),
                    node_size=16,
                    node_color="0.65",
                    alpha=0.8,
                    node_shape=markers[i],
                    edgecolors="black",
                    linewidths=0.35,
                    ax=ax,
                )
    handles = [
        Line2D(
            [],
            [],
            marker=marker,
            linestyle="none",
            color="black",
            markerfacecolor="0.65",
            markeredgecolor="black",
            markersize=6,
            alpha=0.65,
            label=f"Community {i + 1}",
        )
        for i, marker in enumerate(markers[: len(communities)])
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=5,
        fontsize=8,
        framealpha=0.9,
        title="Communities",
        title_fontsize=9,
        bbox_to_anchor=(0.5, 0.015),
    )
    fig.subplots_adjust(left=0.01, right=0.99, top=0.95, bottom=0.17, wspace=0.0)
    fig.savefig(Path(output_folder) / "communities.pdf", bbox_inches="tight")


def governing_parties_histograms(network: WeightedNetwork, output_folder: Path) -> None:
    """Plot Appendix Figure A2: governing-party frequencies within each community.

    Args:
        network: Weighted network containing community and edge data.
        output_folder: Directory where the figure is saved.
    """
    fig, axarr = plt.subplots(2, 5, sharey=True, sharex=False, figsize=(8, 4))
    flatax = axarr.flatten()

    edges = network.edges()
    communities = network.communities()
    colors = get_standard_colors()

    for i, community in enumerate(communities):
        in_edges = edges[edges["from"].isin(community) & edges["to"].isin(community)]
        histogram = in_edges.PartyID.value_counts().to_frame().sort_index()
        x = range(len(histogram.index))
        y = histogram["count"].values
        y = y / y.sum()

        flatax[i].bar(x, y, color=colors[i])
        hide_and_move_axis(flatax[i])
        flatax[i].set_xticks(x, histogram.index, rotation="vertical", size=5)

    axarr[1, 2].set_xlabel("Governing party")
    axarr[0, 0].set_ylabel("Share of years\nwith governing party")
    axarr[1, 0].set_ylabel("Share of years\nwith governing party")
    fig.tight_layout()
    fig.savefig(Path(output_folder) / "governing_parties.jpg", dpi=400)


def plot_temporal_network_statistics(
    network: TemporalNetwork,
    output_folder: Path,
    hamming_threshold: int = 400,
    min_year: int = 1200,
) -> None:
    """Plot Figure 2: average degree and year-to-year network changes over time.

    Args:
        network: Temporal network with degree and Hamming-distance statistics.
        output_folder: Directory where the figure is saved.
        hamming_threshold: Minimum Hamming distance highlighted as a large change.
        min_year: Earliest year included in the figure.
    """
    fig, axarr = plt.subplots(2, 1, figsize=(5, 3.5), sharex=True)

    years = network.years()
    hamming_distance = network.hamming_distance()
    average_degree = network.average_degree_sequence()

    within_timeframe = years >= min_year
    years = years[within_timeframe]
    hamming_distance = hamming_distance[within_timeframe]
    average_degree = average_degree[within_timeframe]

    non_boundary_years = ((years - 1) % 50) != 0
    significant_changes = hamming_distance > hamming_threshold
    print("Years with significant changes:", years[non_boundary_years & significant_changes])

    axarr[0].plot(years, average_degree, c=flatuicolors.wetasphalt)
    axarr[1].plot(
        years[non_boundary_years],
        hamming_distance[non_boundary_years],
        c=flatuicolors.wetasphalt,
    )

    for ax in axarr:
        hide_and_move_axis(ax)
        for year in years[non_boundary_years & significant_changes]:
            ax.axvline(year, zorder=0, c=flatuicolors.pomegranate, lw=4, alpha=0.3)

    axarr[1].axhline(hamming_threshold, ls=":", c="k")
    axarr[1].set_xlabel("Year")
    axarr[0].set_ylabel("Average Degree")
    axarr[1].set_ylabel("No. links that change")
    fig.tight_layout()
    fig.savefig(Path(output_folder) / "temporal_evolution.png", dpi=400)


def get_shared_status(network: WeightedNetwork) -> pd.DataFrame:
    """Prepare yearly pairwise status data used to create main-text Figure 3.

    Args:
        network: Network providing node-year status observations.
    """
    nodes = network.nodes()
    places = nodes.PlaceID.unique()

    frames = []
    for place_id in places:
        frames.append(
            pd.merge(
                nodes[nodes.PlaceID == place_id],
                nodes[nodes.PlaceID > place_id],
                on="Year",
            )[["PlaceID_x", "PlaceID_y", "Year", "Juden_x", "Juden_y"]]
        )

    shared_status = pd.concat(frames)
    shared_status["co-occur"] = (shared_status.Juden_x & shared_status.Juden_y).astype(bool)
    shared_status["coherence"] = shared_status.Juden_x == shared_status.Juden_y
    shared_status["fromto"] = (
        shared_status["PlaceID_x"].astype(str) + "_" + shared_status["PlaceID_y"].astype(str)
    )
    return shared_status


def compute_shared_status_randomization(
    shared_status_df: pd.DataFrame,
    network: WeightedNetwork,
    key: Literal["coherence", "co-occur"] = "coherence",
    n_bins: int = 5,
    min_values: int = 10,
    n_repetitions: int = 9999,
    seed: int = 0,
) -> pd.DataFrame:
    """Prepare observed and randomized pairwise status distributions for Figure 3.

    Args:
        shared_status_df: Yearly pairwise status data from `get_shared_status`.
        network: Network providing the observed communities.
        key: Status column to analyze, such as `coherence` or `co-occur`.
        n_bins: Number of bins spanning the status range from zero to one.
        min_values: Minimum observations required for a city pair.
        n_repetitions: Number of randomized assignments per community.
        seed: Random seed for reproducible assignments.

    Returns observed and null histogram shares, confidence intervals, and adjusted
    p-values for each community and status bin.
    """
    if n_repetitions < 1:
        raise ValueError("n_repetitions must be at least 1")

    start_time = time.perf_counter()
    rng = np.random.default_rng(seed)
    edges = np.linspace(0, 1, n_bins + 1)
    pair_stats = (
        shared_status_df.groupby(["PlaceID_x", "PlaceID_y"])[key]
        .agg(["mean", "count"])
        .reset_index()
    )
    pair_stats = pair_stats[pair_stats["count"] > min_values]
    all_places = np.unique(
        np.concatenate(
            [shared_status_df["PlaceID_x"].unique(), shared_status_df["PlaceID_y"].unique()]
        )
    )

    def hist_for(places: Iterable[int]) -> NDArray[np.float64]:
        """Return the binned pairwise-status distribution for a set of places.

        Args:
            places: Place identifiers to include in the pairwise distribution.
        """
        selected_places = set(places)
        mask = pair_stats["PlaceID_x"].isin(selected_places) & pair_stats["PlaceID_y"].isin(
            selected_places
        )
        means = pair_stats.loc[mask, "mean"]
        if len(means) == 0:
            return np.full(n_bins, np.nan)
        counts, _ = np.histogram(means, bins=edges)
        return counts / counts.sum()

    communities = network.communities()[:10]
    p_values = np.full((len(communities), n_bins), np.nan)
    results = []
    print(
        f"Starting randomization test: {len(communities)} communities, "
        f"{n_repetitions:,} repetitions per community.",
        flush=True,
    )

    for i, community in enumerate(communities):
        observed = hist_for(community)
        community_size = len(community)
        print(
            f"Community {i + 1}/{len(communities)} ({community_size} places): "
            "starting random assignments.",
            flush=True,
        )
        null_draws = []
        progress_interval = max(1, n_repetitions // 4)
        for draw_idx in range(n_repetitions):
            null_draws.append(
                hist_for(rng.choice(all_places, size=community_size, replace=False))
            )
            completed = draw_idx + 1
            if completed % progress_interval == 0 or completed == n_repetitions:
                print(
                    f"  Random assignments: {completed:,}/{n_repetitions:,} "
                    f"({completed / n_repetitions:.0%})",
                    flush=True,
                )
        null = np.asarray(null_draws)

        for bin_index in range(n_bins):
            draws = null[:, bin_index]
            draws = draws[np.isfinite(draws)]
            null_lower, null_median, null_upper = np.nan, np.nan, np.nan
            p_value = np.nan
            if len(draws):
                null_lower, null_median, null_upper = np.percentile(draws, [2.5, 50, 97.5])
                if np.isfinite(observed[bin_index]):
                    lower_tail = (np.sum(draws <= observed[bin_index]) + 1) / (len(draws) + 1)
                    upper_tail = (np.sum(draws >= observed[bin_index]) + 1) / (len(draws) + 1)
                    p_value = min(1.0, 2 * min(lower_tail, upper_tail))
                    p_values[i, bin_index] = p_value
            results.append(
                {
                    "community": i,
                    "bin_index": bin_index,
                    "bin": f"{edges[bin_index]:.1f}-{edges[bin_index + 1]:.1f}",
                    "observed": observed[bin_index],
                    "null_median": null_median,
                    "null_lower": null_lower,
                    "null_upper": null_upper,
                    "p_value": p_value,
                }
            )
        print(
            f"Community {i + 1}/{len(communities)} complete "
            f"({time.perf_counter() - start_time:.1f}s elapsed).",
            flush=True,
        )

    tested = np.flatnonzero(np.isfinite(p_values))
    adjusted = np.full(p_values.size, np.nan)
    if len(tested):
        order = tested[np.argsort(p_values.ravel()[tested])]
        ranked = p_values.ravel()[order] * (len(order) - np.arange(len(order)))
        adjusted[order] = np.minimum(1.0, np.maximum.accumulate(ranked))
    for row, p_holm in zip(results, adjusted.reshape(p_values.shape).ravel()):
        row["p_holm"] = p_holm

    print(
        f"Randomization test complete ({time.perf_counter() - start_time:.1f}s total).",
        flush=True,
    )
    return pd.DataFrame(results)


def plot_shared_status_randomized_communities(
    results: pd.DataFrame,
    output_folder: Path,
    key: Literal["coherence", "co-occur"] = "coherence",
    n_bins: int = 5,
    show_asterisks: bool = True,
) -> None:
    """Plot Figure 3: observed versus randomized pairwise status by community.

    Args:
        results: Observed and randomized distributions from the randomization test.
        output_folder: Directory where the figure is saved.
        key: Status represented by the distributions, such as `coherence`.
        n_bins: Number of status bins used to position bars and tick labels.
        show_asterisks: Whether to mark bins significant after p-value adjustment.
    """
    fig, axarr = plt.subplots(2, 5, sharex=True, sharey=True, figsize=(8, 5))
    colors = get_standard_colors()
    bin_width = 1 / n_bins
    edges = np.linspace(0, 1, n_bins + 1)
    centers = 0.5 * (edges[1:] + edges[:-1])
    bar_group_midpoints = centers - 0.1 * bin_width
    x_label = (
        "Mean pairwise co-presence\n(fraction of years with Jews in both places)"
        if key == "co-occur"
        else "Mean pairwise coherence\n(fraction of years with matching policy)"
    )

    for i, ax in enumerate(axarr.flatten()):
        title_y = (1.12 if i >= 5 else 1.0) if show_asterisks else 1.0
        ax.set_title(f"Community {i + 1}", fontsize=8, y=title_y)
        community_results = results[results["community"] == i].sort_values("bin_index")
        if community_results.empty:
            continue

        observed = community_results["observed"].to_numpy()
        null_median = community_results["null_median"].to_numpy()
        null_lower = community_results["null_lower"].to_numpy()
        null_upper = community_results["null_upper"].to_numpy()
        ax.bar(
            centers - 0.4 * bin_width + 0.015,
            observed,
            width=bin_width * 0.4,
            color=colors[i],
            alpha=0.95,
        )
        ax.bar(
            centers - 0.015,
            null_median,
            width=bin_width * 0.4,
            color="k",
            alpha=0.25,
            zorder=0,
        )

        valid = np.isfinite(null_median) & np.isfinite(null_lower) & np.isfinite(null_upper)
        ax.errorbar(
            centers[valid] - 0.015 + 0.2 * bin_width,
            null_median[valid],
            yerr=np.vstack(
                [null_median[valid] - null_lower[valid], null_upper[valid] - null_median[valid]]
            ),
            fmt="none",
            ecolor="k",
            alpha=0.6,
            lw=0.8,
            capsize=2,
            zorder=1,
        )

        if show_asterisks:
            for bin_index, p_holm in enumerate(community_results["p_holm"].to_numpy()):
                if np.isfinite(p_holm) and p_holm < 0.05:
                    observed_bar_center = (
                        centers[bin_index] - 0.4 * bin_width + 0.015 + 0.2 * bin_width
                    )
                    ax.text(
                        observed_bar_center,
                        1.02,
                        "*",
                        transform=ax.get_xaxis_transform(),
                        ha="center",
                        va="bottom",
                        fontsize=10,
                        fontweight="bold",
                        clip_on=False,
                    )
        ax.set_ylim(0, 0.45)

    fig.supxlabel(x_label, y=0.01)
    fig.supylabel("Share of city pairs", x=0.018, y=0.5)

    for ax in axarr.flatten():
        ax.set_xlim(0, 1)
        ax.set_xticks(bar_group_midpoints)
        ax.set_xticklabels(["0", "", "0.5", "", "1"])
        ax.xaxis.set_minor_locator(
            FixedLocator([bar_group_midpoints[0], bar_group_midpoints[2], bar_group_midpoints[4]])
        )
        ax.xaxis.set_minor_formatter(
            FuncFormatter(
                lambda x, pos: "0"
                if np.isclose(x, bar_group_midpoints[0])
                else "0.5"
                if np.isclose(x, bar_group_midpoints[2])
                else "1"
                if np.isclose(x, bar_group_midpoints[4])
                else ""
            )
        )
        ax.tick_params(axis="x", which="minor", length=6, width=1.2)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.subplots_adjust(
        left=0.09, right=0.99, bottom=0.20, top=0.95, wspace=0.22, hspace=0.45
    )
    output_file = Path(output_folder) / f"prob_{key}_community_structure.jpg"
    fig.savefig(output_file, dpi=400)
    print(f"Plot saved to {output_file}.", flush=True)
