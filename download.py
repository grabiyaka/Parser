import os
import requests

def download_xml_file(xml_url, file_name):
    # Создаем директорию "downloads/", если её нет
    download_dir = 'downloads'
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Формируем полный путь к файлу для сохранения
    file_path = os.path.join(download_dir, file_name)

    try:
        # Отправляем GET-запрос для скачивания файла
        response = requests.get(xml_url)

        # Проверяем успешность запроса
        if response.status_code == 200:
            # Сохраняем содержимое файла
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f'Файл успешно скачан: {file_path}')
        else:
            print(f'Ошибка при скачивании файла. Код ответа: {response.status_code}')
    except Exception as e:
        print(f'Произошла ошибка: {str(e)}')

# Пример использования:
if __name__ == "__main__":
    xml_url = input("Введите ссылку на XML файл: ")
    file_name = input("Введите название файла для сохранения: ")

    download_xml_file(xml_url, file_name)
