<?php

// URL-адрес, на который будет отправлен POST-запрос
$url = 'https://parser-for-grabiyaka.000webhostapp.com';

// Пути к файлам на локальной машине
$file1Path = 'xml/formdekor.xml';
$file2Path = 'xml/techno-odis.xml';

// Формируем данные для отправки
$data = array(
    'formdekor' => new CURLFile($file1Path),
    'techno-odis' => new CURLFile($file2Path)
);

// Инициализация cURL
$curl = curl_init();

// Установка опций cURL для POST-запроса
curl_setopt($curl, CURLOPT_URL, $url);
curl_setopt($curl, CURLOPT_POST, true);
curl_setopt($curl, CURLOPT_POSTFIELDS, $data);
curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

// Выполнение запроса
$result = curl_exec($curl);

// Закрытие cURL-соединения
curl_close($curl);

// Обработка ответа
if ($result !== false) {
    echo $result;
} else {
    echo 'Ошибка при выполнении запроса.';
}

?>
