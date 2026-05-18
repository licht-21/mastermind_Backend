# Deploy Flask online (URL-only Android app)

Right now your stack is **local**:

```
Phone (Wi-Fi / USB) → Flask on PC (192.168.x.x:5000) → MySQL on PC
```

To depend **only on a URL** (anywhere with internet), host **both** online:

```
Phone (mobile data or any Wi-Fi) → Flask on cloud (https://your-api.com) → MySQL on cloud
```

The Android app only needs to change `BASE_URL` in `RetrofitClient.java` once.

---

## What must be online

| Piece | Local now | Online |
|--------|-----------|--------|
| Flask API | Your PC port 5000 | Cloud server (Render, Railway, PythonAnywhere, VPS) |
| MySQL | Your PC port 3306 | Cloud MySQL (PlanetScale, Railway, Aiven, AWS RDS, etc.) |
| Android | `http://192.168.x.x:5000/` | `https://your-app.onrender.com/` |

MySQL is **never** called from the phone—only Flask uses it.

---

## Recommended path (student / free tier)

### 1. Cloud MySQL

Pick one:

- **Railway** – MySQL plugin, connection string in dashboard  
- **PlanetScale** – free tier (note: may need SQL dialect tweaks)  
- **Aiven** – free MySQL trial  

Create database `saving_db` and run **`schema.sql`** from this folder.

### 2. Update Flask for production

In `config.py` / `routes.py`, use **environment variables** instead of hardcoded passwords:

```python
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "saving_db")
```

On the host, set:

- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- Run with **HTTPS** (host provides SSL)

Use **gunicorn** in production (not `flask run`):

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 "run:app"
```

### 3. Deploy Flask (example: Render)

1. Push `mastermind` to GitHub (no `.venv`, no passwords in repo).  
2. [render.com](https://render.com) → New **Web Service** → connect repo.  
3. Build: `pip install -r requirements.txt`  
4. Start: `gunicorn -w 2 -b 0.0.0.0:$PORT run:app`  
5. Add environment variables for MySQL.  
6. You get a URL like: `https://saving-api-xxxx.onrender.com`

### 4. Android app – one URL

In `RetrofitClient.java`:

```java
private static final String BASE_URL = "https://saving-api-xxxx.onrender.com/";
```

- Use **`https://`** (not `http://`) for public hosts.  
- Trailing `/` required.  
- Rebuild and install the APK.

No Wi-Fi to your PC, no `10.0.2.2`, no `adb reverse`.

---

## Security checklist (before going public)

- [ ] Change default MySQL passwords  
- [ ] Do not commit `passwordito` to GitHub  
- [ ] Use **HTTPS** only in production  
- [ ] Hash passwords (bcrypt) instead of plain text in `users.password`  
- [ ] Add rate limiting on `/api/login` and `/api/register`  
- [ ] Restrict CORS if you add a web client (Android native app does not need CORS)

---

## Quick comparison

| Mode | BASE_URL example | Needs same Wi-Fi? |
|------|------------------|-------------------|
| Emulator + PC | `http://10.0.2.2:5000/` | Yes (PC running Flask) |
| Physical phone + PC | `http://192.168.1.x:5000/` | Yes |
| USB + adb reverse | `http://127.0.0.1:5000/` | USB + adb each time |
| **Online** | `https://your-api.onrender.com/` | **No** – only internet |

---

## Files in this folder

| File | Use |
|------|-----|
| `schema.sql` | **Full database** – new install |
| `schema_migrations.sql` | Upgrade old DB (Phase 2+3 columns) |
| `schema_phase1.sql` … `phase3.sql` | Historical steps (optional) |
| `config.py` | Local DB credentials |
| `run.py` | Local dev server |

After deploy, test from a browser or phone browser:

`https://your-api.onrender.com/api/savings`  

(Will return 401 without `X-User-Id`—that proves the server is up.)
