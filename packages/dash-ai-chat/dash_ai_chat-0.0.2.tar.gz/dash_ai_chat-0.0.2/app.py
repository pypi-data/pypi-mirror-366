from dash_ai_chat import DashAIChat

app = DashAIChat(base_dir="/Users/me/Desktop/temp/test_chat_basdir")

import os

import dash_ai_chat

print("PATH:", dash_ai_chat.__path__)

print(os.getcwd())
print("---------")
print(*os.listdir(), sep="\n")
print("---------")
for key, val in app.config.items():
    print(key, ": ", val)
print("BASE_DIR:", app.BASE_DIR.absolute())

if __name__ == "__main__":
    app.run(debug=True)
