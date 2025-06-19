import matplotlib.pyplot as plt
from typing import List
from emotion import Emotion

def plot_emotions(emotions: List[Emotion], title: str) -> plt.Figure:
    """
    Creates a horizontal bar chart of emotion scores.

    Args:
        emotions: A list of Emotion objects.
        title: The title for the chart.

    Returns:
        A Matplotlib Figure object containing the plot.
    """
    names = [e.name.capitalize() for e in emotions]
    scores = [e.score for e in emotions]

    fig, ax = plt.subplots()
    ax.barh(names, scores, color='skyblue')
    ax.set_xlabel('Score')
    ax.set_ylabel('Emotion')
    ax.set_title(title)
    ax.set_xlim(0, 1)

    for index, value in enumerate(scores):
        ax.text(value, index, f' {value:.2f}')

    plt.tight_layout()
    return fig
