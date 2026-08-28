# School AI

A single-page study assistant that runs entirely in a browser tab. No install, no build step, nothing to download — just open a URL (or a single HTML file) and it works.

## What's in it

- **Chat** — an AI homework helper. Calls the Anthropic API directly from your browser using your own API key (stored only in that browser's local storage). Explains and guides rather than just handing over answers.
- **Flashcards** — paste `term :: definition` lines to build a deck, then study with flip cards and a simple "still learning / got it" queue.
- **Planner** — track assignments with subject, due date, and priority; overdue/due-today badges.
- **Timer** — a Pomodoro-style focus/break timer.
- **GPA calculator** — standard 4.0-scale weighted GPA from your course list.
- **Settings** — set/remove your API key and model, and back up all your data (planner, decks, GPA, key) as text you can copy out and paste back in later, since everything lives in local storage on one device/browser.

Everything except the Chat tab works completely offline with no API key.

## Using it without downloading anything

If you're on a locked-down or shared computer (e.g. a school Chromebook) and can't save files, the easiest path is to open the page from a URL instead of a file:

1. Enable GitHub Pages once for this repo: **Settings → Pages → Source → GitHub Actions**. The included workflow (`.github/workflows/pages.yml`) then deploys `index.html` automatically on every push to `main`.
2. Open the resulting `https://<your-username>.github.io/school-ai/` URL in a tab. That's it — no download required, and it will keep re-deploying whenever this branch is merged to `main`.

If you *can* save a file, `index.html` is fully self-contained — save it anywhere and double-click to open it in any browser.

## Getting an API key for the Chat tab

The Chat tab needs an [Anthropic API key](https://console.anthropic.com/settings/keys) to work. Paste it into **Settings**. It's sent only to `api.anthropic.com` directly from your browser and stored only in that browser's local storage — never uploaded anywhere else. Note that some school networks block direct API calls; if Chat can't connect, the other tabs still work fully offline.

## Notes on data persistence

Local storage is tied to one browser on one device. If your school computer resets its profile between logins, your planner/decks/GPA data (and API key) can be wiped. Use **Settings → Copy backup to clipboard** to save a text snapshot somewhere (a note to yourself, a doc) and **Restore from backup** to bring it back later.
