from flask import Flask, request, render_template, redirect
from generate import createPlan, buildChain
import json
from flask_socketio import SocketIO, send
from google.generativeai.types.generation_types import GenerateContentResponse

app = Flask(__name__)
socketio = SocketIO(app)


from auth import auth_bp
app.register_blueprint(auth_bp)

#    Returns main page
@app.route('/')
def index():
    return render_template('main_page.html')

#    This is called when the user sends in a message. It determines what type or request is happening and creates a chain of steps to execute. Returns to front end
@app.route('/api/generate/form_plan', methods=['POST'])
def generate():
    data = request.json
    request_steps = createPlan(data)
    return json.dumps(request_steps)

#    Socket to front end. This needs to be improved. Stays open 24/7 lol
#    Handles transfer from front end to back end of generated content. Gets sent a step in the chain along with the history and returns the generated form
@socketio.on('message')
def handle_message(msg):
    msg = json.loads(msg)
    send(json.dumps({"intent": "send_tool_chain", "content": msg['data']}))
    for content, stream_status, stream, tool in buildChain(msg['data'], msg['history']):
        if content == "content":
            if stream_status:
                send(json.dumps({"intent": "create_stream_card"}), to=request.sid)
                if isinstance(stream, GenerateContentResponse):
                    for token in stream:
                        try:
                            send(json.dumps({"token":token.text, "intent": "stream_token"}), to=request.sid)
                        except AttributeError as e:
                            send(json.dumps({"token": e, "intent": "stream_token"}))
                    send(json.dumps({"intent": "end_stream_card"}), to=request.sid)
                    
                else:
                    for token in stream:
                        send(json.dumps({"token":token.choices[0].delta.content, "intent": "stream_token"}))
                    send(json.dumps({"intent": "end_stream_card"}), to=request.sid)
            else:
                send(json.dumps({"tool": tool, "intent": "send_tool_content"}))

        else:
            if tool['stream'] == False:
                print(tool['tool_name'])
                print(tool['tool_purpose'])
                send(json.dumps({"tool": tool, "intent": "send_tool"}), to=request.sid)
    send(json.dumps({"intent": "end_tool_chain"}), to=request.sid)


#    This prototype for how auth will handle login required page.
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

#    No clue why I made this. Returns main_page.html
@app.route('/main', methods=['GET'])
def main():
    return render_template('main_page.html')


#    How I get around auth for testing. cheat.html doesn't require auth for all html and js to be sent
@app.route('/dashboard/cheat')
def cheat():
    return render_template('cheat.html')


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
