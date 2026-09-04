from html import escape
from config import BASE_DIR, INDEX_FILE, ROW_Y, RIGHT, LEFT


def rank_class(rank):
    if rank in (1, 2):
        return 'rank gold'
    if rank == 3:
        return 'rank grey'
    if rank >= 14:
        return 'rank danger'
    return 'rank'


def local_logo(filename):
    if not filename:
        return None
    path = BASE_DIR / 'assets' / 'logos' / filename
    if path.exists() and path.stat().st_size > 0:
        return 'assets/logos/' + filename
    return None


def logo_markup(team):
    # Prefer the downloaded local logo; otherwise use Flashscore's URL.
    logo_src = local_logo(team.get('logo')) or team.get('logo_src') or ''
    if not logo_src:
        return ''
    return (
        f'<img src="{escape(logo_src, quote=True)}" '
        f'alt="" class="team-logo" loading="eager" decoding="async">'
    )


def row_right(team, y):
    """Ranks 1-8. Visual order: MJ | PTS | ÉQUIPE | LOGO | RANG."""
    return f'''
      <div class="dynamic-row row-right" style="top:{y}px;">
        <div class="cell played" style="left:{RIGHT['played_x']}px;">{escape(str(team['played']))}</div>
        <div class="cell points" style="left:{RIGHT['points_x']}px;">{escape(str(team['points']))}</div>
        <div class="cell team-name" style="left:{RIGHT['team_x']}px;width:{RIGHT['team_width']}px;">{escape(team['arabic'])}</div>
        <div class="cell leftforlogo logo">{logo_markup(team)}</div>
        <div class="cell {rank_class(int(team['rank']))}" style="left:{RIGHT['rank_x']}px;">{int(team['rank'])}</div>
      </div>'''


def row_left(team, y):
    """Ranks 9-16. EXACT same visual order as the right table: MJ | PTS | ÉQUIPE | LOGO | RANG."""
    return f'''
      <div class="dynamic-row row-left" style="top:{y}px;">
        <div class="cell played" style="left:{LEFT['played_x']}px;">{escape(str(team['played']))}</div>
        <div class="cell points" style="left:{LEFT['points_x']}px;">{escape(str(team['points']))}</div>
        <div class="cell team-name" style="left:{LEFT['team_x']}px;width:{LEFT['team_width']}px;">{escape(team['arabic'])}</div>
        <div class="cell rightforlogo logo">{logo_markup(team)}</div>
        <div class="cell {rank_class(int(team['rank']))}" style="left:{LEFT['rank_x']}px;">{int(team['rank'])}</div>
      </div>'''


def rows_html(standings):
    parts = []
    for team in standings:
        rank = int(team['rank'])
        pos = rank if rank <= 8 else rank - 8
        y = ROW_Y[pos]
        parts.append(row_right(team, y) if rank <= 8 else row_left(team, y))
    return ''.join(parts)


def build_index(standings):
    dynamic = rows_html(standings)
    return f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LA ANT MATCH — ترتيب</title>
  <link rel="stylesheet" href="style.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Alexandria:wght@100..900&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
</head>
<body>
<button id="updateBtn" class="export-btn update-btn" type="button">
    <span class="export-icon">↻</span>
    <span>UPDATE</span>
</button>
<button id="exportBtn" class="export-btn" type="button">
    <span class="export-icon">↓</span>
    <span>EXPORT</span>
</button>
<button id="flashscoreBtn" class="export-btn flashscore-btn" type="button">
    <span class="export-icon">↗</span>
    <span>FLASHSCORE</span>
</button>
<button id="editAssetsBtn" class="export-btn edit-assets-btn" type="button">
    <span class="export-icon">✎</span>
    <span>EDIT</span>
</button>
<div id="updateNotice" class="update-notice" role="status" aria-live="polite"></div>
<section id="exportOptions" class="export-options" hidden>
  <button id="closeExportOptions" class="export-options-close" type="button">×</button>
  <strong>EXPORT OPTIONS</strong>
  <button id="exportFullBtn" type="button">FULL TABLE</button>
  <label for="exportRowCount">NUMBER OF ROWS</label>
  <input id="exportRowCount" type="number" min="1" max="16" value="4">
  <button id="exportCustomBtn" type="button">EXPORT ROWS</button>
</section>
<section id="assetPanel" class="asset-panel" hidden>
  <button id="closeAssetPanel" class="asset-panel-close" type="button">×</button>
  <strong>UPLOAD ASSET</strong>
  <label for="hashtagText">Hashtag</label>
  <input id="hashtagText" type="text" value="#الرابطة_المحترفة_الأولى" dir="rtl">
  <label for="assetFolder">Folder</label>
  <select id="assetFolder">
    <option value="background">background</option>
    <option value="branding">branding</option>
    <option value="competition">competition</option>
    <option value="cup">cup</option>
    <option value="teams">teams</option>
  </select>
  <select id="teamTarget" hidden></select>
  <input id="assetFile" type="file" accept="image/*">
  <button id="uploadAssetBtn" type="button">UPLOAD</button>
</section>
  <main class="board">
    <img class="background" src="assets/background.png" alt="">
    <img class="cup" src="assets/cup.png" alt="">
    <img class="shadow-overlay" src="assets/shadow.png" alt="" aria-hidden="true">
    <img class="laant-logo" src="assets/logo.png" alt="LA ANT MATCH">
    <img class="ligue-live" src="assets/ligue live DS.png" alt="">

    <section class="competition">
      <div class="hashtag">#الرابطة_المحترفة_الأولى</div>
      <img src="./assets/tartib.png" alt="ترتيب" class="competition-logo">
    </section>

    <!-- BOTH tables use EXACTLY the same left-to-right order:
         MJ | PTS | NOM ÉQUIPE | LOGO | RANG. -->
    <section class="table table-left">
      <div class="headers headers-left">
        <span>لعب</span><span>نقاط</span>
      </div>
    </section>

    <section class="table table-right">
      <div class="headers headers-right">
        <span>لعب</span><span>نقاط</span>
      </div>
    </section>

    <div class="divider"></div>
    <section class="dynamic-data">{dynamic}
    </section>
  </main>
  <script type="module" src="script.js"></script>
</body>
</html>
'''


def write_index(standings):
    INDEX_FILE.write_text(build_index(standings), encoding='utf-8')
    print(f'index.html generated: {INDEX_FILE}')
