<?php return [
    'app' => [
        'name' => '汽车4S店维修业务管理系统',
        'version' => '1.0.0',
        'url' => 'http://localhost',
        'timezone' => 'Asia/Shanghai',
    ],
    'database' => [
        'host' => 'localhost',
        'dbname' => 'auto_4s_system',
        'username' => 'root',
        'password' => '',
        'charset' => 'utf8mb4',
    ],
    'session' => [
        'name' => 'AUTO_4S_SESSION',
        'lifetime' => 7200,
    ],
    'upload' => [
        'max_size' => 10485760,
        'allowed_types' => ['jpg', 'jpeg', 'png', 'gif', 'pdf'],
        'path' => __DIR__ . '/../uploads/',
    ]
];