<?php
require_once __DIR__ . '/core/Config.php';
require_once __DIR__ . '/core/Database.php';
require_once __DIR__ . '/core/Auth.php';
require_once __DIR__ . '/core/Logger.php';
require_once __DIR__ . '/core/Helper.php';

Config::load(__DIR__ . '/config/app.php');

error_reporting(E_ALL);
ini_set('display_errors', 1);

date_default_timezone_set(Config::get('app.timezone'));
