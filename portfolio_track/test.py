import google.generativeai as genai
genai.configure(api_key="AIzaSyCWuqTcJMr6WL-Abff-18QWw8XUyfGjKfw")

for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(m.name)
