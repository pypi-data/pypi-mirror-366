"""Prediction Module:

Typical Usage Example:
    ``` Python
    from netseer import utils, generate_graph, prediction
    from pathlib import Path

    # Get the directory/folder with all the graphs.
    directory_path = Path.cwd() / Path("path/to/data")
    # Use glob to get a list of absolute paths for .gml files.
    graph_files = directory_path.glob("*.gml"))

    # Load the graphs into igraph using the list of gml files.
    graph_list = utils.read_graph_list(graph_files)
    # Predict the next graph.
    predict = prediction.predict_graph(graph_list, h=1)
    ```

"""

from collections.abc import Iterable
from typing import Optional

import numpy as np
import igraph as ig
import igraph.operators.functions as igf
import pulp
import pulp.constants

import netseer.forecasting as forecasting
import netseer.utils as utils

WEIGHTS = "weights"


def predict_graph(
    graph_list: Iterable[ig.Graph],
    h: int = 5,
    conf_nodes=None,
    conf_degree: int = 90,
    weights_option: int = 4,
) -> ig.Graph:
    """From a list of graphs, predicts a new graph

    Args:
        graph_list: A list of graphs to be predicted on: See generate_graph_list()
        h: How many steps into the future the prediction should be.
        conf_nodes: -- TODO
        conf_degree: -- TODO
        weights_option: Int between 1-7 determines the weight of newly created edges.
            1-3: Weight 0 for all edges.
            4: Weight 1 for all edges.
            5: Linear scaling weights for new edges (x+1). E.g. 1, 2, 3
            6: Proportional Weights.
            7: Weight 0 for all edges, except for last edge which is 1.

    Returns:
        Predicted Graph.
    """

    print("Forecasting properties of the new graph")
    # predict the number of nodes for the predicted graph
    new_nodes, new_nodes_lower, new_nodes_upper = forecasting.predict_num_nodes(
        graph_list, h=h, conf_level=conf_nodes
    )
    # predict the degrees for the new nodes
    new_nodes_degrees = forecasting.predict_new_nodes_degrees(graph_list)

    # predict the degrees of the existing nodes
    existing_nodes_degrees = forecasting.predict_existing_nodes_degrees(
        graph_list, h=h, conf_level=conf_degree
    )

    total_edges = forecasting.predict_total_edges_counts(
        graph_list, h=h, conf_level=conf_degree
    )

    EDGES_CONF_LEVEL = "conf_high"  # "mean"
    print("Using forecasts to predict the new graph")
    mean_graph = predict_graph_from_forecasts(
        graph_list,
        new_nodes,
        existing_nodes_degrees[EDGES_CONF_LEVEL],
        new_nodes_degrees,
        total_edges[EDGES_CONF_LEVEL],
        conf_nodes,
        conf_degree,
        weights_option,
    )

    print("done")
    return mean_graph


def construct_union_graph(
    graph_list: list[ig.Graph],
    num_new_nodes: int,
    new_nodes_degrees,
    remove_vertices: Optional[int] = 0,
    weights_option: int = 2,
    weights_param=0,
    num_most_connected_nodes: int = 10,
):
    def weights_value(weights_option: int, index: int, num_graphs: int) -> float:
        # different options for assigning weights to each edge
        if weights_option <= 3:
            return 0
        if weights_option == 4:
            return 1
        if weights_option == 5:
            return index + 1
        if weights_option == 6:
            return 1 / (num_graphs - index)
        if weights_option == 7:
            return 1 if index == num_graphs - 1 else 0
        return 0

    num_graphs = len(graph_list)

    def this_weights_key(graph_idx):
        return f"{WEIGHTS}_{graph_idx}"

    # set the weights for each edge
    for graph_idx in range(num_graphs):
        graph_list[graph_idx].es[this_weights_key(graph_idx)] = weights_value(
            weights_option, graph_idx, num_graphs
        )
        graph_list[graph_idx].vs["name"] = list(range(graph_list[graph_idx].vcount()))
    # create the graph that is the union of every graph in the graphlist
    union_graph = igf.union(graph_list, byname=False)
    # combine the weights of the components of the union graph
    weights = np.zeros((union_graph.ecount(),), dtype=float)
    for graph_idx in range(num_graphs):
        this_weights_str = this_weights_key(graph_idx)
        this_weights = np.array(union_graph.es[this_weights_str], dtype=float)
        del union_graph.es[this_weights_str]
        np.nan_to_num(
            this_weights, copy=False, nan=0.0
        )  # this is for edges that exist somewhere in the union graph, but not in this graph
        if any(np.isnan(this_weights)):
            print(f"Error: nan weights for graph {graph_idx}")
        weights += this_weights
    weights /= np.max(weights)
    union_graph.es[WEIGHTS] = weights
    num_existing_edges = union_graph.ecount()

    # add potential new edges and their weights
    non_edges = utils.get_neighbours_of_neighbours(union_graph)
    if weights_option in [4, 5, 6]:
        non_edges_weight = np.quantile(weights, q=weights_param)  #
    elif weights_option == 7:
        non_edges_weight = weights_param
    else:
        nonedges_weight = 0
    union_graph.add_edges(non_edges, {WEIGHTS: non_edges_weight})

    if num_new_nodes > 0:
        # Add new nodes
        num_existing_nodes = union_graph.vcount()

        existing_node_degrees = np.array(union_graph.degree(), dtype=int)
        # Use only a fixed number of old vertices
        # Which vertices have the highest degree
        if weights_option == 3:
            num_most_connected_nodes *= 2
        num_most_connected_nodes = min(num_most_connected_nodes, union_graph.vcount())
        most_connected_nodes = np.argpartition(
            existing_node_degrees, kth=-num_most_connected_nodes
        )[
            -num_most_connected_nodes:
        ]  # attach potential edges to this number of nodes in the union graph, with the highest degrees
        union_graph.add_vertices(num_new_nodes)
        new_nodes = union_graph.vs[num_existing_nodes:].indices

        new_nodes_edges_weights = 0  # []*len(new_node_edges) #weight for the new node
        new_node_edges = [
            (old_node, new_node)
            for old_node in most_connected_nodes
            for new_node in new_nodes
        ]
        if weights_option in [1, 2]:
            # Binary weights - new nodes connected to all old nodes
            pass
        elif weights_option == 3:
            # Binary weights - new nodes connected to most connected old nodes
            pass
        elif weights_option in [4, 5, 6, 7]:
            # Proportional weights - new nodes connected to all old nodes
            # But the weights will be much smaller
            existing_nodes_quantiles = existing_node_degrees / (
                sum(existing_node_degrees)
            )
            existing_nodes_weights = np.quantile(a=weights, q=existing_nodes_quantiles)

        union_graph.add_edges(
            new_node_edges, attributes={WEIGHTS: new_nodes_edges_weights}
        )  #

        # use uniform weights for weights options 1, 2, and 3
        if weights_option in (1, 2, 3):
            union_graph.es[WEIGHTS] = 1

    return union_graph


def setup_lp_solver(
    union_graph: ig.Graph, max_node_degrees: list[int], total_edges: int
) -> pulp.LpProblem:
    # create object to run the integer linear programming solver
    problem = pulp.LpProblem(name="edge_solver", sense=pulp.constants.LpMaximize)
    weights = union_graph.es[WEIGHTS]
    variables = [
        pulp.LpVariable(str(e_idx), cat="Binary") for e_idx in range(len(weights))
    ]
    problem.setObjective(pulp.LpAffineExpression(zip(variables, weights)))
    # degree constraints for each node
    for node_idx in range(union_graph.vcount()):
        this_edges = union_graph.es.select(_source=node_idx).indices
        this_expression = pulp.LpAffineExpression(
            [(variables[edge], 1) for edge in this_edges]
        )
        this_constraint = pulp.LpConstraint(
            e=this_expression,
            sense=pulp.LpConstraintLE,
            rhs=max_node_degrees[node_idx],
            name=str(node_idx),
        )
        problem.addConstraint(this_constraint)
    # total edges constraint
    total_edges_expression = pulp.LpAffineExpression((v, 1) for v in variables)
    total_edges_constraint = pulp.LpConstraint(
        e=total_edges_expression,
        sense=pulp.LpConstraintLE,
        rhs=total_edges,
        name="total_edges",
    )
    problem.addConstraint(total_edges_constraint)

    # print(problem)

    return problem


def run_lp_solver(problem: pulp.LpProblem) -> list[int]:
    # run the linear programming solver, and extract the solution
    # this argument stops the solver from printing output - the relevant command(s) will change depending on which solver is used
    status = problem.solve(pulp.PULP_CBC_CMD(msg=False))  # , gapAbs=0.0001
    if status != pulp.constants.LpSolutionOptimal:
        print(
            f"Error running solver - {status=} - {pulp.constants.LpSolution[status]}"
        )  #
    vars = problem.variables()
    solution_edge_idxs = [int(edge.name) for edge in vars if edge.varValue > 0]
    return solution_edge_idxs


def make_solution_graph(
    union_graph: ig.Graph, solution_edge_idxs: list[int]
) -> ig.Graph:
    # solution_edges = []
    return union_graph.subgraph_edges(edges=solution_edge_idxs, delete_vertices=False)


def predict_graph_from_forecasts(
    graph_list: list[ig.Graph],
    new_nodes: int,
    existing_nodes_degrees,
    new_nodes_degrees: int,
    total_edges,
    conf_nodes: Optional[int] = None,
    conf_degree: Optional[int] = None,
    weights_option: int = 1,
) -> ig.Graph:
    # the maximum degree for each node
    max_node_degrees = None  # the maximim degree of each node in the solution graph
    if new_nodes > 0:
        num_existing_nodes = len(existing_nodes_degrees)
        max_node_degrees = np.ndarray((num_existing_nodes + new_nodes), dtype=int)
        max_node_degrees[0:num_existing_nodes] = existing_nodes_degrees
        max_node_degrees[num_existing_nodes:] = new_nodes_degrees
        pass
    else:
        max_node_degrees = existing_nodes_degrees

    # construction a graph that is the union of the graphs in the graph list
    print("Creating union graph for solver")
    union_graph = construct_union_graph(
        graph_list, new_nodes, new_nodes_degrees, weights_option=weights_option
    )

    # setup linear programming solver
    problem = setup_lp_solver(union_graph, max_node_degrees, total_edges)

    # solve problem
    print("Running LP Solver")
    solution_edge_idxs = run_lp_solver(problem)

    # turn the solution into a graph
    solution_graph = make_solution_graph(union_graph, solution_edge_idxs)

    # check that the solution meets the constraints
    solution_ok = utils.check_solution_against_constraints(
        solution_graph, union_graph, max_node_degrees, total_edges
    )
    print(f"Does the solution follow the constraints? {'yes' if solution_ok else 'no'}")

    # done
    return solution_graph
