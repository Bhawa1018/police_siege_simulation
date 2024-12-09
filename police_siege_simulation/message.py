class Message:
    def __init__(self, sender, receiver, performative, content):
        """
        Create a FIPA-compliant message.
        :param sender: Unique ID of the sender agent
        :param receiver: Unique ID of the receiver agent
        :param performative: FIPA performative (e.g., "REQUEST", "AGREE", etc.)
        :param content: Dictionary with additional information
        """
        self.sender = sender
        self.receiver = receiver
        self.performative = performative
        self.content = content
