import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'C:/techpulse-daily')
from atomtech_instagram import parse_social_posts, parse_sources, parse_digest, build_caption
from pathlib import Path

issue_dir = Path('C:/techpulse-daily/issues/2026-05-09')
stories   = parse_social_posts(issue_dir)
domains   = parse_sources(issue_dir)
summaries = parse_digest(issue_dir)

lines = []
for s in stories:
    n = s['number']
    caption = build_caption(s, summaries.get(n, s['hook']), domains)
    lines.append(f"=== POST {n:02d} — {s['headline'][:65]} ===")
    lines.append(f"IMAGEN: C:\\techpulse-daily\\issues\\2026-05-09\\instagram\\{n:02d}.jpg")
    lines.append("CAPTION:")
    lines.append(caption)
    lines.append("")
    lines.append("=" * 70)
    lines.append("")

Path('C:/techpulse-daily/captions_para_instagram.txt').write_text('\n'.join(lines), encoding='utf-8')
print(f"OK — {len(stories)} captions escritas en captions_para_instagram.txt")
