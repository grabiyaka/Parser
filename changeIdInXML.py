import xml.etree.ElementTree as ET

def update_xml_ids(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Начальное значение уникального номера
        unique_number = 1

        # Найти все теги <offer> и обновить их атрибуты id
        for offer in root.findall(".//offer"):
            # Получить текущее значение атрибута id
            current_id = offer.get("id")
            
            # Обновить атрибут id с учетом уникального номера
            offer.set("id", f"{current_id}_{unique_number}")

            # Увеличить уникальный номер на 1
            unique_number += 1

        # Сохранить обновленный XML в новый файл
        updated_xml_file = xml_file
        tree.write(updated_xml_file)

        print(f"Успешно обновлен XML и сохранен в {updated_xml_file}")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

# Укажите путь к вашему XML-файлу
xml_file_path = "xml/ExportProducts_Prom.xml"
update_xml_ids(xml_file_path)
