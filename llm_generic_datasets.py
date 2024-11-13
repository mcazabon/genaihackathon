import json
import openai
import os
import re
import time

# Set your Azure-specific parameters
endpoint = os.getenv("ENDPOINT_URL", "")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-35-turbo")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "")

# Ensure the API key is set
if not subscription_key:
    raise ValueError("AZURE_OPENAI_API_KEY environment variable not set")

# Configure the OpenAI API client
openai.api_type = "azure"
openai.api_base = endpoint
openai.api_version = "2024-05-01-preview"
openai.api_key = subscription_key

def generate_failure_reasons(prompt, retries=3):
    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                engine=deployment,
                messages=[
                    {"role": "system", "content": "You are an assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            response_text = response.choices[0].message['content'].strip()
            print(f"Response Text: {response_text}")

            # Extract JSON content from the response text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                failure_reason = json.loads(json_match.group(0))
                return failure_reason
            else:
                print(f"Failed to extract JSON from response on attempt {attempt + 1}: {response_text}")
        except Exception as e:
            print(f"Error generating failure reasons on attempt {attempt + 1}: {e}")
        time.sleep(3)  # Delay before retrying

    # Fallback mechanism
    print("All attempts failed. Returning default failure reason.")
    return {
        "FailureReason": "Unknown Error",
        "Description": "Failed to generate failure reason after multiple attempts.",
        "Resolution": "Please try again later or contact support."
    }

# Define the base prompt for generating failure reasons
base_prompt = "Generate 1 failure reason for Citrix client or VDI Session with description and resolution in the JSON format as follows: {\"FailureReason\": \"Reason\", \"Description\": \"Description\", \"Resolution\": \"Resolution\"}"

# Generate 100 failure reasons
failure_reasons = []
for i in range(1000):
    generated_text = generate_failure_reasons(base_prompt)
    if generated_text:
        failure_reasons.append(generated_text)

# Create the final dataset
dataset = {"Failure_Reasons": failure_reasons}

# Save to a JSON file
with open("failure_reasons_rev2.json", "w") as json_file:
    json.dump(dataset, json_file, indent=4)

print("JSON dataset with 1000 failure reasons created successfully.”)