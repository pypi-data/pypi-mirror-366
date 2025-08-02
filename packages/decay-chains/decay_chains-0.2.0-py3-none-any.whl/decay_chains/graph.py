class DAGraph:
    def __init__(self, graph: dict[str, set[str]] | None = None):
        """
        Initialize a Directed Acyclic Graph.

        Parameters
        ----------
        graph : dict of str to set of str or None
            The graph structure to load. Keys of the dictionary are nodes in the
            tree, and values of the dictionary are sets containing all children
            nodes of the node represented by the key.
        """
        self.graph = graph

    def add_node(self, node: str, dependencies: set[str]):
        """
        Adds a node to the graph.

        Parameters
        ----------
        node : str
            The node to add to the graph.
        dependencies : set of str
            The dependencies of the node.
        """
        if self.graph is None:
            self.graph = {}
        self.graph[node] = dependencies

    def _dfs(self, path, paths, target):
        if self.graph is None:
            return
        node = path[-1]
        if node == target:
            paths.append(path.copy())
        if node in self.graph.keys():
            for subnode in self.graph[node]:
                path.append(subnode)
                self._dfs(path, paths, target)
                path.pop()

    def get_paths(self, endpoint: str):
        """
        Finds all paths that lead to the endpoint node.

        Parameters
        ----------
        endpoint : str
            The terminal node of paths to find.

        Returns
        -------
        list of list of str
            A list containing all paths to the endpoint.
        """
        if self.graph is None:
            return []
        nodes = list(self.graph.keys())
        all_paths = []
        for node in nodes:
            path = [node]
            paths = []
            self._dfs(path, paths, endpoint)
            all_paths += paths
        return all_paths
