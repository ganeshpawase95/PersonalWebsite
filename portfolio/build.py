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
NAV = ["Home", "About", "Skills", "Projects", "Experience", "Contact"]
# TODO(owner): Add Real Estate CRM and ERPNext case studies once the contribution,
# stack, approved screenshots and outcomes can be documented.
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
    return f'''<a class="project" href="{base}projects/{slug}/index.html">
      <div class="cover {slug}"><img src="{base}assets/images/previews/{project["image"]}.jpg" loading="lazy" alt=""></div>
      <div class="project-info"><span class="category">{escape(project["category"])}</span><h3>{name}</h3>
      <p>{escape(project["desc"])}</p>{tags(project["tags"])}</div></a>'''


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
        links.append(f'<a href="{home}#{name.lower()}"{current}>{name}</a>')
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
    skills, roles = records("skills"), records("roles")
    toolkit = "".join(
        f'<article class="skill"><div class="skill-icon">{icon(glyph)}</div>'
        f'<h3>{escape(name)}</h3><p>{escape(detail)}</p></article>'
        for glyph, name, detail in skills
    )
    home = Template((SOURCE / "home.html").read_text(encoding="utf-8")).substitute(
        project_count=len(projects), featured="".join(card(p, "") for p in projects[:3]),
        skills=toolkit, roles=timeline(roles[:2]),
        **{name: icon(name) for name in ("grid", "github", "pin", "angular", "db", "box",
                                          "briefcase", "layers", "file", "mail", "linkedin")}
    )
    page("index.html", "Ganesh Pawase | Full-Stack Developer & ERPNext Consultant",
         "Ganesh Pawase builds web applications, REST APIs and ERPNext solutions in Navi Mumbai. Explore his projects, skills and experience.", home, "Home")
    gallery = '<div class="project-grid">' + "".join(card(p, "../") for p in projects) + "</div>"
    page("projects/index.html", "Projects | Ganesh Pawase", "Software projects by Ganesh Pawase.",
         subpage("Portfolio", "All projects", gallery), "Projects")
    for project in projects:
        name = escape(project["name"])
        preview = f'assets/images/previews/{project["image"]}.jpg'
        body = f'''<div class="detail"><p class="page-intro">{escape(project["desc"])}</p>
        {tags(project["tags"])}<img src="../../{preview}" alt="{name} interface from the original portfolio">
        <h2>Project overview</h2><p>{escape(project["overview"])}</p></div>'''
        page(f'projects/{project["slug"]}/index.html', f'{project["name"]} | Ganesh Pawase',
             project["desc"], subpage(escape(project["category"]), name, body, "../index.html", "All projects"),
             "Projects", preview)
    page("experience/index.html", "Experience | Ganesh Pawase", "Ganesh Pawase’s software development experience.",
         subpage("Experience", "Career timeline", '<div class="timeline">' + timeline(roles) + "</div>"), "Experience")
    page("404.html", "Page not found | Ganesh Pawase", "Return to Ganesh Pawase’s portfolio.",
         subpage("404", "Page not found", '<p class="page-intro">You can explore my work from the homepage.</p>',
                 "/index.html", "Return home"), "")


if __name__ == "__main__":
    build()
