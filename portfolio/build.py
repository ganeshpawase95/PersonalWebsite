"""Generate the dependency-free portfolio. Run python portfolio/build.py after content edits."""
from html import escape
import json
import os
from pathlib import Path
from string import Template

SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parent
LAYOUT = Template((SOURCE / "layout.html").read_text(encoding="utf-8"))
SYMBOLS = (ROOT / "assets/images/icons.svg").read_text(encoding="utf-8").replace(
    "<svg ", '<svg width="0" height="0" style="position:absolute" aria-hidden="true" ', 1)
NAV = ["Home", "About", "Skills", "Projects", "Experience", "Blogs", "Contact"]
SITE_URL = os.environ.get("URL", "https://ganeshpawaseportfolio.netlify.app").rstrip("/")


def records(name):
    return json.loads((SOURCE / f"{name}.json").read_text(encoding="utf-8"))


def icon(name):
    return f'<svg class="icon i-{name}" aria-hidden="true"><use href="#{name}"/></svg>'


def tags(values):
    return '<div class="tags">' + "".join(f'<span>{escape(value)}</span>' for value in values) + "</div>"


def card(project, base):
    slug = project["slug"]
    name = escape(project["name"])
    return f'''<article class="project" data-category="{escape(project.get("group", "Earlier"))}">
      {project_art(project, base)}
      <div class="project-info"><span class="category">{escape(project["category"])}</span>
      <h3><a href="{base}projects/{slug}/index.html">{name}</a></h3>
      <p>{escape(project["desc"])}</p>{tags(project["tags"])}</div></article>'''


def project_art(project, base):
    if "illustration" in project:
        return f'''<div class="concept cover"><img loading="lazy" width="450" height="245"
          src="{base}assets/images/concepts/{project["illustration"]}.svg" alt="">
          <small>Concept illustration</small></div>'''
    return f'''<div class="cover {project["slug"]}"><img loading="lazy"
      src="{base}assets/images/previews/{project["image"]}.jpg" alt="{escape(project["name"])} interface"></div>'''


def gallery(projects, base):
    groups = ["All", *dict.fromkeys(p.get("group", "Earlier") for p in projects)]
    buttons = "".join(
        f'<button type="button" data-filter="{group}" aria-pressed="{str(group == "All").lower()}">{group}</button>'
        for group in groups
    )
    return (f'<div class="gallery"><div class="filters" role="group" aria-label="Filter projects" hidden>{buttons}</div>'
            '<span class="sr-only" role="status"></span><div class="project-grid">'
            + "".join(card(p, base) for p in projects) + "</div></div>")


def blog_cards(articles, heading="h3"):
    cards = []
    for article in articles:
        title = escape(article["title"])
        if article["url"]:
            action = f'<a class="text-link" href="{escape(article["url"])}" aria-label="Read {title} on DEV">Read on DEV</a>'
        else:
            action = '<span class="article-status">Article link pending</span>'
        cards.append(f'''<article class="article-card"><div class="article-topic">{icon(article["icon"])}
          {escape(article["topic"])}</div><{heading}>{title}</{heading}><p>{escape(article["summary"])}</p>{action}</article>''')
    return '<div class="blog-grid">' + "".join(cards) + "</div>"


def skill_icon(glyph):
    if glyph in {"erpnext", "frappe", "webrtc"}:
        return f'<img src="assets/images/brands/{glyph}.svg" width="28" height="28" alt="" loading="lazy">'
    return icon(glyph)


def timeline(roles):
    return "".join(
        f'<article class="job"><span class="job-date">{escape(date)}</span>'
        f'<h3>{escape(title)}</h3><p>{escape(company)}</p></article>'
        for title, company, date in roles
    )


def page(path, title, description, content, active, preview="assets/images/social-preview.jpg"):
    target = ROOT / path
    base = "/" if path == "404.html" else "../" * (len(Path(path).parts) - 1)
    home = "" if path == "index.html" else base + "index.html"
    links = []
    for name in NAV:
        current = ' aria-current="location"' if name == active else ""
        href = f"{home}#{name.lower()}"
        if name == "Blogs":
            href = base + "blogs/index.html"
            current = ' aria-current="page"' if name == active else ""
        links.append(f'<a href="{href}"{current}>{name}</a>')
    social = f'<meta property="og:image" content="{base}{preview}">'
    if SITE_URL:
        url = escape(SITE_URL + "/" + path.removesuffix("index.html"), quote=True)
        image = escape(SITE_URL + "/" + preview, quote=True)
        social = (f'<link rel="canonical" href="{url}"><meta property="og:url" content="{url}">'
                  f'<meta property="og:image" content="{image}"><meta name="twitter:card" content="summary_large_image">')
    target.parent.mkdir(parents=True, exist_ok=True)
    html = LAYOUT.substitute(
        base=base, home=home, title=escape(title), description=escape(description),
        social=social, content=content, navigation="".join(links), symbols=SYMBOLS,
        **{name: icon(name) for name in ("mail", "sun", "moon", "menu", "close")}
    )
    target.write_text(html, encoding="utf-8", newline="\n")


def subpage(label, title, body, back="../index.html#home", back_label="Home"):
    return f'''<div class="shell section subpage"><a class="text-link" href="{back}">{back_label}</a>
    <p class="eyebrow"><span class="rule"></span>{label}</p><h1 class="page-title">{title}<span class="accent">.</span></h1>{body}</div>'''


def build():
    projects = json.loads((ROOT / "projects/projects.json").read_text(encoding="utf-8"))
    skills, roles, articles = records("skills"), records("roles"), records("blogs")
    toolkit = "".join(
        f'<article class="skill"><div class="skill-icon">{skill_icon(glyph)}</div>'
        f'<h3>{escape(name)}</h3><p>{escape(detail)}</p></article>'
        for glyph, name, detail in skills
    )
    home = Template((SOURCE / "home.html").read_text(encoding="utf-8")).substitute(
        project_count=len(projects), gallery=gallery(projects, ""), blogs=blog_cards(articles),
        skills=toolkit, roles=timeline(roles),
        **{name: icon(name) for name in ("grid", "github", "pin", "angular", "db", "box",
                                          "briefcase", "layers", "file", "mail", "linkedin")}
    )
    page("index.html", "Ganesh Pawase | Full-Stack Developer & ERPNext Consultant",
         "Ganesh Pawase builds web applications, REST APIs and ERPNext solutions in Navi Mumbai. Explore his projects, skills and experience.", home, "Home")
    page("projects/index.html", "Projects | Ganesh Pawase", "Software projects by Ganesh Pawase.",
         subpage("Portfolio", "All projects", gallery(projects, "../")), "Projects")
    for project in projects:
        name = escape(project["name"])
        preview = (f'assets/images/previews/{project["image"]}.jpg' if "image" in project
                   else "assets/images/social-preview.jpg")
        artwork = (f'<img src="../../{preview}" alt="{name} interface from the original portfolio">'
                   if "image" in project else project_art(project, "../../"))
        body = f'''<div class="detail"><p class="page-intro">{escape(project["desc"])}</p>
        {tags(project["tags"])}{artwork}
        <h2>Project overview</h2><p>{escape(project["overview"])}</p></div>'''
        page(f'projects/{project["slug"]}/index.html', f'{project["name"]} | Ganesh Pawase',
             project["desc"], subpage(escape(project["category"]), name, body, "../index.html", "All projects"),
             "Projects", preview)
    page("blogs/index.html", "Blogs | Ganesh Pawase", "Technical notes by Ganesh Pawase on JavaScript and browser graphics.",
         subpage("Writing", "Technical notes", blog_cards(articles, "h2")), "Blogs")
    page("experience/index.html", "Experience | Ganesh Pawase", "Ganesh Pawase’s software development experience.",
         subpage("Experience", "Career timeline", '<div class="timeline">' + timeline(roles) + "</div>"), "Experience")
    page("404.html", "Page not found | Ganesh Pawase", "Return to Ganesh Pawase’s portfolio.",
         subpage("404", "Page not found", '<p class="page-intro">You can explore my work from the homepage.</p>',
                 "/index.html", "Return home"), "")


if __name__ == "__main__":
    build()
