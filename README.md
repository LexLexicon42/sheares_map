# 🌍 WorldMeet

**when2meet, but for countries.** Mark where you're going on a world map, add optional date ranges, and see where your friends are heading — hover any highlighted country to see who's visiting and when.

---

## Running locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run
python app.py
```

Open http://localhost:5000, create a board, and share the URL with friends.

---

## Deploying (free hosting)

### Option A — Railway ⭐ (recommended)
Railway gives you a free tier with **persistent storage**, so your SQLite database survives between deploys.

1. Push this folder to a GitHub repo
2. Go to https://railway.app → New Project → Deploy from GitHub repo
3. Railway auto-detects the Procfile — hit Deploy
4. Your app gets a public URL like `https://worldmeet-production.up.railway.app`

That's it. No extra config needed.

### Option B — PythonAnywhere (also free, very simple)
Good if you don't want to use GitHub.

1. Sign up at https://www.pythonanywhere.com (free Beginner account)
2. Go to **Files** → upload all files (keeping the `templates/` folder structure)
3. Open a **Bash console** and run:
   ```bash
   pip install flask gunicorn --user
   python app.py  # just to create the DB
   ```
4. Go to **Web** tab → Add new web app → Flask → point it to `/home/<you>/app.py`
5. You get a URL like `https://yourname.pythonanywhere.com`

### Option C — Render (free but ⚠️ DB resets on redeploy)
Render's free tier has ephemeral storage — the SQLite file is wiped whenever the app redeploys. Fine for testing, not great long-term. If you want Render, add a **Disk** ($1/mo) and set `DATABASE` env var to point to it.

---

## How it works

- **Create a board** → you get a unique 8-character URL (`/board/abc12345`)
- **Share the URL** with friends — no accounts, they just enter their name
- **Click any country** on the map → optionally pick arrival/departure dates → Save
- **Hover a green country** → tooltip shows everyone going there and their dates
- **Green intensity** = more people going there (darker = more overlap)
- Map **auto-refreshes** every 12 seconds so everyone sees updates live

---

## Project structure

```
worldmeet/
├── app.py              ← Flask backend + SQLite
├── requirements.txt
├── Procfile
├── worldmeet.db        ← created automatically on first run
└── templates/
    ├── index.html      ← landing / create board page
    └── board.html      ← interactive map page
```

---

## Customising

- **Change the poll interval**: in `board.html`, find `setInterval(loadEntries, 12000)` — the number is milliseconds
- **Add a country**: the `CN` object in `board.html` maps ISO numeric codes to names; just add `"123": "Country Name"`
- **Colour scheme**: the gradient is in `colorFor()` — swap `'#bbf7d0'` / `'#14532d'` for any two hex colours
