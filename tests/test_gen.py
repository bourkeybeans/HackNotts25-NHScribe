from letter_utils.generate_letter_content import generate_letter_content
test_data = {
  "status": "success",
  "batch_id": "b4c6d833-f1c7-4074-b6a9-dedaabe3b710",
  "patient": {
    "id": 1,
    "name": "Ron",
    "age": 18,
    "sex": "M",
    "address": "Golders Green",
    "conditions": ""
  },
  "results": [
    {
      "test_name": "Haemoglobin",
      "value": "118",
      "unit": "g/L",
      "flag": "Low",
      "reference_low": "115",
      "reference_high": "165",
      "source_file": "oneline.csv",
      "batch_id": "b4c6d833-f1c7-4074-b6a9-dedaabe3b710"
    }
  ]
}

print(generate_letter_content(test_data, "llama3"))