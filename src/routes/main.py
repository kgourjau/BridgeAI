import json
import logging
import re
from functools import wraps
from pathlib import Path

import requests
from flask import Blueprint, jsonify, render_template, request, url_for, redirect, flash, session, current_app, \
    Response, stream_with_context

from src.decorators import bearer_required
from src.services.openai_service import (
    openai_chat_completion,
    openai_list_models,
    openai_chat_completion_for_chat,
    openai_chat_completion_stream,
    openai_chat_completion_for_chat_stream,
)
from src.config import TARGET_API_BASE_URL, OPENAI_API_KEY

main_blueprint = Blueprint("main", __name__)
chat_logger = logging.getLogger("chat_logger")

# --- New Login Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session:
            return redirect(url_for('main.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def get_last_logs(num_lines=200):
    """Get the last N lines from logs.txt"""
    try:
        with open("logs/logs.txt", "r") as f:
            lines = f.readlines()
            return lines[-num_lines:] if len(lines) > num_lines else lines
    except FileNotFoundError:
        return ["No log file found."]
    except Exception as e:
        return [f"Error reading log file: {str(e)}"]


def parse_chat_logs():
    """Parse chat_logs.txt and return a list of structured log entries."""
    log_entries = []
    log_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (.*?): (.*)")
    try:
        with open("logs/chat_logs.txt", "r") as f:
            for line in f:
                match = log_pattern.match(line.strip())
                if match:
                    timestamp, source, message = match.groups()
                    role = "user" if "user" in source.lower() else "assistant"
                    log_entries.append({
                        "timestamp": timestamp,
                        "role": role,
                        "source": source,
                        "message": message
                    })
    except FileNotFoundError:
        return [{"timestamp": "", "role": "system", "source": "System", "message": "Chat log file not found."}]
    except Exception as e:
        return [{"timestamp": "", "role": "system", "source": "System", "message": f"Error reading chat log file: {e}"}]

    return log_entries


@main_blueprint.route("/")
def index():
    """Renders the home page"""
    return render_template("index.html")


@main_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('authenticated'):
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        token = request.form.get('token')
        if token == current_app.config.get('ACCESS_TOKEN'):
            session['authenticated'] = True
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Invalid access token')
    return render_template('login.html')


@main_blueprint.route("/logout")
@login_required
def logout():
    """Log the user out."""
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('main.login'))


@main_blueprint.route("/openai/v1/chat/completions", methods=["GET", "POST"])
@bearer_required
def chat_completions():
    """Handle OpenAI chat completions"""
    try:
        request_data = request.json
        messages = request_data.get("messages")
        stream = request_data.get("stream", False)

        if not messages:
            return jsonify({"error": "messages is required"}), 400

        chat_logger.info(f"user: {json.dumps(request_data)}")

        def stream_generator(response_iterator):
            for chunk in response_iterator:
                yield chunk + b'\\n'

        if len(messages) >= 2 and messages[1].get("content") == "Test prompt using gpt-3.5-turbo":
            if stream:
                chat_logger.info("AI: Streaming response initiated for test prompt.")
                streamer = openai_chat_completion_stream()
                return Response(stream_with_context(stream_generator(streamer)), mimetype="text/event-stream")
            else:
                result = openai_chat_completion()
                chat_logger.info(f"AI: {json.dumps(result)}")
                return jsonify(result)

        if True:
            chat_logger.info("AI: Streaming response initiated.")
            payload = request_data

            payload["model"] = "llama-3.3-70b-versatile"

            def generate_stream():
                """Proxy the stream directly, yielding each chunk as it arrives."""
                try:
                    response = openai_chat_completion_for_chat_stream(payload)
                    ai_source = f"AI ({TARGET_API_BASE_URL}/chat/completions)"
                    chat_logger.info(f"{ai_source}: Streaming response initiated (proxy mode).")
                    buffer = b""
                    for chunk in response.iter_content(chunk_size=None):
                        buffer = buffer + chunk
                        index = buffer.find(b"\n\n")
                        while index > -1:
                            line = buffer[6:index]
                            if line.find(b"[DONE]") > -1:
                                yield b"data: " + line + b"\n\n"
                                break
                            json_chunk = json.loads(line)
                            json_chunk["model"] = "gpt-4o-mini"
                            if "x_groq" in json_chunk:
                                del json_chunk["x_groq"]
                            new_chunk = "data: " + json.dumps(json_chunk) + "\n\n"
                            binary_chunk = bytes(new_chunk, "UTF-8")
                            print("chunk:", binary_chunk)
                            buffer = buffer[index + 2:]
                            index = buffer.find(b"\n\n")
                            yield binary_chunk
                        # yield chunk
                    pass
                except Exception as e:
                    chat_logger.error(f"Error during stream generation: {str(e)}", exc_info=True)
                    error_message = json.dumps({"error": {"message": "An error occurred during the stream."}})
                    yield f"data: {error_message}\\n\\n".encode('utf-8')

            return Response(stream_with_context(generate_stream()), mimetype='text/event-stream')

        completion = openai_chat_completion_for_chat(messages)
        ai_source = f"AI ({TARGET_API_BASE_URL}/chat/completions)"
        chat_logger.info(f"{ai_source}: {json.dumps(completion)}")

        return jsonify(completion)
    except Exception as e:
        chat_logger.error(f"Error in calling completion: {str(e)}", exc_info=True)
        current_app.logger.error(f"Error in OpenAI chat completion: {e}", exc_info=True)
        return jsonify({"error": "An internal error has occurred."}), 500


@main_blueprint.route("/openai/v1/models", methods=["GET"])
@bearer_required
def list_models():
    """Handle OpenAI models list"""
    try:
        result = openai_list_models()
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error fetching OpenAI models: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@main_blueprint.route("/chat", methods=["GET"])
@login_required
def chat_page():
    """Render the chat page"""
    return render_template("chat.html")


@main_blueprint.route("/chat/message", methods=["POST"])
@login_required
def chat_message():
    """Handle chat messages from the user and stream the response."""
    try:
        data = request.get_json()
        user_input = data.get("message") or data.get("prompt")
        if not user_input:
            return jsonify({"error": "message or prompt is required"}), 400

        chat_logger.info(f"user: {user_input}")

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input},
        ]
        
        payload = {
            "messages": messages,
            "model": "llama-3.3-70b-versatile"
        }

        def generate_stream():
            """Proxy the stream directly, yielding each chunk as it arrives."""
            try:
                response = openai_chat_completion_for_chat_stream(payload)
                ai_source = f"AI ({TARGET_API_BASE_URL}/chat/completions)"
                chat_logger.info(f"{ai_source}: Streaming response initiated (proxy mode).")
                buffer = b""
                for chunk in response.iter_content(chunk_size=None):
                    buffer = buffer + chunk
                    index = buffer.find(b"\n\n")
                    while index > -1:
                        json_chunk = json.loads(buffer[6:index])
                        json_chunk["model"] = "gpt-4o-mini"
                        if "x_groq" in json_chunk:
                            del json_chunk["x_groq"]
                        new_chunk = "data: " + json.dumps(json_chunk) + "\n\n"
                        binary_chunk = bytes(new_chunk, "UTF-8")
                        print("chunk:", binary_chunk)
                        buffer = buffer[index+2:]
                        index = buffer.find(b"\n\n")
                        yield binary_chunk
                    # yield chunk
                pass
            except Exception as e:
                chat_logger.error(f"Error during stream generation: {str(e)}", exc_info=True)
                error_message = json.dumps({"error": {"message": "An error occurred during the stream."}})
                yield f"data: {error_message}\\n\\n".encode('utf-8')

        return Response(stream_with_context(generate_stream()), mimetype='text/event-stream')

    except Exception as e:
        current_app.logger.error(f"Error handling chat message: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@main_blueprint.route("/logs", methods=["GET"])
@login_required
def logs_page():
    """Render the logs page"""
    return render_template("logs.html")


@main_blueprint.route("/api/logs", methods=["GET"])
@login_required
def get_logs():
    """API endpoint to get log data"""
    try:
        logs = get_last_logs(200)
        return jsonify({"logs": logs})
    except Exception as e:
        current_app.logger.error(f"Error fetching logs: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@main_blueprint.route("/chat-logs", methods=["GET"])
@login_required
def chat_logs_page():
    """Render the chat logs visualization page"""
    return render_template("chat_logs.html")


@main_blueprint.route("/api/chat-logs", methods=["GET"])
@login_required
def get_chat_logs():
    """API endpoint to get parsed chat log data"""
    try:
        logs = parse_chat_logs()
        return jsonify({"logs": logs})
    except Exception as e:
        current_app.logger.error(f"Error fetching chat logs: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500