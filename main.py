from flask import Flask, request, jsonify
from undetected_chromedriver import Chrome
from threading import Thread
import time
import uuid

app = Flask(__name__)
tasks = []
MAX_TASKS = 10


def browser_manager():
    while True:
        time.sleep(1)

        for task in tasks:
            if not task['IsReady']:
                driver = Chrome()
                driver.get(task['url'])
                time.sleep(7)
                page_html = driver.page_source
                task['IsReady'] = True
                task['result'] = page_html
                driver.quit()


def get_next_task():
    for task in tasks:
        if not task['IsRequested']:
            task['IsRequested'] = True
            return task['url']
    return None


def task_manager():
    while True:
        time.sleep(1)

        # Получение готовых задач
        ready_tasks = [task for task in tasks if task['IsRequested'] and task['IsReady']]

        # Удаление готовых задач, если их количество превышает MAX_TASKS
        if len(ready_tasks) > MAX_TASKS:
            tasks[:] = [task for task in tasks if not (task['IsRequested'] and task['IsReady'])]

        # Добавление новых задач
        while len(tasks) < MAX_TASKS:
            new_task = get_next_task()  # Получение следующей задачи
            if new_task:
                task_id = str(uuid.uuid4())
                task = {
                    'id': task_id,
                    'url': new_task,
                    'IsRequested': True,
                    'IsReady': False
                }
                tasks.append(task)
            else:
                break


@app.route('/tasks/create', methods=['GET'])
def create_task():
    url = request.args.get('url')
    task_id = str(uuid.uuid4())
    task = {
        'id': task_id,
        'url': url,
        'IsRequested': True,
        'IsReady': False
    }
    tasks.append(task)

    return jsonify({'id': task_id}), 200


@app.route('/tasks/getResult', methods=['GET'])
def get_task_result():
    task_id = request.args.get('id')
    task = next((task for task in tasks if task['id'] == task_id), None)
    if task:
        if task['IsReady']:
            result = task['result']
            return jsonify({'result': result}), 200
        else:
            return jsonify({'status': 'processing'}), 200
    else:
        return jsonify({'error': 'Task not found'}), 404


def start_threads():
    browser_thread = Thread(target=browser_manager)
    task_thread = Thread(target=task_manager)
    browser_thread.start()
    task_thread.start()


if __name__ == '__main__':
    start_threads()
    app.run()
