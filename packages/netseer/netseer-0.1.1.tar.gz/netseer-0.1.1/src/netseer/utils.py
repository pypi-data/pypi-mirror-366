"""Utility functions that help with dataloading

Typical functions:
    ``` Python
    from netseer import utils, prediction
    from pathlib import Path

    # Get the directory/folder with all the graphs.
    directory_path = Path.cwd() / Path("path/to/data")
    # Use glob to get a list of absolute paths for .gml files.
    graph_files = directory_path.glob("*.gml"))

    # Load the graphs into igraph using the list of gml files.
    graph_list = utils.read_graph_list(graph_files)

    # Then use the list of graphs for predictions.
    predict = prediction.predict_graph(graph_list, h=1)
    ```

    read_graph_list()
"""

import pickle
import math
import numpy as np
import numpy.linalg as npla
import igraph as ig


def get_neighbours_of_neighbours(gr: ig.Graph) -> np.ndarray:
    # get neighbours-of-neighours of a graph - edges where there's an edge from A to B and from B to C, but not A to C
    # returns an (n, 2) ndarray of integers that is a list of (source node, target node) pairs
    adj1 = gr.get_adjacency_sparse()
    adj2 = adj1 * adj1  # neighbours of neighbours
    non = np.vstack(
        np.nonzero((adj2 - adj1) > 0)
    ).T  # neighbours of neighbours, not including existing edges
    non = non[non[:, 0] < non[:, 1]]  # get only one triangle of edges

    return non


def read_graph_list(filenames: list[str]) -> list[ig.Graph]:
    """Reads a list graphs from disk.

    The graphs are read in index order, therefore the first graph in the time-series is at index 0.

    Args:
        filenames: A list of absolute paths to ig.read compatible graphs. E.g. *.gml files.

    Returns:
        A list of read graphs.
    """
    # read a list of saved graph files
    print(f"Reading in graph files: {filenames}")
    return [ig.read(filename) for filename in filenames]


def read_pickled_list(filename: str) -> list[ig.Graph]:
    """Reads a saved list of graphs from a .pkl file.

    Args:
        filename: Absolute path to the .pkl file.

    Returns:
        A list of graphs.
    """
    # read a graph list that is stored in a single pickled file
    print(f"Reading pickled graph list from {filename}")
    return pickle.load(filename)


def check_solution_against_constraints(
    solution_graph: ig.Graph,
    union_graph: ig.Graph,
    max_node_degrees: list[int],
    total_edges_constraint: int,
) -> bool:
    all_ok = True
    # check total number of edges
    num_solution_edges = solution_graph.ecount()
    if num_solution_edges > int(total_edges_constraint):
        print(
            f"num solution edges = {num_solution_edges}, total_edges constraint = {total_edges_constraint}, union_graph edges= {union_graph.ecount()}"
        )
        all_ok = False

    # check the degree constraints of each node
    over_degree_capacity = [
        n
        for n in range(solution_graph.vcount())
        if solution_graph.degree()[n] > int(max_node_degrees[n])
    ]
    if len(over_degree_capacity) > 0:
        for n in over_degree_capacity:
            print(
                f"degree of Node {n}: {solution_graph.degree()[n]} is larger than its constraint: {int(max_node_degrees[n])}"
            )
            all_ok = False
            continue

    if num_solution_edges >= int(total_edges_constraint):
        return all_ok

    # if not all edges were used, check for any edges that could have been added to the graph
    print(f"Nodes with spare degrees:")
    spare_degrees = []
    for n in range(union_graph.vcount()):
        solution_degree = solution_graph.degree()[n]
        degree_constraint = int(max_node_degrees[n])
        if solution_degree == degree_constraint:
            continue
        for e in union_graph.es(_source=n):
            other = e.source if e.target == n else e.target
            if solution_graph.degree()[other] >= int(max_node_degrees[other]):
                continue
            if solution_graph.are_connected(n, other):
                continue
            spare_degrees.append((n, other, e))
            print(
                f"Spare connection from {n}: {solution_degree} < {degree_constraint} to {other}: {solution_graph.degree()[other]} < {int(max_node_degrees[other])} through edge {e.index}"
            )
            all_ok = False

    return all_ok


def triangle_density(gr: ig.Graph) -> float:
    def count_triangles(gr: ig.Graph) -> np.ndarray:
        triangles = gr.list_triangles()
        counts = np.zeros(gr.vcount(), dtype=int)
        for triangle in triangles:
            for vertex in triangle:
                counts[vertex] += 1
        return counts

    return sum(count_triangles(gr)) / (
        gr.vcount() * (gr.vcount() - 1) * (gr.vcount() - 2) / 6
    )


def evaluation(actual_graph: ig.Graph, predicted_graph: ig.Graph) -> dict:
    # evaluate the performance of the prdiction by comparing a gredicted graph to an actual graph

    # Prediction stats for pred
    vcount_err = abs(predicted_graph.vcount() / actual_graph.vcount() - 1)
    ecount_err = abs(predicted_graph.ecount() / actual_graph.ecount() - 1)

    def edge_density(gr: ig.Graph) -> float:
        return gr.ecount() / (gr.vcount**2)

    edge_density_err = abs(predicted_graph.density() - actual_graph.density())
    triangle_density_err = abs(
        triangle_density(predicted_graph) - triangle_density(actual_graph)
    )
    max_degree_err = abs(max(predicted_graph.degree()) / max(actual_graph.degree()) - 1)

    d = dict(
        vcount_err=vcount_err,
        ecount_err=ecount_err,
        edge_density_err=edge_density_err,
        triangle_density_err=triangle_density_err,
        max_degree_err=max_degree_err,
    )
    return d


def arrange_matrix(mat: np.ndarray) -> np.ndarray:
    rowsums = np.sum(mat, axis=1)
    order_row = np.flip(np.argsort(rowsums))
    mat2 = mat[order_row, :]

    colsums = np.sum(mat, axis=0)
    order_col = np.flip(np.argsort(colsums))
    mat3 = mat2[:, order_col]

    return mat3


def diff_metrics(act_adj: np.ndarray, pred_adj: np.ndarray) -> dict:
    # positives to be denoted by 1 and negatives with 0
    if act_adj.shape != pred_adj.shape:
        raise ValueError(
            "The actual and predicted adjacency lists must have the same shapes"
        )
    n = act_adj.size
    tp = np.sum((act_adj == 1) & (pred_adj == 1))
    tn = np.sum((act_adj == 0) & (pred_adj == 0))
    fp = np.sum((act_adj == 0) & (pred_adj == 1))
    fn = np.sum((act_adj == 1) & (pred_adj == 0))
    prec = (tp + tn) / n
    sn = tp / (tp + fn)
    sp = tn / (tn + fp)
    precision = (tp / (tp + fp)) if ((tp + fp) != 0) else 0
    recall = tp / (tp + fn)
    fmeasure = (
        (2 * precision * recall / (precision + recall))
        if ((precision + recall) != 0)
        else 0
    )
    return dict(
        N=n,
        true_pos=tp,
        true_neg=tn,
        false_pos=fp,
        false_neg=fn,
        accuracy=prec,
        sensitivity=sn,
        specificity=sp,
        gmean=math.sqrt(sn * sp),
        precision=precision,
        recall=recall,
        fmeasure=fmeasure,
    )


def eval_metrics2(actual_graph: ig.Graph, predicted_graph: ig.Graph) -> dict:
    new_vert = None
    node_error = (
        predicted_graph.vcount() - actual_graph.vcount()
    ) / actual_graph.vcount()

    if node_error > 0:
        new_vert = predicted_graph.vcount() - actual_graph.vcount()
        actual_graph.add_vertices(new_vert)
    elif node_error < 0:
        new_vert = actual_graph.vcount() - predicted_graph.vcount()
        predicted_graph.add_vertices(new_vert)

    adj_act = np.array(actual_graph.get_adjacency())
    adj_pred = np.array(predicted_graph.get_adjacency())

    def norm(array: np.ndarray) -> float:
        ord = "fro" if array.ndim > 1 else 2
        return npla.norm(array, ord=ord)

    # arrange rows by row sums and columns by column sums,
    adj_act2 = arrange_matrix(adj_act)
    adj_pred2 = arrange_matrix(adj_pred)
    adjacency_error = norm(adj_pred2 - adj_act2) / norm(adj_act2)

    deg_act = np.array(actual_graph.degree())
    deg_prd = np.array(predicted_graph.degree())
    deg_cosine_sim = sum(deg_act * deg_prd) / (norm(deg_act) * norm(deg_prd))

    lap_act = actual_graph.laplacian()
    lap_prd = predicted_graph.laplacian()

    eig_act = npla.eigvals(lap_act)
    eig_prd = npla.eigvals(lap_prd)
    eig_cosine_sim = sum(eig_act * eig_prd) / (norm(eig_act) * norm(eig_prd))

    evaluation_metrics = dict(
        node_error=node_error,
        adjacency_error=adjacency_error,
        degree_cosine=deg_cosine_sim,
        lap_eigen_cosine=eig_cosine_sim,
    )

    difference_metric = diff_metrics(adj_act, adj_pred)
    evaluation_metrics.update(difference_metric)

    return evaluation_metrics
