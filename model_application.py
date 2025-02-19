# Import the dependencies we need to run the code.
import os
import requests
import json
import gradio as gr
import numpy as np
import traceback
import pickle

# Get a few environment variables. These are so we:
# - Know what endpoint we should request
# - Set server name and port for Gradio
URL = os.getenv("INFERENCE_ENDPOINT")                       # You need to manually set this with an environment variable
GRADIO_SERVER_PORT = int(os.getenv("GRADIO_SERVER_PORT"))   # Automatically set by the Dockerfile
GRADIO_SERVER_NAME = os.getenv("GRADIO_SERVER_NAME")        # Automatically set by the Dockerfile

# Create a small function that sends data to the inference endpoint and recieves a prediction
def predict(distance_from_home,distance_from_last_transaction,ratio_to_median_purchase_price,repeat_retailer,used_chip,used_pin_number,online_order):

   data = [distance_from_home,distance_from_last_transaction,ratio_to_median_purchase_price,repeat_retailer,used_chip,used_pin_number,online_order]
    
   with open('scaler.pkl', 'rb') as handle:
         scaler = pickle.load(handle)
   data_scaled =  scaler.transform([data]).tolist()[0]
    
    payload = {
        "inputs": [
            {
                "name": "dense_input", 
                "shape": [1, 7], 
                "datatype": "FP32",
                "data": data_scaled 
            },
            ]
        }
    headers = {
        'content-type': 'application/json'
    }

    with open('scaler.pkl', 'rb') as handle:
         scaler = pickle.load(handle)

    try:
        response = requests.post(URL, json=payload, headers=headers)
        
        # Print the status code (good practice)
        print(f"Response Status Code: {response.status_code}")

        # Print the response body (text-based)
        print(f"Response Body (text): {response.text}")

        # If you expect JSON, parse it and print it nicely
    
        response_json = response.json()  # Try to parse as JSON
        print(f"Response Body (JSON): {json.dumps(response_json, indent=4)}") # Use json.dumps for pretty printing
    except json.JSONDecodeError:
        print("Response body is not valid JSON")
            
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        prediction = response.json()['outputs'][0]['data'][0]
        return "Fraud" if prediction >= 0.995 else "Not fraud"
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        traceback.print_exc()  # Print the full traceback for debugging
        return "Error: Could not connect to inference endpoint"  # Or a more informative message
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error parsing response: {e}")
        traceback.print_exc()
        return "Error: Invalid response from inference endpoint"


# Create and launch a Gradio interface that uses the prediction function to predict an output based on the inputs. 
# We also set up a few example inputs to make it easier to try out the application.
demo = gr.Interface(
    fn=predict, 
    inputs=["number","number","number","number","number","number","number"], 
    outputs="textbox",
    examples=[
        [57.87785658389723,0.3111400080477545,1.9459399775518593,1.0,1.0,0.0,0.0],
        [15.694985541059943,175.98918151972342,0.8556228290724207,1.0,0.0,0.0,1.0]
        ],
    title="Predict Credit Card Fraud"
    )

demo.launch(server_name=GRADIO_SERVER_NAME, server_port=GRADIO_SERVER_PORT)
