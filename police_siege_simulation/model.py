import matplotlib.pyplot as plt
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agents import Police, Suspect, PoliceStation

class PoliceSuspectModel(Model):
    def __init__(self, width, height, num_police, num_suspects, initial_guns, max_police):
        super().__init__()
        self.num_police = num_police
        self.num_suspects = num_suspects
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)
        self.running = True
        self.outcome = None

        # Create the police station
        self.police_station = PoliceStation("PoliceStation", self, initial_guns, max_police)

        # Deploy initial police agents
        for i in range(self.num_police):
            police = Police(f"Police_{i}", self)
            self.grid.place_agent(police, self.grid.find_empty())
            self.schedule.add(police)

        # Add initial suspects
        for i in range(self.num_suspects):
            suspect = Suspect(f"Suspect_{i}", self)
            self.grid.place_agent(suspect, self.grid.find_empty())
            self.schedule.add(suspect)

        # Data collector
        self.datacollector = DataCollector(
            model_reporters={ 
                "Gun Store": lambda m: m.police_station.gun_store,
                "Police Available": lambda m: m.police_station.police_available,
                "Police Count": lambda m: len([a for a in m.schedule.agents if isinstance(a, Police)]),
                "Suspect Count": lambda m: len([a for a in m.schedule.agents if isinstance(a, Suspect)]),
            },
            agent_reporters={"Guns": lambda a: a.guns if isinstance(a, Police) else None}
        )

        # Counter to control suspect addition
        self.suspect_add_counter = 0

    def deploy_new_police(self):
        """
        Deploy additional police from the station if available.
        """
        if self.police_station.deploy_police():
            new_police = Police(f"Police_{len([a for a in self.schedule.agents if isinstance(a, Police)])}", self)
            self.grid.place_agent(new_police, self.grid.find_empty())
            self.schedule.add(new_police)

    def add_new_suspects(self):
        """
        Add new suspects automatically with a delay.
        This is controlled by the `suspect_add_counter`.
        """
        if self.suspect_add_counter >= 3:  # Delay by adding a suspect every 3 steps
            if len([a for a in self.schedule.agents if isinstance(a, Suspect)]) < 50:  # Example max number of suspects
                new_suspect = Suspect(f"Suspect_{len([a for a in self.schedule.agents if isinstance(a, Suspect)])}", self)
                self.grid.place_agent(new_suspect, self.grid.find_empty())
                self.schedule.add(new_suspect)
            self.suspect_add_counter = 0  # Reset the counter after adding a suspect
        else:
            self.suspect_add_counter += 1  # Increment the counter every step

    def step(self):
        # Deploy police if suspects outnumber police on the grid
        num_police = len([a for a in self.schedule.agents if isinstance(a, Police)])
        num_suspects = len([a for a in self.schedule.agents if isinstance(a, Suspect)])

        # Request reinforcements if there are more suspects than police
        if num_suspects > num_police:
            print(f"[Model] Requesting reinforcement: {num_suspects - num_police} police needed.")
            self.deploy_new_police()

        # Add new suspects slower than police reinforcements
        self.add_new_suspects()

        # Check if there are guns available
        guns_available = self.police_station.gun_store > 0
        for police in self.schedule.agents:
            if isinstance(police, Police):
                if not guns_available:
                    police.guns = 0  # Release police without guns if no guns available
                else:
                    police.guns = 1  # Equip police with one gun if available (assuming 1 gun per police)

        # Collect data and advance the model step
        self.datacollector.collect(self)
        self.schedule.step()

        # Check win conditions based on guns and police count
        num_police_with_guns = len([a for a in self.schedule.agents if isinstance(a, Police) and a.guns > 0])

        if self.police_station.police_available == 0 and num_suspects > num_police:
            print("[Model] Suspects Win! All police resources exhausted.")
            self.outcome = "Suspects Win"
            self.running = False
        elif num_police_with_guns >= num_suspects:
            print("[Model] Police Win! Suspects under control.")
            self.outcome = "Police Win"
            self.running = False
        elif num_police == 0 or num_police_with_guns == 0:
            print("[Model] Suspects Win! No police resources available.")
            self.outcome = "Suspects Win"
            self.running = False

