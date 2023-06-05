from flask import Flask, request, jsonify
from ChromeManager import ChromeManager
from Task import Task, TaskState, TaskContainerObj
import logging
import utils
import argparse
import threading

logger = logging.getLogger()


def main():
    # Waiting for quit...
    pressed = False
    while True:
        if not pressed:
            input("Press Enter to quit...")
            pressed = True
        else:
            if utils.query_yes_no("Want to quit?"):
                logging.info("Shutting down Python Chrome.")
                chrome_manager.quit()
                break
            pressed = False


# region Task Processing

chrome_manager = ChromeManager()
tasks = []


def task_processing():
    while True:
        try:
            # Task processing
            task_co: TaskContainerObj = next((taskContainerObj for taskContainerObj in tasks
                                              if taskContainerObj.taskState == TaskState.New), None)
            if task_co:
                task_co.taskState = TaskState.InProgress
                chrome_manager.get_html_page(task_co.task)  # processing new Task
                task_co.taskState = TaskState.Completed

                # Check if tasks list has 'Requested' Task`s and remove `em
                tasks[:] = [task for task in tasks if task.taskState != TaskState.Requested]
            else:
                if next((taskContainerObj for taskContainerObj in tasks
                         if taskContainerObj.taskState == TaskState.InProgress), None) is None:
                    utils.sleep_with_timeout(1)  # 1 sec sleep if no new Task

        except Exception as e:
            logging.error("Task processing error: ")
            logging.exception(e)


task_processing_thread: threading.Thread = threading.Thread(target=task_processing, daemon=True)

# endregion

# region RESTFul

app = Flask(__name__)


@app.route('/tasks/create', methods=['POST'])
def create_task():
    try:
        data = request.get_data()
        task: Task = Task.from_json(data)
        new_task = TaskContainerObj(task)
        tasks.append(new_task)
        return jsonify({'id': task.ID}), 200
    except Exception as e:
        logging.exception(e)
        return jsonify({'error': str(e)}), 500


@app.route('/tasks/getResult', methods=['GET'])
def get_task_result():
    try:
        task_id = request.args.get('id')
        task: TaskContainerObj = next((taskContainerObj for taskContainerObj in tasks if taskContainerObj.task.ID ==
                                       task_id), None)
        if task:
            if task.taskState == TaskState.Completed:
                result = task.task.Page_Source
                task.taskState = TaskState.Requested
                return jsonify({'result': result}), 200
            elif task.taskState == TaskState.New or task.taskState == TaskState.InProgress:
                return jsonify({'status': 'Task in progress'}), 200
        else:
            return jsonify({'error': 'Task not found'}), 400
    except Exception as e:
        logging.exception(e)
        return jsonify({'error': str(e)}), 500


def web():
    parser = argparse.ArgumentParser(description='define Flask default')
    parser.add_argument('-p', '--port', default=5000)
    args = parser.parse_args()
    flask_port = args.port

    app.run(host='0.0.0.0', port=flask_port, debug=False, use_reloader=False)


flask_thread: threading.Thread = threading.Thread(target=web, daemon=True)

# endregion

if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    logging.info("Python Chrome is run.\n")

    flask_thread.start()  # start RESTFul API
    task_processing_thread.start()  # start Task Processing
    main()
