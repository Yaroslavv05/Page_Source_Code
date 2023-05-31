import requests
import time

# URL адреса для тестирования
urls = [
    'https://resourceplus.work',
    'https://www.google.com',
    'https://www.github.com',
    'https://www.openai.com',
    'https://www.python.org',
    'https://www.wikipedia.org',
    'https://www.amazon.com',
    'https://www.microsoft.com',
    'https://www.apple.com',
    'https://www.stackoverflow.com'
]

task_ids = []

# Добавление сайтов в массив tasks
for i in range(50):
    for url in urls:
        response = requests.get(f'http://localhost:5000/tasks/create?url={url}')
        if response.status_code == 200:
            task_id = response.json()['id']
            task_ids.append(task_id)
            print(f"Task created with ID: {task_id}")

# Ожидание обработки задач
while True:
    time.sleep(1)
    for task_id in task_ids:
        response = requests.get(f'http://localhost:5000/tasks/getResult?id={task_id}')
        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                print(data['error'])
            elif 'status' in data and data['status'] == 'processing':
                print(f"Task with ID {task_id} is still processing...")
            elif 'result' in data:
                result = data['result']
                print(f"Task with ID {task_id} result:\n{result}")
                task_ids.remove(task_id)
                break

    if not task_ids:
        break
