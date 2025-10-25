import ollama
import json
import datetime

def generate_letter_content(letter_data: dict, llama_model: str = "llama3.2:1b") -> str:
    llama_client = ollama.Client()

    test_data_str = json.dumps(letter_data)

    patient = letter_data["patient"]
    results = letter_data["results"]

    sex = patient["sex"]

    prompt = f"""
    You are an NHS medical transcriptionist tasked with creating a realistic, 
    patient-friendly blood test results letter.

    Below is the patient data and results in JSON format for context:
    {results}

    ### Instructions:
    - Use the real patient details below (not placeholders):
    Sex: {sex}

    - Write in the tone and format of a genuine NHS results letter.
    - Do not address the patient al all.
    - Explain the test results in plain, reassuring English.
    - Include test names, results, units, and normal ranges.
    - If a result is 'Low' or 'High', explain possible reasons gently and suggest what to do next.
    - If the result is normal, reassure the patient.
    - Do not end with a sign-off:

    ### Output format:
    Only return the completed letter — no JSON, no code, no notes.
    """

    print("Generating letter content...")
    response = llama_client.generate(model=llama_model, prompt=prompt)

    return response.response
