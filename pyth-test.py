import google.generativeai as genai

# Replace with your actual Gemini API key
genai.configure(api_key="AIzaSyBLp5GkaWs-yp9zlz_c7so6f_nz_2EoJsw")

# List available models
print("Available models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  {model.name}")