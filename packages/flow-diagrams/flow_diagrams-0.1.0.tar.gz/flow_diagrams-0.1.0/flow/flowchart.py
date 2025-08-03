"""Creates a flowchart using the Flow library"""


class FlowchartBuilder:
    def __init__(self, direction="TD"):  # TD: Top Down
        self.direction = direction
        self.nodes = []
        self.edges = []

    def add_node(self, node_id, label):
        self.nodes.append(f'{node_id}["{label}"]')

    def add_edge(self, from_node, to_node, label=""):
        edge = f"{from_node} -->{f'|{label}|' if label else ''} {to_node}"
        self.edges.append(edge)

    def build(self):
        return f"flowchart {self.direction}\n" + "\n".join(self.nodes + self.edges)
