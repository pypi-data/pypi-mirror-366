from typing import Any

import networkx as nx
import pandas as pd
from funtracks.data_model import SolutionTracks

import finn
from finn.track_data_views.views.tree_view.tree_widget_utils import (
    extract_sorted_tracks,
)


def assign_tracklet_ids(graph: nx.DiGraph) -> tuple[nx.DiGraph, list[Any], int]:
    """Add a track_id attribute to a graph by removing division edges,
    assigning one id to each connected component.
    Designed as a helper for visualizing the graph in the napari Tracks layer.

    Args:
        graph (nx.DiGraph): A networkx graph with a tracking solution

    Returns:
        nx.DiGraph, list[Any], int: The same graph with the track_id assigned. Probably
        occurrs in place but returned just to be clear. Also returns a list of edges
        that are between tracks (e.g. at divisions), and the max track ID that was
        assigned
    """
    graph_copy = graph.copy()

    parents = [node for node, degree in graph.out_degree() if degree >= 2]
    intertrack_edges = []

    # Remove all intertrack edges from a copy of the original graph
    for parent in parents:
        daughters = [child for p, child in graph.out_edges(parent)]
        for daughter in daughters:
            graph_copy.remove_edge(parent, daughter)
            intertrack_edges.append((parent, daughter))

    track_id = 1
    for tracklet in nx.weakly_connected_components(graph_copy):
        nx.set_node_attributes(graph, {node: {"track_id": track_id} for node in tracklet})
        track_id += 1
    return graph, intertrack_edges, track_id


def test_track_df(graph_2d):
    tracks = SolutionTracks(graph=graph_2d, ndim=3)

    assert tracks.get_area(1) == 1245
    assert tracks.get_area(2) is None

    tracks.graph, _, _ = assign_tracklet_ids(tracks.graph)

    colormap = finn.utils.colormaps.label_colormap(
        49,
        seed=0.5,
        background_value=0,
    )

    track_df = extract_sorted_tracks(tracks, colormap)
    assert isinstance(track_df, pd.DataFrame)
    assert track_df.loc[track_df["node_id"] == 1, "area"].values[0] == 1245
    assert track_df.loc[track_df["node_id"] == 2, "area"].values[0] == 0
    assert track_df["area"].notna().all()
