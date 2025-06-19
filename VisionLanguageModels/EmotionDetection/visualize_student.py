import matplotlib.pyplot as plt
from typing import List
from .emotion import Emotion

def plot_emotions(emotions: List[Emotion], title: str) -> plt.Figure:
    """
    Creates a horizontal bar chart of emotion scores.

    Args:
        emotions: A list of Emotion objects.
        title: The title for the chart.

    Returns:
        A Matplotlib Figure object containing the plot.
    """
    # TODO: Extract emotion names and scores into separate lists.
    # You should iterate through the 'emotions' list and collect the 'name'
    # and 'score' attributes from each Emotion object.
    names = []
    scores = []

    # TODO: Create a Matplotlib figure and axes for the plot.
    # Use plt.subplots() to get a figure and an axes object to draw on.
    fig, ax = (None, None)

    # TODO: Create a horizontal bar chart using the axes object.
    # Use the ax.barh() function with the names and scores.
    pass

    # TODO: Set the chart's title, x-label, and y-label.
    # Also, set the x-axis limit to be from 0 to 1, as the scores are in this range.
    pass

    # TODO: Return the Matplotlib figure object.
    # The Streamlit app will use this figure to display the chart.
    return fig
