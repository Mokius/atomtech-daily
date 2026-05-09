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

# ── Estilo base — aplica a todas las imagenes ──────────────────────────────────
# Garantiza consistencia visual entre los 20 posts del dia
STYLE_BASE = (
    "Professional tech news photography, cinematic lighting, "
    "sharp focus, high contrast, slightly cool color grading, 4K photorealistic. "
    "The bottom 40% of the image must be significantly darker "
    "so that white text remains perfectly legible on top of it. "
    "No text, no letters, no words, no watermarks anywhere in the image."
)

# ── Templates visuales por categoria ──────────────────────────────────────────
CATEGORY_TEMPLATES = {

    "ai": (
        "Close-up of a glowing AI chip (NVIDIA H100 or similar) with blue and cyan "
        "light trails, neural network visualization overlaid as a subtle glow, "
        "modern server rack background softly blurred. "
        "Photorealistic digital art meets real product photography. "
        "Story: {headline}."
    ),

    "research": (
        "University research lab: scientists in front of large monitors showing "
        "mathematical models or neural network diagrams, clean academic environment, "
        "whiteboards with equations softly visible in background. "
        "Story: {headline}."
    ),

    "devtools": (
        "Developer workstation with ultrawide monitors showing VS Code or a terminal "
        "in dark theme, mechanical keyboard, subtle GitHub or tool logo softly reflected "
        "on the screen, professional clean desk, moody ambient lighting. "
        "Story: {headline}."
    ),

    "security": (
        "Cybersecurity dramatic visual: a glowing digital padlock or broken shield "
        "with red and blue data streams, abstract network nodes in the background, "
        "ominous dark atmosphere suggesting a breach or vulnerability. "
        "Story: {headline}."
    ),

    "cloud": (
        "Hyperscale data center interior: rows of servers with blue LED lighting, "
        "cable trays, shallow depth of field, slight fog effect between aisles, "
        "giving a sense of massive scale and precision infrastructure. "
        "Story: {headline}."
    ),

    "hardware": (
        "Extreme macro photography of a semiconductor wafer — intricate circuit "
        "patterns, metallic and iridescent colors, cleanroom aesthetic. "
        "Or: an NVIDIA GPU PCB on a dark reflective surface, dramatic side lighting. "
        "Story: {headline}."
    ),

    "quantum": (
        "Abstract quantum physics visualization: glowing entangled particles, "
        "interference patterns in blue and white light, quantum computer hardware "
        "with superconducting qubits visible, cold blue laboratory atmosphere. "
        "Story: {headline}."
    ),

    "medical": (
        "Medical research laboratory: close-up of a blood sample under a high-tech "
        "microscope, blue and white lab lighting, researcher in gloves holding a vial, "
        "scientific precision and cleanliness. "
        "Story: {headline}."
    ),

    "energy": (
        "Clean energy concept: sunlight refracting through a transparent surface "
        "onto scientific equipment, solar panels or photocatalytic reactor in a lab, "
        "warm golden light contrasting with cool scientific environment. "
        "Story: {headline}."
    ),

    "robotics": (
        "Modern humanoid robot or advanced robotic arm in motion, sharp photorealistic "
        "render, industrial or research lab setting, dramatic lighting with blue "
        "and white highlights, dynamic pose suggesting intelligence and precision. "
        "Story: {headline}."
    ),

    "aerospace": (
        "Small autonomous spacecraft against the dark of space, Earth curvature "
        "visible below, stars and orbital debris in background, military/defense "
        "aesthetic, dramatic lighting from the sun catching metallic surfaces. "
        "Story: {headline}."
    ),

    "startups": (
        "Modern tech startup or VC office: glass-walled meeting room, "
        "whiteboards covered in startup diagrams, city skyline visible through "
        "floor-to-ceiling windows, professional business energy, warm and ambitious. "
        "Story: {headline}."
    ),

    "default": (
        "Futuristic technology concept: blue and cyan neon light trails over "
        "abstract digital shapes, professional editorial photography style, "
        "cinematic depth. Story: {headline}."
    ),
}


def build_dalle_prompt(headline: str, category: str) -> str:
    template = CATEGORY_TEMPLATES.get(category, CATEGORY_TEMPLATES["default"])
    return template.format(headline=headline) + " " + STYLE_BASE


def detect_category(headline: str, hashtags: str) -> str:
    """
    Infiere categoria visual a partir del headline.
    Orden: mas especifico primero, mas general al final.
    """
    h = headline.lower()

    # Espacial / defensa — muy especifico
    if any(w in h for w in ["space", "spacecraft", "orbital", "satellite", "anomaly", "missile"]):
        return "aerospace"

    # Robotica
    if any(w in h for w in ["robot", "embodied", "newton physics", "manipulation", "agibot", "humanoid"]):
        return "robotics"

    # Quantum — antes de "science" generica
    if any(w in h for w in ["quantum", "quadsqueez", "qubit", "entangle"]):
        return "quantum"

    # Medico / biologia — antes de "science" generica
    if any(w in h for w in ["blood test", "depression", "immune", "cancer", "medical", "clinical"]):
        return "medical"

    # Energia limpia — antes de "science" generica
    if any(w in h for w in ["hydrogen", "solar", "sunlight", "plastic", "clean energy", "photocatal"]):
        return "energy"

    # Ciencia generica
    if any(w in h for w in ["science", "discovery", "biology", "chemistry", "physics", "breakthrough"]):
        return "research"

    # Seguridad — antes de "devtools"
    if any(w in h for w in ["cve-", "zero-day", "exploit", "cisa", "vulnerability", "patch tuesday",
                              "ransomware", "breach", "malware"]):
        return "security"

    # Semiconductor / hardware — antes de "ai"
    if any(w in h for w in ["semiconductor", "chip", "wafer", "tsmc", "gpu", "npu", "silicon", "arm chip"]):
        return "hardware"

    # Dev tools — antes de "ai" (github copilot es devtools, no ai)
    if any(w in h for w in ["github", "copilot", "vscode", "codeql", "warp terminal",
                              "git ", "dev tool", "ide ", "cli "]):
        return "devtools"

    # Cloud / infra
    if any(w in h for w in ["kubernetes", "vmware", "cloud foundation", "data center",
                              "vultr", "suse", "supermicro", "infrastructure"]):
        return "cloud"

    # Startups / funding — muy especifico
    if any(w in h for w in ["raises ", "series ", "valuation", "funding", "venture", "billion"]):
        return "startups"

    # AI — amplio, al final
    if any(w in h for w in ["ai ", "llm", "model", "grok", "gemma", "deepseek", "gpt", "claude",
                              "watsonx", "ibm think", "machine learning", "neural", "agentic"]):
        return "ai"

    # Research academica
    if any(w in h for w in ["stanford", "arxiv", "paper", "manifold", "university"]):
        return "research"

    return "default"


# ── Parsers ────────────────────────────────────────────────────────────────────

def parse_social_posts(issue_dir: Path) -> list:
    text   = (issue_dir / "social-posts.md").read_text(encoding="utf-8")
    blocks = re.split(r"\n---\n", text)
    stories = []
    for block in blocks:
        if "## " not in block or "Hook:" not in block:
            continue
        num   = re.search(r"## (\d+) ·", block)
        title = re.search(r"## \d+ · (.+)", block)
        hook  = re.search(r"\*\*Hook:\*\*\s*(.+)", block)
        tags  = re.search(r"\*\*Hashtags:\*\*\s*(.+)", block)
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


# ── Generacion de imagen ────────────────────────────────────────────────────────

def generate_dalle_image(client: OpenAI, headline: str, hashtags: str) -> Image.Image:
    category = detect_category(headline, hashtags)
    prompt   = build_dalle_prompt(headline, category)
    print(f"     [{category}] prompt listo")

    resp = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    data = requests.get(resp.data[0].url, timeout=30).content
    img  = Image.open(BytesIO(data)).convert("RGBA")
    return img.resize((1080, 1080), Image.LANCZOS)


# ── Composicion de texto ────────────────────────────────────────────────────────

def load_font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def compose_image(base: Image.Image, headline: str, hook: str) -> Image.Image:
    """
    Diseno de slide para Instagram:
      ┌─────────────────────────────────────┐
      │  ⚡ ATOMTECH DAILY          [barra] │
      │  ─────────────────────────────────  │
      │                                     │
      │      [imagen DALL-E de fondo]       │
      │                                     │
      │▓▓▓▓▓▓ gradiente oscuro creciente ▓▓▓│
      │  TITULAR EN BLANCO BOLD             │
      │  hook en azul claro                 │
      │  🔗 github.com/Mokius/atomtech-daily│
      └─────────────────────────────────────┘
    """
    img  = base.copy().convert("RGBA")
    W, H = img.size   # 1080 x 1080
    ov   = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d    = ImageDraw.Draw(ov)

    # Gradiente oscuro — zona inferior 45%
    grad_start = int(H * 0.55)
    for y in range(grad_start, H):
        alpha = int(240 * (y - grad_start) / (H - grad_start))
        d.rectangle([(0, y), (W, y + 1)], fill=(5, 5, 16, alpha))

    # Barra de marca superior
    d.rectangle([(0, 0), (W, 82)], fill=(5, 5, 16, 225))
    d.rectangle([(0, 82), (W, 86)], fill=(*BRAND_COLOR, 210))
    d.text((28, 20), "⚡ ATOMTECH DAILY",
           font=load_font(FONT_BOLD, 36), fill=BRAND_COLOR)

    # Headline — con sombra para contraste sobre cualquier fondo
    fh = load_font(FONT_BOLD, 50)
    hl_y = H - 325
    for line in textwrap.wrap(headline, width=27)[:3]:
        d.text((42, hl_y + 2), line, font=fh, fill=(0, 0, 0, 210))   # sombra
        d.text((40, hl_y),     line, font=fh, fill=WHITE)
        hl_y += 62

    # Hook — subtitulo en azul claro
    fk = load_font(FONT_REG, 30)
    hk_y = hl_y + 12
    for line in textwrap.wrap(hook, width=44)[:2]:
        d.text((42, hk_y + 1), line, font=fk, fill=(0, 0, 0, 180))
        d.text((40, hk_y),     line, font=fk, fill=LIGHT_BLUE)
        hk_y += 40

    # URL GitHub al pie
    d.text((40, H - 40), f"🔗 {GITHUB_URL}",
           font=load_font(FONT_REG, 23), fill=BRAND_COLOR)

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


# ── Instagram ──────────────────────────────────────────────────────────────────

def ig_login() -> Client:
    cl           = Client()
    session_file = REPO_ROOT / "ig_session.json"
    if session_file.exists():
        cl.load_settings(str(session_file))
    cl.login(INSTAGRAM_USER, INSTAGRAM_PASS)
    cl.dump_settings(str(session_file))
    print("   ✅ Login en @atomtech_daily")
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

    print("\n📂 Leyendo archivos del issue...")
    stories   = parse_social_posts(issue_dir)
    domains   = parse_sources(issue_dir)
    summaries = parse_digest(issue_dir)
    print(f"   {len(stories)} historias · {len(domains)} fuentes")

    oai = OpenAI(api_key=OPENAI_API_KEY)
    print("\n📱 Iniciando sesion en Instagram...")
    ig  = ig_login()

    for story in stories:
        n        = story["number"]
        img_path = output_dir / f"{n:02d}.jpg"
        print(f"\n[{n:02d}/20] {story['headline'][:55]}...")

        # 1. Imagen
        if img_path.exists():
            print("  ♻️  Reutilizando imagen ya generada.")
            base = Image.open(img_path).convert("RGBA").resize((1080, 1080))
        else:
            print("  🎨 Generando imagen DALL-E 3...")
            base = generate_dalle_image(oai, story["headline"], story["hashtags"])

        # 2. Texto sobre imagen
        final = compose_image(base, story["headline"], story["hook"])
        final.save(str(img_path), "JPEG", quality=95)
        print(f"  💾 {img_path.name}")

        # 3. Publicar
        summary = summaries.get(n, story["hook"])
        caption = build_caption(story, summary, domains)
        print("  📸 Publicando...")
        ig.photo_upload(str(img_path), caption=caption)
        print("  ✅ Publicado.")

        if n < len(stories):
            print("  ⏳ 45s...")
            time.sleep(45)

    print(f"\n🎉 {len(stories)} posts publicados en @atomtech_daily!")

if __name__ == "__main__":
    main()
