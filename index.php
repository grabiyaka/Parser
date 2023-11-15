<?php

//index.php on server side

ini_set('file_uploads', 'On');
ini_set('display_errors', 1);
error_reporting(E_ALL);


if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    $validate = [
        'formdekor_data',
        'techno_odis_data',
        'hitbeton_data',
        'semj_data',
        'molli_data',
        'fortechne_data',
        'de_technik_data',
        'raduga_data_1',
        'raduga_data_2'
    ];


    foreach ($validate as $field) {
        if (isset($_FILES[$field])) {
            $file = $_FILES[$field];
            if ($file['error'] === UPLOAD_ERR_OK) {
                $targetDir = 'xml/';

                $fileName = basename($file['name']);
                $targetFilePath = $targetDir . $fileName;
                if (move_uploaded_file($file['tmp_name'], $targetFilePath)) {
                    echo 'XML-файл успешно загружен и сохранен.<br>';
                } else {
                    echo 'Ошибка при сохранении первого XML-файла.<br>';
                }

            }
        }
    }

    if (isset($_POST['success']) && $_POST['success'] == true) {
        $xmlContent = '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
        $xmlContent .= '<yml_catalog date="' . date('Y-m-d H:i') . '">' . "\n";
        $xmlContent .= '    <shop>' . "\n";
        $xmlContent .= '        <name>Products</name>' . "\n";
        $xmlContent .= '        <company></company>' . "\n";
        $xmlContent .= '        <url></url>' . "\n";
        $xmlContent .= '        <platform>Opencart</platform>' . "\n";
        $xmlContent .= '        <version></version>' . "\n";
        $xmlContent .= '        <currencies>' . "\n";
        $xmlContent .= '            <currency id="USD" rate="1"/>' . "\n";
        $xmlContent .= '        </currencies>' . "\n";
        $xmlContent .= '        <categories>' . "\n";
        $xmlContent .= '            <category id="59"> Поліуретанові штампи</category>' . "\n";
        $xmlContent .= '            <category id="60"> Форми для 3d панелей</category>' . "\n";
        $xmlContent .= '        </categories>' . "\n";
        $xmlContent .= '        <offers>' . "\n";

        foreach ($validate as $field) {
            $fileName = "xml/{$field}.xml"; 
            if (file_exists($fileName)) {
                $xmlContent .= file_get_contents($fileName);
            }
        }

        $xmlContent .= '        </offers>' . "\n";
        $xmlContent .= '    </shop>' . "\n";
        $xmlContent .= '</yml_catalog>';

        file_put_contents('xml/parser_data.xml', $xmlContent);

        echo 'success';
    }


} else {
    echo 'Привет!<br>';
}

?>