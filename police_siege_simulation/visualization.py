from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from model import PoliceSuspectModel
from agents import Police, Suspect

def agent_portrayal(agent):
    """
    Define how agents are visualized on the grid.
    Only Police and Suspects are shown.
    """
    if isinstance(agent, Police):
        return {"Shape": "circle", "Color": "blue", "r": 0.5, "Layer": 1}
    elif isinstance(agent, Suspect):
        return {"Shape": "circle", "Color": "red", "r": 0.5, "Layer": 1}
    return None

class OutcomeElement(TextElement):
    """
    Display the current status of the game (police win, suspect win, or ongoing).
    """
    def render(self, model):
        if model.outcome:
            return f"<b>Outcome: {model.outcome}</b>"
        return "<b>Outcome: Ongoing</b>"

# Visualization elements
grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
chart = ChartModule(
    [{"Label": "Gun Store", "Color": "green"}],
    data_collector_name="datacollector"
)
outcome_element = OutcomeElement()

# Server setup
server = ModularServer(
    PoliceSuspectModel,
    [grid, chart, outcome_element],
    "Police-Suspect Simulation",
    {
        "width": 10,
        "height": 10,
        "num_police": UserSettableParameter("slider", "Number of Police", 5, 1, 20, 1),
        "num_suspects": UserSettableParameter("slider", "Number of Suspects", 10, 1, 20, 1),
        "initial_guns": UserSettableParameter("slider", "Initial Guns", 15, 0, 50, 1),
        "max_police": UserSettableParameter("slider", "Max Police Reinforcements", 5, 0, 10, 1),
    },
)

if __name__ == "__main__":
    server.launch()