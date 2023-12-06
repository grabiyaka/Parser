import os
import requests

def download_xml_file(xml_url, file_name):
    download_dir = 'downloads'
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    file_path = os.path.join(download_dir, file_name)

    try:
        response = requests.get(xml_url)

        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f'Файл успешно скачан: {file_path}')
        else:
            print(f'Ошибка при скачивании файла. Код ответа: {response.status_code}')
    except Exception as e:
        print(f'Произошла ошибка: {str(e)}')

if __name__ == "__main__":
    xml_url = 'http://elijah.kiev.ua/Parser/xml/drp.xml'
    file_name = 'drp'

    download_xml_file(xml_url, file_name)
