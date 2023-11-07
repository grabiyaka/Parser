<?php
// Убедитесь, что загрузка файлов разрешена в настройках PHP
ini_set('file_uploads', 'On');
ini_set('display_errors', 1);
error_reporting(E_ALL);


// Обработка загруженных файлов
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    
   
   if(isset($_FILES['parser_data'])){
        $file1 = $_FILES['parser_data'];
        // Проверяем наличие ошибок при загрузке файлов
        if ($file1['error'] === UPLOAD_ERR_OK) {
            $targetDir = 'xml/'; 
    
            $fileName1 = basename($file1['name']);
            $targetFilePath1 = $targetDir . $fileName1;
            if (move_uploaded_file($file1['tmp_name'], $targetFilePath1)) {
                echo 'XML-файл успешно загружен и сохранен.<br>';
            } else {
                echo 'Ошибка при сохранении первого XML-файла.<br>';
            }
            
        }
    } else{
        echo "no file parser_data(";
    }
   
    
} else {
    echo 'Ошибка загрузки XML-файлов.<br>';
}

?>
