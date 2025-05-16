import threading
import webbrowser
import os
import time
from typing import List, Dict

# Flask imports
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
)

# ROS imports
from rclpy.node import Node

# Internal imports
from ros_create3_agent.robot.robot_state import get_robot_state
from ros_create3_agent.logging import get_logger
from ros_create3_agent.rosa_config import WEB_PORT, MAX_CHAT_HISTORY

# Get a logger for this module
logger = get_logger(__name__)

# Global variables
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
)

# Set in initialize()
agent_node = None
agent_rosa = None
robot_state = None

# Our own chat history (list of dicts: {content, sender})
chat_history = []


# Helper to trim chat history
def _trim_chat_history():
    global chat_history
    if len(chat_history) > MAX_CHAT_HISTORY:
        chat_history = chat_history[-MAX_CHAT_HISTORY:]


def _add_user_message(content: str):
    chat_history.append({"content": content, "sender": "user"})
    _trim_chat_history()


def add_robot_message(content: str):
    chat_history.append({"content": content, "sender": "robot"})
    _trim_chat_history()


def _add_agent_message(content: str):
    chat_history.append({"content": content, "sender": "agent"})
    _trim_chat_history()


def initialize(node: Node, rosa_agent) -> None:
    """Initialize the web interface for the Create 3 robot agent."""
    global agent_node, agent_rosa, robot_state
    agent_node = node
    agent_rosa = rosa_agent
    robot_state = get_robot_state(node)
    welcome_msg = "Welcome to the Create 3 Robot Assistant. How can I help you today?"
    _add_agent_message(welcome_msg)
    web_thread = threading.Thread(target=_run_flask_app, daemon=True)
    web_thread.start()
    time.sleep(2)
    webbrowser.open(f"http://localhost:{WEB_PORT}")
    logger.info(f"Web interface initialized on http://localhost:{WEB_PORT}")


def _get_chat_history() -> List[Dict[str, str]]:
    """Return our own chat history for the web UI."""
    return list(chat_history)


def _run_flask_app() -> None:
    """Run the Flask app in a separate thread."""
    app.run(host="0.0.0.0", port=WEB_PORT, threaded=True, debug=False)


def _process_user_input(user_input: str) -> str:
    logger.info(f"Processing command via web: {user_input}")
    # Add user message immediately
    _add_user_message(user_input)
    try:
        # Call ROSA agent, get response (AI message)
        response = agent_rosa.invoke(user_input)
        # Add agent (AI) message
        _add_agent_message(response)
        return response
    except Exception as e:
        error_msg = f"Error processing command: {str(e)}"
        logger.error(error_msg)
        _add_agent_message(error_msg)
        return error_msg


@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html", max_chat_history=MAX_CHAT_HISTORY)


@app.route("/api/chat", methods=["GET"])
def get_chat():
    """API endpoint to get chat history."""
    return jsonify({"history": _get_chat_history(), "status": robot_state.get_state()})


@app.route("/api/chat", methods=["POST"])
def post_message():
    """API endpoint to post a new message."""
    if not request.json or "message" not in request.json:
        return jsonify({"error": "Invalid request"}), 400

    user_input = request.json["message"]

    # Process the message
    response = _process_user_input(user_input)

    # Return updated chat history
    return jsonify(
        {
            "history": _get_chat_history(),
            "status": robot_state.get_state(),
            "response": response,
        }
    )
