import os
import requests

def download_xml_file(xml_url, file_name):
    download_dir = 'downloads'
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    file_path = os.path.join(download_dir, file_name)

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 OPR/102.0.0.0',
        }
        response = requests.get(xml_url, headers=headers)

        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f'Файл успешно скачан: {file_path}')
        else:
            print(f'Ошибка при скачивании файла. Код ответа: {response.status_code}')
    except Exception as e:
        print(f'Произошла ошибка: {str(e)}')

if __name__ == "__main__":
    xml_url = 'https://kukuruzabox.com.ua/products_feed.xml?hash_tag=58ee6724781917b0cf6d043572013925&sales_notes=&product_ids=&label_ids=&exclude_fields=description&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk&group_ids=2323313%2C2509099%2C22798006%2C85080759%2C98570328&nested_group_ids=2323313%2C2509099%2C22798006%2C85080759%2C98570328&extra_fields='
    file_name = 'kuku.xml'

    download_xml_file(xml_url, file_name)
