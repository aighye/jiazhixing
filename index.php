<?php
require_once __DIR__ . '/bootstrap.php';

if (Auth::check()) {
    header('Location: /dashboard.php');
    exit;
}

header('Location: /login.php');
exit;
