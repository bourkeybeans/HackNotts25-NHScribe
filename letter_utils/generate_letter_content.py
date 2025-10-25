import ollama
import json
import datetime

def generate_letter_content(letter_data: dict, llama_model: str = "llama3.2:1b") -> str:
    llama_client = ollama.Client()

    test_data_str = json.dumps(letter_data)

    patient = letter_data["patient"]
    address = patient["address"]
    name = patient["name"]
    sex = patient["sex"]
    date = datetime.datetime.today().date()

    prompt = f"""
    You are an NHS medical transcriptionist tasked with creating a realistic, 
    patient-friendly blood test results letter.

    Below is the patient data and results in JSON format for context:
    {test_data_str}

    ### Instructions:
    - Use the real patient details below (not placeholders):
    Name: {name}
    Sex: {sex}
    Address: {address}

    - Begin the letter with:
    {name}
    {address}
    {date}

    - Address the patient appropriately based on gender:
    - If sex = "M", use "Dear Mr. {name}"
    - If sex = "F", use "Dear Ms. {name}"
    - Otherwise, just use "Dear {name}"

    - Write in the tone and format of a genuine NHS results letter.
    - Explain the test results in plain, reassuring English.
    - Include test names, results, units, and normal ranges.
    - If a result is 'Low' or 'High', explain possible reasons gently and suggest what to do next.
    - If the result is normal, reassure the patient.
    - End with a polite, professional sign-off:

    Yours sincerely,
    NHScribe Official

    ### Output format:
    Only return the completed letter — no JSON, no code, no notes.
    """

    response = llama_client.generate(model=llama_model, prompt=prompt)

    return response.response
