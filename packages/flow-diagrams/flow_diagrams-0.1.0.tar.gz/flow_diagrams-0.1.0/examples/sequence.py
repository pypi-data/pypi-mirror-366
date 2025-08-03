"""Shows an example of how to use the Flow library to create a sequence diagram and send it via HTTP."""

from flow.sequence import SequenceBuilder
from flow.httpsender import HTTPSender

seq = SequenceBuilder()
seq.add_actor("Client")
seq.add_actor("Server")
seq.add_call("Client", "Server", "Request")
seq.add_return("Server", "Client", "Response")
seq.add_note("Client", "Client processes response")

chart = seq.build()
print(chart)

sender = HTTPSender()
sender.send(chart)
