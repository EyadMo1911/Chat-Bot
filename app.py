from flask import Flask, render_template, request
import mainn  # replace this with the name of your Python file containing the chat function

app = Flask(__name__,template_folder='tem')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg')
    bot_response = mainn.chat(user_text)
    return bot_response

if __name__ == "__main__":
    app.run()
