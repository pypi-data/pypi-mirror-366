import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


from src.autoagentsai.graph import FlowGraph


def main():
    flow_graph = FlowGraph()
    flow_graph.add_node("node1", "text", {"x": 100, "y": 100})
    flow_graph.add_node("node2", "text", {"x": 200, "y": 200})
    flow_graph.add_edge("node1", "node2")
    flow_graph.compile()
    print(flow_graph.to_json())


if __name__ == "__main__":
    main()