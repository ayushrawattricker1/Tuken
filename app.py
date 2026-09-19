import os
import re
import json
import hashlib
import requests as req
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# ============================================================
# HTML TEMPLATE – Full Merged Panel UI
# ============================================================
HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>FB Token Extractor • 2026</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300..800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;min-height:100vh;background:#07070d;display:flex;justify-content:center;align-items:center;
background-image:radial-gradient(ellipse at 20% 50%,rgba(24,119,242,0.05) 0%,transparent 60%),radial-gradient(ellipse at 80% 20%,rgba(156,39,176,0.05) 0%,transparent 60%);padding:20px}
.panel{background:#0e0e16;border:1px solid rgba(255,255,255,0.04);border-radius:20px;padding:36px;max-width:520px;width:100%;box-shadow:0 30px 80px rgba(0,0,0,0.7)}
.logo{display:flex;align-items:center;gap:12px;margin-bottom:28px}
.logo-icon{width:40px;height:40px;background:linear-gradient(135deg,#1877F2,#9C27B0);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:18px;color:#fff;font-weight:800}
.logo-text h1{font-size:19px;font-weight:700;color:#e4e4f0;letter-spacing:-0.3px}
.logo-text p{font-size:11px;color:#5a5a70;font-weight:400}
.grp{margin-bottom:16px}
label{display:block;font-size:12px;font-weight:500;color:#9090a8;margin-bottom:5px}
input{width:100%;padding:13px 15px;background:#16161f;border:1px solid #242430;border-radius:10px;color:#e4e4f0;font-size:14px;font-family:'Inter',sans-serif;transition:border .2s;outline:none}
input:focus{border-color:#1877F2;box-shadow:0 0 0 3px rgba(24,119,242,.12)}
input::placeholder{color:#3a3a4a}
.btn{width:100%;padding:13px;background:linear-gradient(135deg,#1877F2,#9C27B0);border:none;border-radius:10px;color:#fff;font-size:14px;font-weight:600;cursor:pointer;transition:transform .2s,box-shadow .2s;font-family:'Inter',sans-serif}
.btn:hover{transform:translateY(-1px);box-shadow:0 8px 30px rgba(24,119,242,.25)}
.btn:disabled{opacity:.5;cursor:not-allowed;transform:none}
.st-box{margin-top:16px;padding:14px;border-radius:10px;font-size:13px;line-height:1.5;display:none}
.st-box.loading{display:block;background:#161622;border:1px solid #262632;color:#9090a8}
.st-box.success{display:block;background:#0b2618;border:1px solid #156635;color:#5fdf9f}
.st-box.error{display:block;background:#260b0b;border:1px solid #661515;color:#ff6f6f}
.tk-box{margin-top:14px;padding:12px;background:#0b0b14;border:1px solid #1a1a28;border-radius:10px;display:none;word-break:break-all}
.tk-box.show{display:block}
.tk-label{font-size:10px;font-weight:600;color:#5a5a70;text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px}
.tk-val{font-size:11px;color:#b0b0c8;font-family:'Courier New',monospace;line-height:1.5}
.cp-btn{margin-top:6px;padding:7px 14px;background:transparent;border:1px solid #242430;border-radius:7px;color:#9090a8;font-size:11px;cursor:pointer;transition:all .2s;font-family:'Inter',sans-serif}
.cp-btn:hover{background:#161622;border-color:#1877F2;color:#1877F2}
.hide{display:none}
.spin{display:inline-block;width:14px;height:14px;border:2px solid rgba(255,255,255,.1);border-top-color:#1877F2;border-radius:50%;animation:spin .8s linear infinite;vertical-align:middle;margin-right:6px}
@keyframes spin{to{transform:rotate(360deg)}}
hr{border:none;border-top:1px solid #1a1a26;margin:18px 0}
.ft{font-size:11px;color:#3a3a4a;text-align:center;margin-top:14px}
a{color:#1877F2;text-decoration:none}
.switch-link{text-align:center;margin-top:10px;font-size:12px;color:#5a5a70}
</style>
</head>
<body>
<div class="panel">
<div class="logo"><div class="logo-icon">F</div><div class="logo-text"><h1>Token Extractor v3</h1><p>Session → EAAD6V7 + EAAAAU</p></div></div>

<div id="s1">
<div class="grp"><label>📧 Email / Phone / UID</label><input type="text" id="cred" placeholder="email@domain.com / +91XXXXXXXXXX / 1000123456789"></div>
<div class="grp"><label>🔑 Password</label><input type="password" id="pass" placeholder="••••••••"></div>
<button class="btn" id="loginBtn" onclick="doLogin()">⚡ Login &amp; Extract Tokens</button>
<div id="st1" class="st-box"></div>
</div>

<div id="s2" class="hide">
<div class="grp"><label>🔐 2FA Code</label><input type="text" id="tfa" placeholder="6-digit code from authenticator / SMS"></div>
<button class="btn" id="tfaBtn" onclick="doTFA()">Submit 2FA &amp; Continue</button>
<div class="switch-link">Don't have 2FA? <a href="#" onclick="showForgot()">Use Password Reset Code →</a></div>
<div id="st2" class="st-box"></div>
</div>

<div id="s3" class="hide">
<div class="grp"><label>📨 Password Reset OTP</label><input type="text" id="fgt" placeholder="6-digit code sent to email / SMS"></div>
<button class="btn" id="fgtBtn" onclick="doForgot()">Submit Reset Code &amp; Continue</button>
<div class="switch-link"><a href="#" onclick="show2FA()">← Back to 2FA</a></div>
<div id="st3" class="st-box"></div>
</div>

<hr>

<div id="tkEAAD" class="tk-box"><div class="tk-label">🔑 EAAD6V7 (User Access Token)</div><div class="tk-val" id="vEAAD">—</div><button class="cp-btn" onclick="cp('vEAAD')">📋 Copy EAAD6V7</button></div>
<div id="tkEAAA" class="tk-box"><div class="tk-label">🔑 EAAAAU (User Token)</div><div class="tk-val" id="vEAAA">—</div><button class="cp-btn" onclick="cp('vEAAA')">📋 Copy EAAAAU</button></div>
<div id="stRes" class="st-box"></div>
<div class="ft">Authorized security testing only. All sessions are sandbox-isolated.</div>
</div>

<script>
function $(i){return document.getElementById(i)}
function st(i,m,t){const e=$(i);e.textContent=m;e.className='st-box '+t}
function sc(i){$(i).textContent='';$(i).className='st-box'}
function ld(b,l){const e=$(b)
if(l){e.disabled=true;e.innerHTML='<span class="spin"></span>Processing...'}
else{e.disabled=false;e.innerHTML=b==='loginBtn'?'⚡ Login & Extract Tokens':b==='tfaBtn'?'Submit 2FA & Continue':'Submit Reset Code & Continue'}}
function s2FA(){$('s3').classList.add('hide');$('s2').classList.remove('hide')}
function sFgt(){$('s2').classList.add('hide');$('s3').classList.remove('hide')}
function stk(eaad,eaaa){
$('vEAAD').textContent=eaad||'Not found';$('tkEAAD').classList.add('show')
$('vEAAA').textContent=eaaa||'Not found';$('tkEAAA').classList.add('show')}
function cp(i){
const t=$(i).textContent
if(t&&t!=='—'&&t!=='Not found'){navigator.clipboard.writeText(t).then(()=>{st('stRes','✓ Token copied to clipboard!','success');setTimeout(()=>sc('stRes'),2500)})}}
async function doLogin(){
const c=$('cred').value.trim(),p=$('pass').value
if(!c||!p){st('st1','❌ Please fill in both fields.','error');return}
ld('loginBtn',true);sc('st1')
try{
const r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({credential:c,password:p})})
const d=await r.json()
if(d.success){
if(d.tfa_required){
$('s1').classList.add('hide');$('s2').classList.remove('hide')
if(d.reset_code_available){$('s2').classList.add('hide');$('s3').classList.remove('hide')}
st('st1','🔐 2FA required. Enter the code below.','success')
}else{st('st1','✅ Login successful! Tokens extracted.','success');stk(d.EAAD6V7||'',d.EAAAAU||'')}
}else{st('st1','❌ '+(d.error||'Login failed.'),'error')}
}catch(e){st('st1','❌ Error: '+e.message,'error')}
ld('loginBtn',false)}
async function doTFA(){
const c=$('tfa').value.trim()
if(!c){st('st2','❌ Please enter the 2FA code.','error');return}
ld('tfaBtn',true);sc('st2')
try{
const r=await fetch('/api/tfa',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({credential:$('cred').value.trim(),password:$('pass').value,code:c,method:'2fa'})})
const d=await r.json()
if(d.success){st('st2','✅ Tokens extracted successfully!','success');stk(d.EAAD6V7||'',d.EAAAAU||'');$('s2').classList.add('hide')}
else{st('st2','❌ '+(d.error||'Invalid code.'),'error')}
}catch(e){st('st2','❌ Error: '+e.message,'error')}
ld('tfaBtn',false)}
async function doForgot(){
const c=$('fgt').value.trim()
if(!c){st('st3','❌ Please enter the reset code.','error');return}
ld('fgtBtn',true);sc('st3')
try{
const r=await fetch('/api/tfa',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({credential:$('cred').value.trim(),password:$('pass').value,code:c,method:'forgot'})})
const d=await r.json()
if(d.success){st('st3','✅ Tokens extracted successfully!','success');stk(d.EAAD6V7||'',d.EAAAAU||'');$('s3').classList.add('hide')}
else{st('st3','❌ '+(d.error||'Invalid code.'),'error')}
}catch(e){st('st3','❌ Error: '+e.message,'error')}
ld('fgtBtn',false)}
</script>
</body></html>'''


# ============================================================
# FACEBOOK AUTH ENGINE
# ============================================================

FB_API_KEY = '3e7c78e35a76a9299309885393b02d97'
FB_SECRET = 'c1e620fa708a1d5696fb991c1bde5662'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Content-Type': 'application/x-www-form-urlencoded',
}


def _gen_sig(params):
    raw = ''.join(f'{k}={params[k]}' for k in sorted(params))
    raw += FB_SECRET
    return hashlib.md5(raw.encode()).hexdigest()


def fb_api_call(params):
    params['sig'] = _gen_sig(params)
    r = req.post('https://api.facebook.com/restserver.php', data=params, headers=HEADERS, timeout=20)
    return r.json()


# -----------------------------------------------------------
# STEP 1: LOGIN → Get session + access_token
# -----------------------------------------------------------
def do_fb_login(credential, password):
    params = {
        'api_key': FB_API_KEY,
        'email': credential,
        'format': 'JSON',
        'generate_machine_id': '1',
        'generate_session_cookies': '1',
        'locale': 'en_US',
        'method': 'auth.login',
        'password': password,
        'return_ssl_resources': '0',
        'v': '1.0',
    }
    data = fb_api_call(params)

    if 'error_code' in data:
        err = data.get('error_msg', str(data))
        # Check if it's 2FA required
        if 'login_approval' in str(data).lower() or 'two_factor' in str(data).lower() or '2fa' in str(data).lower() or 'approvals' in str(data).lower():
            return {'success': False, 'tfa_required': True, 'error': err, 'reset_code_available': True}
        return {'success': False, 'error': err}

    if 'session_key' not in data:
        return {'success': False, 'error': 'No session key returned. Login may have failed.'}

    access_token = data.get('access_token', '')
    session_key = data.get('session_key', '')
    uid = data.get('uid', '')

    # Build cookie jar for further token extraction
    cookies_raw = data.get('session_cookies', [])
    cookie_dict = {}
    if isinstance(cookies_raw, list):
        for c in cookies_raw:
            if isinstance(c, dict) and 'name' in c and 'value' in c:
                cookie_dict[c['name']] = c['value']

    return {
        'success': True,
        'access_token': access_token,
        'session_key': session_key,
        'uid': uid,
        'cookies': cookie_dict,
        'tfa_required': False,
    }


# -----------------------------------------------------------
# STEP 2: EXTRACT EAAD6V7 + EAAAAU from business pages
# -----------------------------------------------------------
def extract_tokens(cookies):
    """Visit Facebook pages to extract EAAD6V7 and EAAAAU tokens."""
    eaad_token = ''
    eaaa_token = ''

    s = req.Session()
    s.headers.update(HEADERS)

    # Set cookies
    for name, val in cookies.items():
        s.cookies.set(name, val, domain='.facebook.com')

    try:
        # --- EAAD6V7 from Events Manager ---
        r1 = s.get('https://www.facebook.com/events_manager2/overview', timeout=15)
        # Pattern: "accessToken":"EAAD...
        m1 = re.search(r'"accessToken":"(EAAD\w+)"', r1.text)
        if m1:
            eaad_token = m1.group(1)
        else:
            # Try alternative: access_token":"EAAD...
            m1b = re.search(r'access_token["\']?\s*[:=]\s*["\'](EAAD\w+)', r1.text)
            if m1b:
                eaad_token = m1b.group(1)
            else:
                # Try EAAG token as fallback
                m1c = re.search(r'(EAAG\w+)', r1.text)
                if m1c:
                    eaad_token = m1c.group(1)

        # --- EAAAAU from business/content_management ---
        r2 = s.get('https://business.facebook.com/content_management', timeout=15)
        m2 = re.search(r'(EAAAAU\w+)', r2.text)
        if m2:
            eaaa_token = m2.group(1)
        else:
            # Try from business_locations
            r2b = s.get('https://business.facebook.com/business_locations', timeout=15)
            m2b = re.search(r'(EAAAAU\w+)', r2b.text)
            if m2b:
                eaaa_token = m2b.group(1)
            else:
                # Fallback: any EAAB/EA prefix token
                m2c = re.search(r'(EAAA\w+)', r2b.text)
                if m2c:
                    eaaa_token = m2c.group(1)

        # If still nothing, try adsmanager
        if not eaad_token:
            r3 = s.get('https://www.facebook.com/adsmanager/manage/campaigns', timeout=15)
            m3 = re.search(r'(EAAD\w+)', r3.text)
            if m3:
                eaad_token = m3.group(1)

        if not eaaa_token:
            r4 = s.get('https://www.facebook.com/adsmanager/manage/', timeout=15)
            m4 = re.search(r'accessToken["\']?\s*:\s*["\'](EAA\w+)', r4.text)
            if m4:
                eaaa_token = m4.group(1)

    except Exception as e:
        pass

    return eaad_token, eaaa_token


# -----------------------------------------------------------
# STEP 3: HANDLE 2FA
# -----------------------------------------------------------
def do_2fa(credential, password, code, method='2fa'):
    """Submit 2FA or password reset code."""
    params = {
        'api_key': FB_API_KEY,
        'email': credential,
        'format': 'JSON',
        'generate_machine_id': '1',
        'generate_session_cookies': '1',
        'locale': 'en_US',
        'method': 'auth.login',
        'password': password,
        'return_ssl_resources': '0',
        'v': '1.0',
    }

    # Add 2FA or reset code parameter
    if method == '2fa':
        params['twofactor_code'] = code
    else:  # forgot password code
        params['forgot_password_code'] = code

    data = fb_api_call(params)

    if 'error_code' in data:
        return {'success': False, 'error': data.get('error_msg', 'Invalid code')}

    if 'session_key' not in data:
        return {'success': False, 'error': 'Authentication failed after code submission.'}

    access_token = data.get('access_token', '')
    cookies_raw = data.get('session_cookies', [])
    cookie_dict = {}
    if isinstance(cookies_raw, list):
        for c in cookies_raw:
            if isinstance(c, dict) and 'name' in c and 'value' in c:
                cookie_dict[c['name']] = c['value']

    # Extract tokens
    eaad, eaaa = extract_tokens(cookie_dict)

    return {
        'success': True,
        'access_token': access_token,
        'EAAD6V7': eaad,
        'EAAAAU': eaaa,
        'uid': data.get('uid', ''),
    }


# ============================================================
# FLASK ROUTES
# ============================================================

@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/api/login', methods=['POST'])
def api_login():
    body = request.get_json()
    if not body:
        return jsonify({'success': False, 'error': 'No data received'})

    credential = body.get('credential', '').strip()
    password = body.get('password', '')

    if not credential or not password:
        return jsonify({'success': False, 'error': 'Missing credential or password'})

    result = do_fb_login(credential, password)

    if not result['success']:
        if result.get('tfa_required'):
            return jsonify({
                'success': True,
                'tfa_required': True,
                'reset_code_available': result.get('reset_code_available', False),
                'error': result.get('error', '')
            })
        return jsonify({'success': False, 'error': result.get('error', 'Login failed')})

    # Extract tokens using cookies
    cookies = result.get('cookies', {})
    eaad, eaaa = extract_tokens(cookies)

    return jsonify({
        'success': True,
        'tfa_required': False,
        'EAAD6V7': eaad,
        'EAAAAU': eaaa,
        'uid': result.get('uid', ''),
        'access_token': result.get('access_token', ''),
    })


@app.route('/api/tfa', methods=['POST'])
def api_tfa():
    body = request.get_json()
    if not body:
        return jsonify({'success': False, 'error': 'No data received'})

    credential = body.get('credential', '').strip()
    password = body.get('password', '')
    code = body.get('code', '').strip()
    method = body.get('method', '2fa')

    if not credential or not password or not code:
        return jsonify({'success': False, 'error': 'Missing required fields'})

    result = do_2fa(credential, password, code, method)
    return jsonify(result)


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
