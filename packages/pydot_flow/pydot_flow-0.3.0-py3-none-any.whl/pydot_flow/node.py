from typing import List, TYPE_CHECKING
import pydot
import uuid

if TYPE_CHECKING:
    from pydot_flow import Chart


class Node:

    def __init__(
        self,
        graph: pydot.Graph,
        src_node_attrs: dict = None,
        src_node: pydot.Node = None,
        chart: "Chart" = None,
    ):
        self._chart = chart
        self._src_node_attrs = {} if src_node_attrs is None else src_node_attrs
        self.graph = graph
        self._src_node = (
            pydot.Node(name=str(uuid.uuid4()), **self._src_node_attrs)
            if src_node is None
            else src_node
        )
        self.graph.add_node(self._src_node)

    def get_node(self) -> pydot.Node:
        return self._src_node

    def get_graph(self) -> pydot.Graph:
        return self.graph

    def flow(
        self,
        src_port: str,
        dst_port: str = None,
        dst_node_attrs: dict = None,
        edge_attrs: dict = None,
        graph: pydot.Graph = None,
    ):
        dst_node_attrs = {} if dst_node_attrs is None else dst_node_attrs
        edge_attrs = {} if edge_attrs is None else edge_attrs

        if dst_port is None:
            dst_port = "".join(
                [
                    {"n": "s", "s": "n", "w": "e", "e": "w"}.get(direction)
                    for direction in list(src_port)
                ]
            )

        dst_node = pydot.Node(name="node_" + uuid.uuid4().hex, **dst_node_attrs)

        if "n" in src_port:
            src = self._src_node.get_name() + ":" + src_port
            dst = dst_node.get_name() + ":" + dst_port
            dir = "forward"
        if "e" in src_port:
            src = self._src_node.get_name() + ":" + src_port
            dst = dst_node.get_name() + ":" + dst_port
            dir = "forward"
        if "w" in src_port:
            src = dst_node.get_name() + ":" + dst_port
            dst = self._src_node.get_name() + ":" + src_port
            dir = "back"
        if "s" in src_port:
            src = self._src_node.get_name() + ":" + src_port
            dst = dst_node.get_name() + ":" + dst_port
            dir = "forward"

        if graph is None:
            graph = self.graph
        else:
            if graph.get_name() == "":
                graph.set_name("graph_" + uuid.uuid4().hex)
            _graphs: List[pydot.Graph] = self._chart.get_graph().get_subgraph_list() + [
                self._chart.get_graph()
            ]
            if not any([_graph.get_name() == graph.get_name() for _graph in _graphs]):
                self.graph.add_subgraph(graph)

        edge = pydot.Edge(src=src, dst=dst, dir=dir, **edge_attrs)
        graph.add_edge(edge)
        return Node(
            graph=graph,
            src_node=dst_node,
            src_node_attrs=dst_node_attrs,
            chart=self._chart,
        )
