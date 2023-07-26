import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime


def getFormdekorData():
    categories = [
        'poliuretanovye-shtampy',
        'formy-dlya-3d-panelej',
        'dekorativnij-kamin',
        'formy-dlya-3d-blokov',
        'formy-dlya-dekora',
        'formy-dlya-sadovyh-figur',
        'master-shtampy'
    ]
    products = []

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0',
        'referer': 'https://formdekor.com/',
        'accept-encoding': 'gzip, deflate, br',
        'cookie': 'OCSESSID=077481e943b5ef1531aeda1f01; _ga=GA1.1.1198526705.1687263981; language=ru-ru; currency=USD; sorecentproduct=109%2C149%2C115%2C162%2C50%2C118%2C177; _ga_BRFVKH6K7T=GS1.1.1690027036.31.0.1690027036.0.0.0',
        'Host': 'formdekor.com'
    }

    session = requests.Session()
    session.headers.update(headers)

    for category in categories:
        url = 'https://formdekor.com/' + category + '/'
        response = session.get(url)

        if response.status_code == 200:
            paginate = response.text
            soup = BeautifulSoup(paginate, 'html.parser')
            paginate_element = soup.select_one('.pagination')
            if(paginate_element):
                paginate_text = paginate_element.get_text()
            else:
                paginate_text = ['1']
            pages = [page for page in paginate_text if page not in '|<>']

            for page in pages:
                url = 'https://formdekor.com/' + category + '/' + '?page=' + page
                response = session.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    productsList = soup.select(
                        '.products-category .products-list .product-layout')

                    for product in productsList:
                        product_data = {}
                        pqProduct = BeautifulSoup(str(product), 'html.parser')
                        product_data['url'] = pqProduct.find('a')['href']
                        product_data['price'] = pqProduct.select_one(
                            '.price-new').get_text().replace('$', '').strip()

                        nameDiv = pqProduct.select_one('h4 a')
                        product_data['name'] = nameDiv.get_text().replace(
                            '&', '&quot;').strip()
                        product_data['category'] = category

                        productPageUrl = product_data['url']
                        response = session.get(productPageUrl.strip())
                        print('formdekor: ' + category + product_data['name'] + ' done')
                        if response.status_code == 200:
                            productPage = response.text
                            pqProductPage = BeautifulSoup(
                                productPage, 'html.parser')
                            product_data['brand'] = pqProductPage.select_one(
                                '.brand a span').get_text().strip()

                            modelDiv = pqProductPage.select_one('.model')
                            product_data['model'] = modelDiv.get_text().strip()

                            product_data['material'] = pqProductPage.select_one(
                                '.propery-title').get_text().strip() if pqProductPage.select_one('.propery-title') else ''

                            product_data['description'] = pqProductPage.select_one(
                                '#collapse-description').get_text().strip()

                            keyWords = [kw.get_text().strip()
                                        for kw in pqProductPage.select('#tab-tags a')]
                            product_data['key_words'] = keyWords

                            images = [img['data-image']
                                      for img in pqProductPage.select('.image-additional a')]
                            product_data['images'] = images

                            address_element = pqProductPage.select_one(
                                '.adres')
                            if address_element:
                                product_data['address'] = address_element.get_text(
                                ).strip()
                            else:
                                product_data['address'] = ''

                        products.append(product_data)

    print(products)

    return products


def generate_xml_f(products):
    output = '<?xml version="1.0" encoding="UTF-8"?>\n' \
             '<yml_catalog date="' + datetime.now().strftime('%Y-%m-%d %H:%M') + '">\n' \
             '    <shop>\n' \
             '        <name>ПУ формы и штампы</name>\n' \
             '        <company>ФОРМДЕКОР-UA</company>\n' \
             '        <url>https://formdekor.com/</url>\n' \
             '        <platform>Opencart</platform>\n' \
             '        <version>3.0.3.8/1.2.1</version>\n' \
             '        <currencies>\n' \
             '            <currency id="USD" rate="1"/>\n' \
             '        </currencies>\n' \
             '        <categories>\n' \
             '            <category id="59"> Поліуретанові штампи</category>\n' \
             '            <category id="60"> Форми для 3d панелей</category>\n' \
             '        </categories>\n' \
             '        <offers>'

    for index, product in enumerate(products):
        output += '<offer id="' + str(index + 1) + '" available="true">\n' \
                  '        <url>' + product['url'] + '</url>\n' \
                  '        <price>' + product['price'] + '</price>\n' \
                  '        <currencyId>USD</currencyId>\n' \
                  '        <categoryId></categoryId>\n' \
                  '        <quantity_in_stock></quantity_in_stock>\n' \
                  '        <name>' + product['name'] + '</name>\n' \
                  '        <vendor>' + product['brand'] + '</vendor>\n' \
                  '        <vendorCode>' + product['model'] + '</vendorCode>\n' \
                  '        <description><![CDATA[' + product['description'] + ']]></description>\n' \
                  '        <keywords>'
        for key, word in enumerate(product['key_words']):
            if word != product['key_words'][-1]:
                output += word + ', <br/>'
            else:
                output += word
        output += '</keywords>\n' \
                  '        <country>Украина</country>\n' \
                  '        <param name="Матеріал">' + product['material'] + '</param>\n' \
                  '        <param name="Бренд">' + \
            product['brand'] + '</param>\n'

        for image in product['images']:
            output += '<picture>' + image + '</picture>'
        output += '</offer>'

    output += '\n' \
              '                </offers>\n' \
              '            </shop>\n' \
              '        </yml_catalog>'
    return output


def save_to_xml(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(data)


def getTechnoOdisData():
    categories = [
        'carpet-stones',
        'antichnyi-kamen',
        '400h400',
        'staryi-gorod',
        'bazalt',
        'staryi-arbat',
        'landshaftnaia',
        'manezh',
        'parket-taverna',
        '300h300',
        'oblitsovka-dekor',
        '320h320',
        'bordiur'
    ]
    products = []
    i = 0

    for category in categories:
        url = 'https://techno-odis.com/catalogue/category/' + category
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            productsList = soup.select('#items-catalog-main .globalFrameProduct')

        for product in productsList:
            product_data = {}
            pqProduct = BeautifulSoup(str(product), 'html.parser')
            product_title = pqProduct.find('.frame-photo-title')
            product_data['url'] = pqProduct.find('a')['href']
            product_data['name'] = product_title['title'] if product_title else ''
            productPageUrl = product_data['url']
            response = requests.get(productPageUrl)

            if response.status_code == 200:
                print('techno-odis: ' + category + product_data['name'] + ' done')
                pqProductPage = BeautifulSoup(response.text, 'html.parser')
                product_data['price'] = pqProductPage.select_one('.priceVariant').text.strip()

                brand_element = pqProductPage.select_one('.brand a span')
                product_data['brand'] = brand_element.get_text().strip() if brand_element else ''

                modelDiv = pqProductPage.select_one('.js-code')
                product_data['model'] = modelDiv.get_text().strip() if modelDiv else ''

                material_element = pqProductPage.select_one('.propery-title')
                product_data['material'] = material_element.get_text().strip() if material_element else ''

                description_element = pqProductPage.select_one('.short-desc')
                product_data['description'] = description_element.get_text().strip() if description_element else ''

                keyWords = [kw.get_text().strip() for kw in pqProductPage.select('#tab-tags a')]
                product_data['key_words'] = keyWords

                images = [img['src'] for img in pqProductPage.select('.items-thumbs .photo-block img')]
                images = list(set(images))
                product_data['images'] = images

                address_element = pqProductPage.select_one('.adres')
                product_data['address'] = address_element.get_text().strip() if address_element else ''

                stockDiv = pqProductPage.select_one('.stock')
                product_data['stock'] = stockDiv.get_text().strip().replace('"', '').replace(' ', '') if stockDiv else ''

                products.append(product_data)

    return products


def generate_xml_t(products):
    output = '<?xml version="1.0" encoding="UTF-8"?>\n' \
             '<yml_catalog date="' + datetime.now().strftime('%Y-%m-%d %H:%M') + '">\n' \
             '    <shop>\n' \
             '        <name>ПУ формы и штампы</name>\n' \
             '        <company>ФОРМДЕКОР-UA</company>\n' \
             '        <url>https://formdekor.com/</url>\n' \
             '        <platform>Opencart</platform>\n' \
             '        <version>3.0.3.8/1.2.1</version>\n' \
             '        <currencies>\n' \
             '            <currency id="USD" rate="1"/>\n' \
             '        </currencies>\n' \
             '        <categories>\n' \
             '            <category id="59"> Поліуретанові штампи</category>\n' \
             '            <category id="60"> Форми для 3d панелей</category>\n' \
             '        </categories>\n' \
             '        <offers>'

    for index, product in enumerate(products):
        output += '<offer id="' + str(index + 1) + '" available="true">\n' \
                  '        <url>' + product['url'] + '</url>\n' \
                  '        <price>' + product['price'] + '</price>\n' \
                  '        <currencyId>USD</currencyId>\n' \
                  '        <categoryId></categoryId>\n' \
                  '        <quantity_in_stock></quantity_in_stock>\n' \
                  '        <name>' + product['name'] + '</name>\n' \
                  '        <vendor>' + 'techno-odis' + '</vendor>\n' \
                  '        <vendorCode>' + product['model'] + '</vendorCode>\n' \
                  '        <description><![CDATA[' + product['description'] + ']]></description>\n' \
                  '        <keywords>'
        for key, word in enumerate(product['key_words']):
            if word != product['key_words'][-1]:
                output += word + ', <br/>'
            else:
                output += word
        output += '</keywords>\n' \
                  '        <country>Украина</country>\n' \
                  '        <param name="Матеріал">' + product['material'] + '</param>\n' \
                  '        <param name="Бренд">' + \
            product['brand'] + '</param>\n'

        for image in product['images']:
            output += '<picture>https://techno-odis.com/' + image + '</picture>'
        output += '</offer>'

    output += '\n' \
              '                </offers>\n' \
              '            </shop>\n' \
              '        </yml_catalog>'
    return output


def save_to_xml(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(data)


# Пример использования
# products = getTechnoOdisData()
# xml_data = generate_xml_t(products)
# file_path = 'techno-odis.xml'  # Укажите путь к файлу, куда хотите сохранить XML данные
# save_to_xml(xml_data, file_path)
# print(f'Данные успешно сохранены в файл: {file_path}')

# Пример использования
# products = getFormdekorData()
# xml_data = generate_xml_f(products)
# file_path = 'output.xml'  # Укажите путь к файлу, куда хотите сохранить XML данные
# save_to_xml(xml_data, file_path)
# print(f'Данные успешно сохранены в файл: {file_path}')

def send_xml_to_server(xml_data1, xml_data2, filename1, filename2):
    url = 'https://parser-for-grabiyaka.000webhostapp.com'  # Замените на адрес вашего сервера

    headers = {
        'Content-Type': 'application/xml',  # Указываем тип данных - XML
    }

    # Преобразуем данные в формат XML
    xml_str1 = xml_data1
    xml_str2 = xml_data2

    # Отправляем POST-запрос с данными XML1 на сервер
    files = {'formdekor': (filename1, xml_str1.encode('utf-8'))}
    response1 = requests.post(url, files=files)

    # Отправляем POST-запрос с данными XML2 на сервер
    files = {'techno-odis': (filename2, xml_str2.encode('utf-8'))}
    response2 = requests.post(url, files=files)

    # Проверяем статусы ответов
    if response1.status_code == 200 and response2.status_code == 200:
        print("Оба XML успешно отправлены на сервер!")

        # Выводим содержимое ответа сервера
        print("Ответ сервера на XML1:")
        print(response1.text)

        print("Ответ сервера на XML2:")
        print(response2.text)
    else:
        print("Ошибка при отправке XML на сервер.")

# Ваши XML коды, которые нужно отправить на сервер
xml_data1 = generate_xml_f(getFormdekorData())

xml_data2 = generate_xml_t(getTechnoOdisData())


# Имена файлов для отправки на сервер
filename1 = 'formdekor.xml'
filename2 = 'techno-odis.xml'

# Отправка данных на сервер с указанными именами файлов
send_xml_to_server(xml_data1, xml_data2, filename1, filename2)

input("Нажмите любую клавишу для выхода...")


