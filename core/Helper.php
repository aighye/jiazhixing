<?php
class Helper {
    public static function json($data, $code = 200) {
        http_response_code($code);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($data, JSON_UNESCAPED_UNICODE);
        exit;
    }

    public static function success($message = '操作成功', $data = []) {
        self::json(['code' => 200, 'message' => $message, 'data' => $data]);
    }

    public static function error($message = '操作失败', $code = 400) {
        self::json(['code' => $code, 'message' => $message]);
    }

    public static function redirect($url) {
        header("Location: {$url}");
        exit;
    }

    public static function back($message = null) {
        if ($message) {
            $_SESSION['flash_message'] = $message;
        }
        header("Location: " . $_SERVER['HTTP_REFERER']);
        exit;
    }

    public static function flash() {
        if (isset($_SESSION['flash_message'])) {
            $message = $_SESSION['flash_message'];
            unset($_SESSION['flash_message']);
            return $message;
        }
        return null;
    }

    public static function pagination($total, $page, $limit) {
        $totalPages = ceil($total / $limit);
        return [
            'total' => $total,
            'page' => $page,
            'limit' => $limit,
            'total_pages' => $totalPages,
            'has_prev' => $page > 1,
            'has_next' => $page < $totalPages
        ];
    }

    public static function formatMoney($amount) {
        return number_format($amount, 2, '.', ',');
    }

    public static function formatDate($date, $format = 'Y-m-d') {
        return date($format, strtotime($date));
    }

    public static function formatDateTime($datetime) {
        return date('Y-m-d H:i:s', strtotime($datetime));
    }

    public static function generateOrderNo($prefix = 'WO') {
        return $prefix . date('YmdHis') . str_pad(mt_rand(1, 9999), 4, '0', STR_PAD_LEFT);
    }

    public static function generatePartsCode() {
        return 'PT' . date('Ymd') . str_pad(mt_rand(1, 9999), 4, '0', STR_PAD_LEFT);
    }

    public static function sanitize($string) {
        return htmlspecialchars(trim($string), ENT_QUOTES, 'UTF-8');
    }

    public static function buildTree($data, $pid = 0, $pidName = 'parent_id') {
        $tree = [];
        foreach ($data as $row) {
            if ($row[$pidName] == $pid) {
                $children = self::buildTree($data, $row['id'], $pidName);
                if ($children) {
                    $row['children'] = $children;
                }
                $tree[] = $row;
            }
        }
        return $tree;
    }

    public static function exportExcel($filename, $headers, $data) {
        header('Content-Type: application/vnd.ms-excel; charset=utf-8');
        header("Content-Disposition: attachment; filename={$filename}.xls");
        header('Pragma: no-cache');
        header('Expires: 0');

        $html = '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40"><head><meta charset="UTF-8"></head><body>';
        $html .= '<table border="1"><tr>';
        foreach ($headers as $header) {
            $html .= '<th>' . $header . '</th>';
        }
        $html .= '</tr>';
        foreach ($data as $row) {
            $html .= '<tr>';
            foreach ($row as $cell) {
                $html .= '<td>' . $cell . '</td>';
            }
            $html .= '</tr>';
        }
        $html .= '</table></body></html>';
        echo $html;
        exit;
    }
}