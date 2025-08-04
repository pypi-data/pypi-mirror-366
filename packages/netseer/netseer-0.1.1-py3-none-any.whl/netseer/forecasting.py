"""Internal: Supplimentary functions for predictions."""

from collections.abc import Iterable
from typing import Optional

import numpy as np
import pandas as pd
import statsmodels
import statsmodels.api as sm
import statsmodels.tools.tools
import statsforecast as sf
import statsforecast.models as sfm


import igraph as ig


def predict_num_nodes(
    graph_list: Iterable[ig.Graph],
    h: int = 5,
    conf_level: Optional[int] = None,
    conf_lower=90,
):
    num_graphs = len(graph_list)
    node_counts = np.array([gr.vcount() for gr in graph_list])
    print(f"{node_counts=}")
    conf_lower = None
    conf_upper = None
    if num_graphs < 15:
        # r: number of nodes = m * time step
        # python: number of nodes = m * time stop + c
        exogenous = statsmodels.tools.tools.add_constant(
            np.arange(num_graphs).reshape((num_graphs, 1))
        )
        linear_model = sm.OLS(node_counts, exog=exogenous).fit()
        prediction = linear_model.predict(exog=[1, h + num_graphs])
        print(f"short node count prediction: {prediction}")
    else:
        model = sfm.AutoETS()
        model.fit(y=node_counts, X=range(num_graphs))
        prediction = model.predict(
            h=h, level=[conf_level] if conf_level is not None else None
        )
        if conf_level is not None:
            conf_lower = prediction[f"lo-{conf_level}"]
            conf_upper = prediction[f"hi-{conf_level}"]
        print(f"longer node count prediction: {prediction}")
        prediction = np.ceil(prediction["mean"]).astype(int)
    # account for the possibility that the number of nodes may decrease
    new_nodes = np.hstack(([prediction[0] - node_counts[-1]], np.diff(prediction)))
    removed_nodes = 0
    for i in range(h):
        if new_nodes[i] < 0:
            removed_nodes += np.abs(new_nodes[i])
            new_nodes[i] = 0
        if removed_nodes <= 0:
            continue
        this_removed_nodes = min(removed_nodes, new_nodes[i])
        removed_nodes -= this_removed_nodes
        new_nodes[i] -= this_removed_nodes
    if removed_nodes > 0:
        new_nodes[-1] -= removed_nodes
        if conf_lower is not None:
            conf_lower[-1] -= removed_nodes
            conf_upper[-1] -= removed_nodes
    # return results
    new_nodes = new_nodes[-1]
    conf_lower = conf_lower[-1] if conf_lower is not None else None
    conf_upper = conf_upper[-1] if conf_upper is not None else None
    return (
        new_nodes,
        conf_lower,
        conf_upper,
    )  # {"new_nodes":, "conf_lower":, "conf_upper":}


def predict_existing_nodes_degrees(
    graph_list: Iterable[ig.Graph], h: int = 5, conf_level: Optional[int] = None
):
    num_graphs = len(graph_list)
    num_nodes = [gr.vcount() for gr in graph_list]
    total_nodes = sum(num_nodes)
    data = np.ndarray((total_nodes, 3), dtype=int)
    data_start = 0
    for graph_idx, gr in enumerate(graph_list):
        this_end = data_start + num_nodes[graph_idx]
        data[data_start:this_end, 0] = range(num_nodes[graph_idx])  # node index
        data[data_start:this_end, 1] = graph_idx  # time step
        data[data_start:this_end, 2] = gr.degree()  # degree of each node
        data_start = this_end

    df = pd.DataFrame(data=data, columns=["node_index", "time_step", "degree"])
    model = sf.StatsForecast(models=[sfm.AutoARIMA()], freq=1)
    model_str = "AutoARIMA"
    rename_dict = {model_str: "mean"}
    if conf_level is not None:
        rename_dict.update(
            {
                f"{model_str}-lo-{conf_level}": "conf_low",
                f"{model_str}-hi-{conf_level}": "conf_high",
            }
        )
    prediction = model.fit_predict(
        df=df,
        id_col="node_index",
        time_col="time_step",
        target_col="degree",
        h=h,
        level=[conf_level],
    )
    print(f"first degree prediction:\n{prediction}")
    print(type(prediction))
    print(f"rename dict: {rename_dict}")
    prediction.rename(columns=rename_dict, inplace=True)
    prediction = prediction[prediction["time_step"] == (num_graphs + h - 1)]
    for prediction_name in rename_dict.values():
        prediction[prediction_name] = np.ceil(prediction[prediction_name]).astype(int)
    # print(f"degree prediction:\n{prediction}")
    return prediction  #


def predict_total_edges_counts(
    graph_list: Iterable[ig.Graph], h: int = 5, conf_level: Optional[int] = None
):
    # predict the total number of edges in the final graph
    model = sfm.AutoARIMA()
    total_edges = np.array([gr.ecount() for gr in graph_list])
    time_steps = np.arange(len(graph_list))
    level = [conf_level] if conf_level is not None else None
    prediction = model.forecast(y=total_edges, h=h, level=level)
    results = {"mean": np.ceil(prediction["mean"][-1]).astype(int)}
    if conf_level is not None:
        results.update(
            {
                "conf_low": np.ceil(prediction[f"lo-{conf_level}"].iloc[-1]).astype(
                    int
                ),
                "conf_high": np.ceil(prediction[f"hi-{conf_level}"].iloc[-1]).astype(
                    int
                ),
            }
        )
    return results


def predict_new_nodes_degrees(graph_list: Iterable[ig.Graph]):
    # predict the degrees for new nodes (nodes that are in the predicted graph but not the original graph list)
    mean_new_degrees = np.zeros((len(graph_list)), dtype=float)
    for graph_idx in range(1, len(graph_list)):
        last_node = graph_list[graph_idx - 1].vcount()
        this_new_nodes_degrees = graph_list[graph_idx].degree()[last_node:]
        this_mean_new_nodes = (
            np.mean(this_new_nodes_degrees) if len(this_new_nodes_degrees) > 0 else 0
        )
        mean_new_degrees[graph_idx] = this_mean_new_nodes
    model = sfm.AutoARIMA()
    prediction = model.forecast(y=mean_new_degrees, h=1)
    # print(f"new nodes degree = {int(np.ceil(prediction['mean'].item()))}")
    return int(np.ceil(prediction["mean"].item()))
