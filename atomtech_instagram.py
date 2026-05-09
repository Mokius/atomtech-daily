#!/usr/bin/env python3
"""
AtomTech Daily - Instagram Auto-Poster
Lee el issue del dia, genera imagenes con DALL-E 3,
compone texto encima y publica en @atomtech_daily.
"""

import os, re, time, textwrap
from pathlib import Path
from datetime import date
from io import BytesIO

import requests
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
from instagrapi import Client

# ── Configuracion ──────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
INSTAGRAM_USER = os.environ.get("INSTAGRAM_USERNAME")
INSTAGRAM_PASS = os.environ.get("INSTAGRAM_PASSWORD")
REPO_ROOT      = Path("C:/techpulse-daily")
GITHUB_URL     = "github.com/Mokius/atomtech-daily"
TODAY          = date.today().isoformat()

BRAND_COLOR = (0, 210, 255)
WHITE       = (255, 255, 255)
LIGHT_BLUE  = (180, 225, 255)
FONT_BOLD   = "C:/Windows/Fonts/arialbd.ttf"
FONT_REG    = "C:/Windows/Fonts/arial.ttf"

# ── Parsers ────────────────────────────────────────────────────────────────────

def parse_social_posts(issue_dir: Path) -> list:
    text   = (issue_dir / "social-posts.md").read_text(encoding="utf-8")
    blocks = re.split(r"\n---\n", text)
    stories = []
    for block in blocks:
        if "## " not in block or "Hook:" not in block:
            continue
        num     = re.search(r"## (\d+) ·", block)
        title   = re.search(r"## \d+ · (.+)", block)
        hook    = re.search(r"\*\*Hook:\*\*\s*(.+)", block)
        tags    = re.search(r"\*\*Hashtags:\*\*\s*(.+)", block)
        if not (num and title and hook):
            continue
        stories.append({
            "number":   int(num.group(1)),
            "headline": title.group(1).strip(),
            "hook":     hook.group(1).strip(),
            "hashtags": tags.group(1).strip() if tags else "#AtomTechDaily",
        })
    return sorted(stories, key=lambda x: x["number"])


def parse_sources(issue_dir: Path) -> list:
    text    = (issue_dir / "sources.md").read_text(encoding="utf-8")
    domains = re.findall(r"\|\s*([a-z0-9\-]+\.[a-z]{2,})\s*\|", text)
    seen, unique = set(), []
    for d in domains:
        if d not in seen and "domain" not in d.lower():
            seen.add(d); unique.append(d)
    return unique

def parse_digest(issue_dir: Path) -> dict:
    text   = (issue_dir / "digest.md").read_text(encoding="utf-8")
    result = {}
    for line in text.splitlines():
        m = re.match(r"\|\s*(\d+)\s*\|.*?\|\s*[🔴🟡🟢]\s*\w+\s*\|\s*(.+?)\s*\|", line)
        if m:
            result[int(m.group(1))] = m.group(2).strip()
    return result


# ── Generacion de imagen ───────────────────────────────────────────────────────

def generate_dalle_image(client: OpenAI, headline: str) -> Image.Image:
    """Llama a DALL-E 3 y devuelve imagen PIL 1080x1080."""
    prompt = (
        f"Futuristic tech news illustration about: '{headline}'. "
        "Dark space-like background, deep blue and cyan neon accents, "
        "abstract digital shapes, cinematic lighting, ultra high quality. "
        "Absolutely NO text, NO letters, NO words anywhere in the image."
    )
    resp    = client.images.generate(model="dall-e-3", prompt=prompt,
                                     size="1024x1024", quality="standard", n=1)
    data    = requests.get(resp.data[0].url, timeout=30).content
    img     = Image.open(BytesIO(data)).convert("RGBA")
    return img.resize((1080, 1080), Image.LANCZOS)

# ── Composicion de texto ───────────────────────────────────────────────────────

def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def compose_image(base: Image.Image, headline: str, hook: str) -> Image.Image:
    """Superpone branding, titular y hook sobre la imagen."""
    img  = base.copy().convert("RGBA")
    W, H = img.size   # 1080 x 1080
    ov   = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d    = ImageDraw.Draw(ov)

    # Gradiente oscuro en mitad inferior
    for y in range(H // 2, H):
        alpha = int(215 * (y - H // 2) / (H // 2))
        d.rectangle([(0, y), (W, y + 1)], fill=(8, 8, 20, alpha))

    # Barra superior de marca
    d.rectangle([(0, 0), (W, 76)], fill=(8, 8, 20, 210))
    d.text((24, 18), "⚡ ATOMTECH DAILY",
           font=load_font(FONT_BOLD, 34), fill=BRAND_COLOR)

    # Linea separadora cyan bajo la barra
    d.rectangle([(0, 76), (W, 80)], fill=(*BRAND_COLOR, 180))

    # Headline (texto grande)
    fh   = load_font(FONT_BOLD, 52)
    lines = textwrap.wrap(headline, width=26)
    y    = H - 310
    for line in lines[:3]:          # max 3 lineas
        d.text((38, y), line, font=fh, fill=WHITE)
        y += 62

    # Hook (texto secundario)
    fk   = load_font(FONT_REG, 30)
    for line in textwrap.wrap(hook, width=44)[:2]:
        d.text((38, y + 10), line, font=fk, fill=LIGHT_BLUE)
        y += 38

    # URL de GitHub en la parte inferior
    fs   = load_font(FONT_REG, 22)
    d.text((38, H - 38), f"🔗 {GITHUB_URL}", font=fs, fill=BRAND_COLOR)

    return Image.alpha_composite(img, ov).convert("RGB")


# ── Caption ────────────────────────────────────────────────────────────────────

def build_caption(story: dict, summary: str, domains: list) -> str:
    sources = "\n".join(f"• {d}" for d in domains[:8])
    return (
        f"{story['hook']}\n\n"
        f"{summary}\n\n"
        f"🔗 Newsletter completo: {GITHUB_URL}\n"
        f"📰 Fuentes de hoy:\n{sources}\n\n"
        f"{story['hashtags']} #AtomTechDaily"
    )

# ── Login Instagram ─────────────────────────────────────────────────────────────

def ig_login() -> Client:
    cl           = Client()
    session_file = REPO_ROOT / "ig_session.json"
    if session_file.exists():
        cl.load_settings(str(session_file))
    cl.login(INSTAGRAM_USER, INSTAGRAM_PASS)
    cl.dump_settings(str(session_file))
    print("   ✅ Login correcto en @atomtech_daily")
    return cl

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print(f"\n⚡ AtomTech Daily — Instagram Poster · {TODAY}")
    print("=" * 52)

    issue_dir  = REPO_ROOT / "issues" / TODAY
    output_dir = issue_dir / "instagram"
    output_dir.mkdir(exist_ok=True)

    if not issue_dir.exists():
        print(f"❌ No existe issue para hoy: {issue_dir}")
        return

    # Leer archivos del dia
    print("\n📂 Leyendo archivos del issue...")
    stories   = parse_social_posts(issue_dir)
    domains   = parse_sources(issue_dir)
    summaries = parse_digest(issue_dir)
    print(f"   {len(stories)} historias · {len(domains)} fuentes")

    # Clientes
    oai = OpenAI(api_key=OPENAI_API_KEY)
    print("\n📱 Iniciando sesion en Instagram...")
    ig  = ig_login()

    # Procesar cada historia
    for story in stories:
        n        = story["number"]
        img_path = output_dir / f"{n:02d}.jpg"

        print(f"\n[{n:02d}/20] {story['headline'][:55]}...")

        # 1. Imagen — reutiliza si ya existe (util si el script se interrumpe)
        if img_path.exists():
            print("  ♻️  Imagen ya generada, reutilizando.")
            base = Image.open(img_path).convert("RGBA").resize((1080, 1080))
        else:
            print("  🎨 Generando imagen con DALL-E 3...")
            base = generate_dalle_image(oai, story["headline"])

        # 2. Componer texto sobre la imagen
        final = compose_image(base, story["headline"], story["hook"])
        final.save(str(img_path), "JPEG", quality=95)
        print(f"  💾 Guardada: {img_path.name}")

        # 3. Caption
        summary = summaries.get(n, story["hook"])
        caption = build_caption(story, summary, domains)

        # 4. Publicar
        print("  📸 Publicando en Instagram...")
        ig.photo_upload(str(img_path), caption=caption)
        print("  ✅ Publicado.")

        # Pausa entre posts (evita rate limits de Instagram)
        if n < len(stories):
            print("  ⏳ Esperando 45s...")
            time.sleep(45)

    print(f"\n🎉 Los {len(stories)} posts se han publicado en @atomtech_daily!")
    print(f"   Imagenes en: {output_dir}")

if __name__ == "__main__":
    main()
