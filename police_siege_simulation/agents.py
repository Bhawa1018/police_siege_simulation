from mesa import Agent

class Message:
    """
    FIPA-compliant message structure.
    """
    def __init__(self, sender, receiver, performative, content):
        self.sender = sender
        self.receiver = receiver
        self.performative = performative
        self.content = content

    def __str__(self):
        return f"From: {self.sender} To: {self.receiver} [{self.performative}] Content: {self.content}"

class PoliceStation(Agent):
    def __init__(self, unique_id, model, initial_guns, max_police):
        super().__init__(unique_id, model)
        self.gun_store = initial_guns  # Initial stock of guns
        self.police_available = max_police  # Maximum number of police available for deployment
        self.message_queue = []  # Queue to hold messages (communication system)

    def give_guns(self, num_guns):
        """
        Allocate guns from the gun store based on requests from police officers.
        """
        guns_given = min(self.gun_store, num_guns)
        self.gun_store -= guns_given
        print(f"[PoliceStation] Dispatched {guns_given} gun(s). Remaining guns: {self.gun_store}")
        return guns_given

    def deploy_police(self):
        """
        Deploy a police officer and allocate guns if both resources are available.
        """
        if self.police_available > 0:
            self.police_available -= 1
            guns_for_new_police = 0
            if self.gun_store > 0:
                guns_for_new_police = self.give_guns(1)  # Allocate 1 gun to the new officer
            print(f"[PoliceStation] Dispatched 1 police officer with {guns_for_new_police} gun(s).")
            return guns_for_new_police  # Return the number of guns allocated to the new officer
        print("[PoliceStation] Deployment failed: No police available.")
        return 0

    def process_incoming_messages(self):
        """
        Process incoming messages from police officers requesting guns or other resources.
        """
        for message in self.message_queue:
            if message.performative == "REQUEST":
                if message.content["type"] == "guns":
                    # If the request is for guns, we check if we can fulfill it
                    requested_guns = message.content["amount"]
                    print(f"[PoliceStation] Received request from Police {message.sender} for {requested_guns} gun(s).")
                    guns_to_dispatch = self.give_guns(requested_guns)
                    # Send back a response to the requesting police officer
                    response = Message(
                        sender=self.unique_id,
                        receiver=message.sender,
                        performative="AGREE",
                        content={"guns_dispatched": guns_to_dispatch}
                    )
                    # Add the response to the police officer's message queue
                    police_agent = self.model.schedule.get_agent(message.sender)
                    police_agent.message_queue.append(response)
                else:
                    # Handle other types of requests here (e.g., special resources)
                    pass
            # Additional message types can be processed here if needed

        # Clear the message queue after processing
        self.message_queue.clear()

class Police(Agent):
    def __init__(self, unique_id, model, initial_guns=0):
        super().__init__(unique_id, model)
        self.guns = initial_guns  # Initialize with guns allocated from the station
        self.message_queue = []

    def step(self):
        # Check if police agent needs more guns (example condition)
        if self.guns < 3:  # A condition where police agent needs more guns
            message = Message(self.unique_id, "PoliceStation", "REQUEST", {"type": "guns", "amount": 3})
            self.model.police_station.message_queue.append(message)
        
        # Process incoming messages (like counter-offers from PoliceStation or other agents)
        for message in self.message_queue:
            if message.performative == "AGREE":
                self.guns += message.content["guns_dispatched"]
                print(f"[Police {self.unique_id}] Guns received: {message.content['guns_dispatched']}. Total guns: {self.guns}")
            elif message.performative == "COUNTER_OFFER":
                # Handle counter-offer: Police agent can decide to accept or propose a new request
                print(f"[Police {self.unique_id}] Received counter-offer: {message.content}")
                if self.guns < 3:  # Accept counter-offer if guns are still below the threshold
                    self.guns += message.content["guns_dispatched"]
                    print(f"[Police {self.unique_id}] Accepting counter-offer. New gun count: {self.guns}")
                else:
                    print(f"[Police {self.unique_id}] Rejecting counter-offer, still enough guns.")
            
            elif message.performative == "REQUEST":
                # Handle request from other police agents for gun sharing (collaboration)
                if isinstance(message.content, dict) and "guns_needed" in message.content:
                    guns_needed = message.content["guns_needed"]
                    if self.guns >= guns_needed:
                        self.guns -= guns_needed
                        sender = self.model.schedule.get_agent(message.sender)
                        sender.guns += guns_needed
                        print(f"[Police {self.unique_id}] Shared {guns_needed} guns with Police {sender.unique_id}.")
            
        self.message_queue.clear()

    def request_guns_from_station(self, guns_needed):
        """
        Method to request guns from the Police Station.
        """
        if self.guns < guns_needed:
            message = Message(self.unique_id, "PoliceStation", "REQUEST", {"type": "guns", "amount": guns_needed})
            self.model.police_station.message_queue.append(message)
            print(f"[Police {self.unique_id}] Requesting {guns_needed} guns from the Police Station.")

    def share_guns(self, neighbor, guns_needed):
        """
        Method for collaboration where one police agent shares guns with another.
        """
        if self.guns >= guns_needed:
            self.guns -= guns_needed
            neighbor.guns += guns_needed
            print(f"[Police {self.unique_id}] Shared {guns_needed} guns with Police {neighbor.unique_id}. New gun count: {self.guns}")
        else:
            print(f"[Police {self.unique_id}] Not enough guns to share with Police {neighbor.unique_id}.")

class Suspect(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        possible_moves = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        new_position = self.random.choice(possible_moves)
        self.model.grid.move_agent(self, new_position)