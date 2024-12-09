from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from model import PoliceSuspectModel
from agents import Police, Suspect, PoliceStation


def agent_portrayal(agent):
    if isinstance(agent, Police):
        return {"Shape": "circle", "Color": "blue", "r": 0.5, "Layer": 1}
    elif isinstance(agent, Suspect):
        return {"Shape": "circle", "Color": "red", "r": 0.5, "Layer": 1}
    elif isinstance(agent, PoliceStation):
        return {"Shape": "rect", "Color": "green", "w": 1, "h": 1, "Layer": 0}
    return None


class OutcomeElement(TextElement):
    def render(self, model):
        if model.outcome:
            return f"<b>Outcome: {model.outcome}</b>"
        return "<b>Outcome: Ongoing</b>"


grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
chart = ChartModule(
    [{"Label": "Gun Store", "Color": "green"}],
    data_collector_name="datacollector"
)
outcome_element = OutcomeElement()

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
