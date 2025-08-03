"""Shows an example of how to use the Flow library to create a flowchart and send it via Redis."""

from flow.flowchart import FlowchartBuilder
from flow.redis_sender import RedisSender

flow = FlowchartBuilder()
flow.add_node("A", "Start")
flow.add_node("B", "Middle")
flow.add_node("C", "End")
flow.add_edge("A", "B")
flow.add_edge("B", "C")

chart = flow.build()

sender = RedisSender()
sender.send(chart)
