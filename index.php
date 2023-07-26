<?php
require __DIR__ . '/functions.php';
require __DIR__ . '/phpQuery-onefile.php';
require __DIR__ . '/parsers/techno-odis.php';
require __DIR__ . '/parsers/formdekor.php';

$formdekorData = getFormdekorData();
file_put_contents('xml/formdekor.xml', $formdekorData);
$technoOdisData = getTechnoOdisData();
file_put_contents('xml/techno-odis.xml', $technoOdisData);

$url = 'https://parser-for-grabiyaka.000webhostapp.com';

$file1Path = 'xml/formdekor.xml';
$file2Path = 'xml/techno-odis.xml';

$data = array(
    'formdekor' => new CURLFile($file1Path),
    'techno-odis' => new CURLFile($file2Path)
);

$curl = curl_init();

curl_setopt($curl, CURLOPT_URL, $url);
curl_setopt($curl, CURLOPT_POST, true);
curl_setopt($curl, CURLOPT_POSTFIELDS, $data);
curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

$result = curl_exec($curl);

curl_close($curl);

if ($result !== false) {
    echo $result;
} else {
    echo 'Ошибка при выполнении запроса.';
}

?>