<?php
session_start();

$api_url = getenv('AEGIS_BACKEND_URL') ?: 'http://127.0.0.1:8000';
$error_msg = '';

// Handle PHP Login Form Submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'login') {
    $username = trim($_POST['username'] ?? '');
    $password = trim($_POST['password'] ?? '');

    if (!empty($username) && !empty($password)) {
        $ch = curl_init($api_url . '/api/v1/auth/login');
        $payload = json_encode(['username' => $username, 'password' => $password]);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
        curl_setopt($ch, CURLOPT_TIMEOUT, 5);

        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($http_code === 200) {
            $data = json_decode($response, true);
            $_SESSION['access_token'] = $data['access_token'];
            $_SESSION['user_role']    = $data['role'];
            $_SESSION['username']     = $data['username'];
            header("Location: index.php");
            exit;
        } else {
            $data = json_decode($response, true);
            $error_msg = is_array($data) && isset($data['detail']) ? 
                (is_array($data['detail']) ? ($data['detail']['detail'] ?? 'Invalid credentials') : $data['detail']) : 
                'Authentication failed.';
        }
    } else {
        $error_msg = 'Please provide both username and password.';
    }
}

// Handle PHP Logout
if (isset($_GET['action']) && $_GET['action'] === 'logout') {
    session_destroy();
    header("Location: index.php");
    exit;
}

$is_authenticated = !empty($_SESSION['access_token']);
$logged_user      = $_SESSION['username'] ?? '';
$logged_role      = $_SESSION['user_role'] ?? '';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AEGIS-TRAFFIC // PHP Operations Portal</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Orbitron:wght@600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        :root {
            --bg-dark: #020617;
            --panel-bg: rgba(13, 17, 23, 0.9);
            --panel-border: rgba(0, 240, 255, 0.2);
            --cyan: #00f0ff;
            --purple: #a855f7;
            --emerald: #10b981;
            --amber: #f59e0b;
            --rose: #ef4444;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            background-image: radial-gradient(circle at 10% 10%, rgba(0, 240, 255, 0.05) 0%, transparent 40%);
        }

        header {
            display: flex; justify-content: space-between; align-items: center;
            padding: 14px 28px; background: rgba(2, 6, 23, 0.95);
            border-bottom: 1px solid var(--panel-border); backdrop-filter: blur(12px);
        }

        .logo-title {
            font-family: 'Orbitron', sans-serif; font-size: 1.3rem; font-weight: 800;
            color: var(--cyan); letter-spacing: 3px; display: flex; align-items: center; gap: 10px;
        }

        .status-badge {
            font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; padding: 5px 12px;
            border-radius: 20px; background: rgba(16, 185, 129, 0.1); border: 1px solid var(--emerald); color: var(--emerald);
            display: flex; align-items: center; gap: 8px;
        }

        .pulse-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--emerald); box-shadow: 0 0 10px var(--emerald); }

        .auth-card {
            background: var(--panel-bg); border: 1px solid var(--panel-border);
            border-radius: 12px; padding: 30px; max-width: 420px; margin: 80px auto;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5); backdrop-filter: blur(12px);
        }

        input[type="text"], input[type="password"] {
            width: 100%; background: rgba(15, 23, 42, 0.8); border: 1px solid var(--panel-border);
            color: #fff; padding: 10px 14px; border-radius: 6px; font-family: 'JetBrains Mono'; font-size: 0.85rem;
            margin-bottom: 12px; outline: none;
        }

        button.btn-primary {
            background: linear-gradient(135deg, #00f0ff, #0088ff); color: #000;
            font-family: 'Orbitron'; font-weight: 700; font-size: 0.75rem; padding: 10px 18px;
            border: none; border-radius: 6px; cursor: pointer; width: 100%;
        }

        .seed-btn {
            font-size: 0.7rem; font-family: 'JetBrains Mono'; padding: 4px 8px;
            border-radius: 4px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
            color: var(--text-muted); cursor: pointer; margin-right: 4px;
        }
    </style>
</head>
<body>

    <header>
        <div class="logo-title"><span>🚦</span> AEGIS-TRAFFIC // PHP ENGINE</div>
        <div class="status-badge"><div class="pulse-dot"></div><span>NODE ACTIVE // VERIFIED ZERO-TRUST</span></div>
    </header>

    <?php if (!$is_authenticated): ?>
        <!-- PHP AUTHENTICATION FORM -->
        <div class="auth-card">
            <h2 style="font-family:'Orbitron';font-size:1.3rem;margin-bottom:6px;color:var(--cyan);">PHP OPERATOR LOGIN</h2>
            <p style="font-family:'JetBrains Mono';font-size:0.75rem;color:var(--text-muted);margin-bottom:20px;">Session Authentication against FastAPI Engine</p>

            <?php if (!empty($error_msg)): ?>
                <div style="background:rgba(239,68,68,0.15);border:1px solid var(--rose);color:var(--rose);padding:10px;border-radius:6px;font-size:0.78rem;margin-bottom:14px;">
                    ⚠️ <?php echo htmlspecialchars($error_msg); ?>
                </div>
            <?php endif; ?>

            <form method="POST" action="index.php">
                <input type="hidden" name="action" value="login">
                <label style="font-family:'JetBrains Mono';font-size:0.7rem;color:var(--text-muted);">USERNAME</label>
                <input type="text" id="php_user" name="username" placeholder="e.g. admin" required>

                <label style="font-family:'JetBrains Mono';font-size:0.7rem;color:var(--text-muted);">PASSWORD</label>
                <input type="password" id="php_pass" name="password" placeholder="••••••••" required>

                <button type="submit" class="btn-primary">🔐 CONNECT SESSION</button>
            </form>

            <div style="margin-top:16px;padding-top:14px;border-top:1px solid rgba(255,255,255,0.1);text-align:center;">
                <span class="seed-btn" onclick="document.getElementById('php_user').value='admin';document.getElementById('php_pass').value='Admin@AEGIS2024!';">🔑 Admin</span>
                <span class="seed-btn" onclick="document.getElementById('php_user').value='operator';document.getElementById('php_pass').value='Operator@AEGIS2024!';">🔑 Operator</span>
                <span class="seed-btn" onclick="document.getElementById('php_user').value='auditor';document.getElementById('php_pass').value='Auditor@AEGIS2024!';">🔑 Auditor</span>
            </div>
        </div>
    <?php else: ?>
        <!-- AUTHENTICATED PHP DASHBOARD -->
        <div style="padding:24px 28px;max-width:1600px;margin:0 auto;">
            <div style="display:flex;justify-content:space-between;align-items:center;background:rgba(15,23,42,0.8);padding:14px 20px;border-radius:8px;border:1px solid var(--panel-border);margin-bottom:20px;">
                <div style="font-family:'Orbitron';font-size:0.9rem;color:var(--cyan);">
                    👤 WELCOME OPERATOR: <strong><?php echo htmlspecialchars($logged_user); ?></strong> (<?php echo htmlspecialchars($logged_role); ?> CLEARANCE)
                </div>
                <a href="index.php?action=logout" style="color:var(--rose);font-family:'JetBrains Mono';font-size:0.8rem;text-decoration:none;font-weight:700;">🔓 LOGOUT SESSION</a>
            </div>

            <!-- EMBEDDED COMPLETE DASHBOARD UI -->
            <iframe src="index.html" style="width:100%;height:800px;border:none;border-radius:12px;"></iframe>
        </div>
    <?php endif; ?>

</body>
</html>
