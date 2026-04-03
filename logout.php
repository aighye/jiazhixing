<?php
require_once __DIR__ . '/bootstrap.php';

Auth::require();
Logger::log('退出', '用户退出系统', 'auth');
Auth::logout();
Helper::redirect('/login.php');
