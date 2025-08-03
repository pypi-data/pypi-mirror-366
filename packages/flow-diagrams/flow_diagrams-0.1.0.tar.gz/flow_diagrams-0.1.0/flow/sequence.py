"""Creates a sequence diagram using the Flow library."""


class SequenceBuilder:
    def __init__(self):
        self.lines = ["sequenceDiagram"]

    def add_actor(self, name, alias=None):
        if alias:
            self.lines.insert(1, f"participant {alias} as {name}")
        else:
            self.lines.insert(1, f"participant {name}")

    def add_call(self, sender, receiver, message):
        self.lines.append(f"{sender}->>{receiver}: {message}")

    def add_return(self, sender, receiver, message):
        self.lines.append(f"{sender}-->>{receiver}: {message}")

    def add_note(self, actor, note, position="right"):
        self.lines.append(f"Note {position} of {actor}: {note}")

    def build(self):
        return "\n".join(self.lines)
