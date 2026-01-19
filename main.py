from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import hashlib
import json
import uvicorn

app = FastAPI()

# -------------- Config --------------
CANVA_URL = "https://smartbartender.my.canva.site/dag-sgpflmm"
BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / "users.json"

# Static folder for background images
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# -------------- User / Password Tools --------------
def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def load_users() -> dict:
    """Load users.json or return empty."""
    if not USERS_FILE.exists():
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users: dict):
    """Save users dict to users.json."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def init_default_admin():
    """Create admin:1234 if missing."""
    users = load_users()
    if "admin" not in users:
        users["admin"] = hash_password("1234")
        save_users(users)


init_default_admin()

# -------------- Shared CSS (Background Image + Glass Card) --------------
BLACK_STYLE = """
<style>
  * { box-sizing: border-box; }

  body {
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;

    background-color: #000;
    background-image: url('/static/background 2.png');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;

    color: white;
  }

  /* Dark overlay to keep text readable */
  body::before {
    content: "";
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.50);
    z-index: -1;
  }

  .overlay {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
  }

  .card {
    background: rgba(255, 255, 255, 0.10);
    backdrop-filter: blur(8px);
    border-radius: 18px;

    padding: 48px 64px;
    width: 95%;
    max-width: 520px;

    text-align: center;
    box-shadow: 0 0 25px rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.20);

    opacity: 0;
    transform: translateY(12px);
    animation: fadeInUp 0.6s ease-out forwards;
  }

  h1, h2 {
    margin-top: 0;
    letter-spacing: 1px;
    font-weight: 600;
  }

  h3 {
    margin-top: 8px;
    margin-bottom: 22px;
    font-weight: 500;
  }

  /* Inputs */
  input {
    width: 100%;
    max-width: 380px;
    padding: 10px 12px;
    border-radius: 10px;
    border: none;
    margin-bottom: 12px;
    font-size: 15px;
  }

  /* ✅ Important: remove default form spacing + add consistent spacing */
  form { margin: 0; }
  form + form { margin-top: 16px; }

  /* ✅ Buttons fixed (same shape, same size, same text style) */
  button {
    width: 320px;              /* wide enough for long label */
    height: 56px;              /* fixed height => identical pills */
    border-radius: 999px;      /* perfect pill */

    border: 1px solid #fff;
    background: #fff;
    color: #000;

    font-size: 16px;           /* bigger text */
    font-weight: 500;

    display: inline-flex;
    align-items: center;
    justify-content: center;

    padding: 0 24px;
    cursor: pointer;
    transition: background 0.2s ease, transform 0.15s ease;
  }

  button:hover {
    background: #e5e5e5;
    transform: translateY(-1px);
  }

  a {
    color: #f0f0f0;
    text-decoration: underline;
    font-size: 14px;
  }

  .small-text {
    font-size: 13px;
    margin-top: 10px;
  }

  .error-text { color: #ff6161; }
  .success-text { color: #7fff7f; }

  label.show-toggle {
    font-size: 13px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 10px;
  }

  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(18px); }
    to { opacity: 1; transform: translateY(0px); }
  }

  /* Mobile: keep buttons responsive */
  @media (max-width: 420px) {
    .card { padding: 36px 20px; }
    button { width: 100%; }
  }
</style>
"""


# -------------- MAIN PAGE --------------
@app.get("/", response_class=HTMLResponse)
async def home():
    html = f"""
    <html><head><title>Smart Bartender Login</title>{BLACK_STYLE}</head>
    <body>
      <div class="overlay">
        <div class="card">
          <h1>SMART BARTENDER</h1>
          <h3>Open login page</h3>

          <form action="/login" method="get">
            <button type="submit">Sign in</button>
          </form>

          <form action="/register" method="get">
            <button type="submit">Create an Account</button>
          </form>
        </div>
      </div>
    </body></html>
    """
    return HTMLResponse(html)


# -------------- LOGOUT --------------
@app.get("/logout")
async def logout():
    return RedirectResponse("/", status_code=302)


# -------------- REGISTER PAGE --------------
@app.get("/register", response_class=HTMLResponse)
async def register_form():
    html = f"""
    <html><head><title>Register</title>{BLACK_STYLE}</head>
    <body>
      <div class="overlay">
        <div class="card">
          <h2>Create Account</h2>

          <form method="post">
            <input name="username" placeholder="Username" required><br>
            <input id="regPassword" name="password" type="password" placeholder="Password" required><br>

            <label class="show-toggle">
              <input type="checkbox" id="showRegPassword"> Show password
            </label><br>

            <button type="submit">Register</button>
          </form>

          <p class="small-text"><a href="/">Back to main page</a></p>
        </div>
      </div>

      <script>
        const regPw = document.getElementById('regPassword');
        const showPw = document.getElementById('showRegPassword');
        showPw.addEventListener('change', () => {{
          regPw.type = showPw.checked ? 'text' : 'password';
        }});
      </script>
    </body></html>
    """
    return HTMLResponse(html)


@app.post("/register", response_class=HTMLResponse)
async def register(username: str = Form(...), password: str = Form(...)):
    users = load_users()

    if username in users:
        return HTMLResponse(f"""
        <html><head>{BLACK_STYLE}</head><body>
          <div class="overlay"><div class="card">
            <h2 class="error-text">Username '{username}' already exists.</h2>
            <p class="small-text"><a href="/register">Try another username</a></p>
            <p class="small-text"><a href="/">Back to main page</a></p>
          </div></div>
        </body></html>
        """)

    if len(password) < 4:
        return HTMLResponse(f"""
        <html><head>{BLACK_STYLE}</head><body>
          <div class="overlay"><div class="card">
            <h2 class="error-text">Password must be at least 4 characters.</h2>
            <p class="small-text"><a href="/register">Try again</a></p>
          </div></div>
        </body></html>
        """)

    users[username] = hash_password(password)
    save_users(users)

    return HTMLResponse(f"""
    <html><head>{BLACK_STYLE}</head><body>
      <div class="overlay"><div class="card">
        <h2 class="success-text">Account '{username}' created!</h2>
        <p class="small-text"><a href="/login">Go to login</a></p>
        <p class="small-text"><a href="/">Back to main page</a></p>
      </div></div>
    </body></html>
    """)


# -------------- FORGOT PASSWORD PAGE --------------
@app.get("/forgot", response_class=HTMLResponse)
async def forgot_form():
    html = f"""
    <html><head><title>Reset Password</title>{BLACK_STYLE}</head>
    <body>
      <div class="overlay">
        <div class="card">
          <h2>Reset Password</h2>

          <form method="post">
            <input name="username" placeholder="Enter your username" required><br>
            <input name="new_password" type="password" placeholder="New password" required><br>
            <button type="submit">Reset Password</button>
          </form>

          <p class="small-text"><a href="/login">Back to login</a></p>
        </div>
      </div>
    </body></html>
    """
    return HTMLResponse(html)


@app.post("/forgot", response_class=HTMLResponse)
async def forgot(username: str = Form(...), new_password: str = Form(...)):
    users = load_users()

    if username not in users:
        return HTMLResponse(f"""
        <html><head>{BLACK_STYLE}</head><body>
          <div class="overlay"><div class="card">
            <h2 class="error-text">Username not found.</h2>
            <p class="small-text"><a href="/forgot">Try again</a></p>
          </div></div>
        </body></html>
        """)

    if len(new_password) < 4:
        return HTMLResponse(f"""
        <html><head>{BLACK_STYLE}</head><body>
          <div class="overlay"><div class="card">
            <h2 class="error-text">Password must be at least 4 characters.</h2>
            <p class="small-text"><a href="/forgot">Try again</a></p>
          </div></div>
        </body></html>
        """)

    users[username] = hash_password(new_password)
    save_users(users)

    return HTMLResponse(f"""
    <html><head>{BLACK_STYLE}</head><body>
      <div class="overlay"><div class="card">
        <h2 class="success-text">Password reset successfully!</h2>
        <p class="small-text"><a href="/login">Return to login</a></p>
      </div></div>
    </body></html>
    """)


# -------------- LOGIN PAGE --------------
@app.get("/login", response_class=HTMLResponse)
async def login_form():
    html = f"""
    <html><head><title>Login</title>{BLACK_STYLE}</head>
    <body>
      <div class="overlay">
        <div class="card">
          <h2>Login</h2>

          <form method="post">
            <input name="username" placeholder="Username" required><br>
            <input id="loginPassword" name="password" type="password" placeholder="Password" required><br>

            <label class="show-toggle">
              <input type="checkbox" id="showLoginPassword"> Show password
            </label><br>

            <button type="submit">Log in</button>
          </form>

          <p class="small-text"><a href="/forgot">Forgot password?</a></p>
          <p class="small-text"><a href="/register">Create a new account</a></p>
          <p class="small-text"><a href="/">Back to main page</a></p>
        </div>
      </div>

      <script>
        const loginPw = document.getElementById('loginPassword');
        const showPw = document.getElementById('showLoginPassword');
        showPw.addEventListener('change', () => {{
          loginPw.type = showPw.checked ? 'text' : 'password';
        }});
      </script>
    </body></html>
    """
    return HTMLResponse(html)


@app.post("/login", response_class=HTMLResponse)
async def login(username: str = Form(...), password: str = Form(...)):
    users = load_users()
    hashed = hash_password(password)

    if username in users and users[username] == hashed:
        html = f"""
        <html><head><title>Welcome</title>{BLACK_STYLE}</head>
        <body>
          <div class="overlay">
            <div class="card">
              <h2 class="success-text">Welcome, {username}!</h2>
              <p>You are now logged in.</p>

              <form action="{CANVA_URL}" method="get">
                <button type="submit">Go to Smart Bartender site</button>
              </form>

              <form action="/logout" method="get">
                <button type="submit">Logout</button>
              </form>
            </div>
          </div>
        </body></html>
        """
        return HTMLResponse(html)

    return HTMLResponse(f"""
    <html><head>{BLACK_STYLE}</head><body>
      <div class="overlay"><div class="card">
        <h2 class="error-text">Invalid username or password</h2>
        <p class="small-text"><a href="/login">Try again</a></p>
      </div></div>
    </body></html>
    """)


# -------------- RUN SERVER --------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8014, reload=True)
