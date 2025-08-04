# Tutorial

---

## **Flow**

The general flow of processing with Netseer is:

- Load a time-series list of graphs.
- Predict the next graph in the series.

## **Getting Started**

For this tutorial, I'm defaulting to using [uv](https://docs.astral.sh/uv/getting-started/installation/).
Otherwise set up a python project using pip/venv as standard and create a `main.py`

### **Setup**

Create a python project:

``` bash
uv init netseer-tutorial
cd netseer-tutorial
```

Add the Netseer package:

``` Python
uv add netseer # or pip install netseer
```

The tutorial takes place in the `main.py` file.

### **Loading**

There are two ways to create graphs:

- Creating your own list of graphs. Typically this would be a time-series list of graphs.
- Randomly generating a list of graphs using Netseer.

#### Using own graphs

If creating your own graphs, Netseer uses the python package `igraph` to handle graphs.  
Therefore, the created graphs need to be saved in a format that can be used by [`igraph.Graph.Read`](https://python.igraph.org/en/main/api/igraph.Graph.html#Read). For our tutorial we will used GML format graphs.

Save the list of graphs into a directory/folder relative to your project. For example in a /data/ directory.
E.g.:

``` ASCII
data/
├── graph_1.gml
├── graph_2.gml
└── graph_3.gml
```

Then create a list of absolute paths. This is easily done using pathlib and glob.

``` Python
# Get the directory/folder with all the graphs.
directory_path = Path.cwd() / Path("path/to/data")
# Use glob to get a list of absolute paths for .gml files.
graph_files = directory_path.glob("*.gml"))
```

The `graph_files` will now contain the path to each graph, as a list.  
Similar to: `["home/code/netseer/data/graph_1.gml", "home/code/netseer/data/graph_2.gml","home/code/netseer/data/graph_3.gml"]`

Then use the imported utils function `read_graph_list()` on the `graph_files`.  
This reads each .gml file in the `graph_files` and loads them into a list of graphs, loaded in memory.  
The graphs are loaded in the index order in `graph_files`.  
Use a numbering system for the .gml file names so that `sorted` can arrange the graphs paths in descending order.

``` Python
# If you need to sort the graph names.
graph_files = sorted(graph_files)
```

After the optional sorting:

``` Python
# Load the graphs into igraph using the list of gml files.
graph_list = utils.read_graph_list(graph_files)
```

The graphs loaded this way are ordered by their filename, in descending order.  
So graph_1 would be at index 0, graph_2 at index 1 etc.  
The order of graphs are important for the prediction.

#### Using random graphs

Alternatively, Netseer has a function to create a random list of graphs.  
Instead of using pathlib, glob and `read_graph_list()`, import generate_graph and use the function `generate_graph_list` to create a random graph list that is already stored in memory.

``` Python
from netseer import generate_graph

graph_list = generate_graph.generate_graph_list()
```

The `generate_graph_list()` function contains parameters to tailor the generated random graphs, such as growth rate.  
Refer to the references documentation for an explanation.

### **Prediction**

After loading the graphs into memory, use the imported prediction function `predict_graph()` to predict the next graph in the series.  
Change the `h` parameter in `predict_graph` to predict that many steps into the future. E.g. 1 step, 2 steps, 3 steps etc.

``` Python
# Then use the list of graphs for predictions.
predict = prediction.predict_graph(graph_list, h=1)
```
