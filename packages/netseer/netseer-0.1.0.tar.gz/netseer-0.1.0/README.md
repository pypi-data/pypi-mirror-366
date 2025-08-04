# Netseer

## Predicting graph structure from a time series of graphs

This is a Python implementation of [*netseer*](https://arxiv.org/html/2401.04280v1).  
Netseer is a tool that outputs a predicted graph based on a time series graph sequence
---

## Purpose

The goal of netseer is to predict the graph structure including new nodes and edges from a time series of graphs.  
The methodology is explained in the preprint (Kandanaarachchi et al. 2025).

![Image of a time-series list of graphs and a predicted graph.](docs/img/netseer.svg "netseer")

## Installation

This package is available on PyPI, and can be installed with PIP or with a Package Manager:

``` Bash
pip install netseer # or uv add netseer
```

## Quick Example

Generating an example graph list:

``` Python
from netseer import generate_graph

graph_list = generate_graph.generate_graph_list()
```

The `generate_graph_list()` function has parameters for templating what types of graphs to generate. Information about these can be found in the reference docs.

Predicting on that graph:

``` Python
from netseer import prediction

predict = prediction.predict_graph(graph_list, h=1)
```

Increasing the `h` parameter increases how many steps into the future the prediction is, with `h=1` being 1 step in the graph sequence.

## References

Kandanaarachchi, Sevvandi, Ziqi Xu, Stefan Westerlund, and Conrad Sanderson. 2025.
  “Predicting Graph Structure via Adapted Flux Balance Analysis.” <https://arxiv.org/abs/2507.05806>.
