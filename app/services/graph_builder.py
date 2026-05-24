import networkx as nx

from app.core.models import Scenario


def build_graph(scenario: Scenario) -> nx.Graph:
    """Build a complete undirected graph from a scenario."""
    graph = nx.Graph()
    graph.add_node("depot", x=scenario.depot.location.x, y=scenario.depot.location.y)

    for order in scenario.orders:
        graph.add_node(order.id, x=order.location.x, y=order.location.y)

    return graph
