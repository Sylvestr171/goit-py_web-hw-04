"Модуля 4. Д/з Веб застосунок"

from pathlib import Path
from logging import info, basicConfig, DEBUG
from threading import Thread
from datetime import datetime
from flask import Flask, render_template, send_from_directory, request, redirect, jsonify
import requests
from time import sleep


basicConfig(level=DEBUG, format="%(asctime)s %(threadName)s %(message)s")
DATA_FILE = Path("front-init/storage/data.json")
last_message = {}


app = Flask(__name__, static_folder="front-init", template_folder="front-init")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/message.html")
def message():
    return render_template("message.html")

@app.route("/<path:filename>")
def static_files(filename):
    file_path = Path("front-init") / filename
    if file_path.exists():
        return send_from_directory("front-init", filename)
    else:
        return render_template("error.html"), 404

@app.route("/message", methods=["POST"])
def message_post():
    global last_message
    data_dict = request.form.to_dict()
    message_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    data_dict_with_time = {message_time: data_dict}
    info("Message: %s", data_dict_with_time)

    last_message = data_dict_with_time

    return redirect("/")

@app.route("/api/data")
def api_data():
    return jsonify(last_message)


def save_to_file(
    data_for_save: str, path_to_save: str = "./front-init/storage/data.json"
):
    """Функція запису даних в файл"""

    file_for_saving = Path(path_to_save)
    with open(file_for_saving, "a", encoding="utf-8") as f:
        f.write(data_for_save + "\n")
        f.close()
    info("Save data: %s to file", data_for_save)


def reception_data():
    previous_data = {}
    while True:
        try:
            response = requests.get("http://127.0.0.1:3000/api/data")
            if response.status_code == 200:
                data = response.json()
                info("Прийнято з API: %s", data)
                if data == previous_data:
                    info("Дані НЕ ЗМІНИЛИСЬ")
                    save_to_file(data)
                    sleep(5)
                    continue
                else:
                    info("ЗАПИС ДО ФАЙЛУ")
                    previous_data = data
            else:
                info("Статус прийому: %s", response.status_code)
        except requests.exceptions.RequestException as e:
            info("Помилка прийому: %s", e)
        sleep(5) 


if __name__ == "__main__":
    reception_thread = Thread(target=reception_data, daemon=True, name="ReceptionThread")
    reception_thread.start()
    app.run(port=3000, debug=True, use_reloader=False)
