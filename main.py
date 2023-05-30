from flask import Flask, request, jsonify
from undetected_chromedriver import Chrome
import time
import uuid

app = Flask(__name__)
tasks = {}


@app.route('/tasks/create', methods=['GET'])
def create_task():
    url = request.args.get('url')
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'url': url, 'status': 'processing'}
    try:
        driver = Chrome()
        driver.get(url)
        time.sleep(10)
        page_html = driver.page_source
        tasks[task_id]['status'] = 'completed'
        tasks[task_id]['result'] = page_html
        driver.quit()
    except Exception as ex:
        tasks[task_id]['status'] = 'error'
        tasks[task_id]['error_message'] = str(ex)

    return jsonify({'id': task_id}), 200


@app.route('/tasks/getResult', methods=['GET'])
def get_task_result():
    task_id = request.args.get('id')
    if task_id in tasks:
        status = tasks[task_id]['status']
        if status == 'completed':
            result = tasks[task_id]['result']
            return jsonify({'result': result}), 200
        elif status == 'processing':
            return jsonify({'status': status}), 200
        else:
            error_message = tasks[task_id]['error_message']
            return jsonify({'status': status, 'error_message': error_message}), 200
    else:
        return jsonify({'error': 'Task not found'}), 404


if __name__ == '__main__':
    app.run()
