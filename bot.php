<?php

// === BOT AYARLARI ===
$botToken = "BOT_TOKENİNİ_BURAYA_EKLE"; 
$apiURL = "https://api.telegram.org/bot$botToken/";

// === ZORUNLU KANALLAR ===
$channel1 = "@invest_usdt_robot";
$channel2 = "@invest_usdt_bot_chat";

// === ADMIN AYARLARI ===
$adminID = 123456789; // Admin Telegram ID (kendininkini ekle)

// === USDT CÜZDANI ===
$walletAddress = "UQAK_r8-L9S5b4pY6pmh9TCVQMwenNGF0I3zszrRYKhz6K2u";

// === TELEGRAM MESAJINI OKU ===
$update = json_decode(file_get_contents("php://input"), true);
$message = $update['message'] ?? null;
$chatID = $message['chat']['id'] ?? null;
$text = $message['text'] ?? "";

// === ABONELİK KONTROLÜ ===
function checkSubscription($userID, $channel) {
    global $apiURL;
    $response = file_get_contents($apiURL . "getChatMember?chat_id=$channel&user_id=$userID");
    $data = json_decode($response, true);
    return isset($data['result']['status']) && in_array($data['result']['status'], ['member', 'administrator', 'creator']);
}

// === KOMUTLARI YÖNET ===
if ($text == "/start") {
    if (!checkSubscription($chatID, $channel1) || !checkSubscription($chatID, $channel2)) {
        sendMessage($chatID, "📌 Botu kullanabilmek için şu kanallara üye olmalısın: \n\n1️⃣ $channel1\n2️⃣ $channel2\n\nÜye olduktan sonra tekrar /start yaz.");
    } else {
        sendMessage($chatID, "🎉 Hoş geldin! USDT yatırım yapmak için /invest yaz.");
    }
}

elseif ($text == "/invest") {
    sendMessage($chatID, "💰 Minimum yatırım: 10 USDT\n📥 USDT Cüzdanı: `$walletAddress`\n\nYatırım yaptıktan sonra /confirm yaz.");
}

elseif ($text == "/confirm") {
    sendMessage($chatID, "📩 Ödeme işleminizi admin kontrol edecek. Lütfen TX ID'nizi gönderin.");
    sendMessage($adminID, "📩 Yeni yatırım talebi var! Kullanıcı: @$chatID");
}

// === MESAJ GÖNDERME FONKSİYONU ===
function sendMessage($chatID, $text) {
    global $apiURL;
    file_get_contents($apiURL . "sendMessage?chat_id=$chatID&text=" . urlencode($text) . "&parse_mode=Markdown");
}

?>

