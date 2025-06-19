import streamlit as st
import pandas as pd
import json

def display_detection_results(detection_data: str):
    """
    Displays the object detection results in a structured format.

    Args:
        detection_data (str): A JSON string containing the detected objects.
    """
    try:
        data = json.loads(detection_data)
        objects = data.get('objects', [])
        
        st.subheader("Detected Objects")
        
        if not objects:
            st.info("No objects were detected in the image.")
            return

        # Prepare data for the table
        display_data = []
        for obj in objects:
            display_data.append({
                "Object": obj.get('name', 'N/A'),
                "Count": obj.get('count', 'N/A'),
                "Colors": ", ".join(obj.get('color', []))
            })

        df = pd.DataFrame(display_data)
        st.table(df)

    except json.JSONDecodeError:
        st.error("Failed to decode the detection data. Displaying raw text instead.")
        st.text(detection_data)
    except Exception as e:
        st.error(f"An error occurred while displaying the results: {e}")
        st.text(detection_data) 