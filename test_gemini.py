import google.generativeai as genai

genai.configure(api_key="AIzaSyA2HqvjsIpmXJXVz_3q69W9M_vONGdca3I")

model = genai.GenerativeModel("models/gemini-2.5-flash")

response = model.generate_content("Say hello in one line")

print(response.text)
