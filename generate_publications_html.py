import pandas as pd
import calendar
import os

df = pd.read_csv("publications.csv", encoding="latin1")
df = df.sort_values(by=['year', 'month', 'day'], ascending=[False, False, False])

journals = df[df['type'] == 'Journal']
conferences = df[df['type'] == 'Conference']

def format_date(row):
    month_abbr = [""] + [calendar.month_abbr[i] + "." for i in range(1, 13)]
    if pd.notnull(row[5]) and pd.notnull(row[6]):
        return f"{month_abbr[int(row[5])]} {int(row[6])}, {int(row[7])}"
    elif pd.notnull(row[5]):
        return f"{month_abbr[int(row[5])]} {int(row[7])}"
    elif pd.notnull(row[7]):
        return f"{int(row[7])}"
    else:
        return ""

def render_pub(row, display_idx):
    date_str = format_date(row)

    authors = row[2]
    if pd.notnull(authors):
        authors = authors.replace("A. Chhabra", "<strong>A. Chhabra</strong>")
    else:
        authors = ""

    title = row[3]
    if "(IN REVIEW)" in title:
        title = title.replace("(IN REVIEW)", '<span style="color:blue; font-weight:500;">(IN REVIEW)</span>')

    title = f'<span style="color:maroon; font-weight:500;">{title}</span>'



    view_paper_btn = f'<a href="{row[9]}" target="_blank" class="btn btn-outline-primary btn-sm me-2">View Paper</a>' \
        if pd.notnull(row[9]) and row[9].strip() != "" else ""

    if pd.notnull(row[10]) and row[10].strip() != "":
        try:
            bibtex_data = open(row[10]).read()
            bibtex_btn = f'<button class="btn btn-outline-dark btn-sm" onclick="toggleBibtex(\'bibtex{row[0]}\')">BibTeX</button>'
        except FileNotFoundError:
            bibtex_btn = ""
            bibtex_data = ""
    else:
        bibtex_btn = ""
        bibtex_data = ""

    remarks_str = f'<p class="text-primary medium fst-italic mb-0">🏆 {row[11]}</p>' if pd.notnull(row[11]) and row[11].strip() != "" else ""

    return f"""
<div class="mb-4">
  <p>
    {display_idx}. {authors}<br>
    {title}<br>
    <i>{row[4]}</i>, {date_str}.
  </p>
  {f'<p class="text-muted">{row[8]}</p>' if pd.notnull(row[8]) and row[8].strip() != "" else ""}
  <div class="mb-2">
    {view_paper_btn}
    {bibtex_btn}
  </div>
  {remarks_str}
  <pre id="bibtex{row[0]}" style="display:none; background:#f8f9fa; padding:0.5rem; border-radius:5px;">
{bibtex_data}
  </pre>
</div>
"""

journals_html = "\n".join(render_pub(row, idx) for idx, row in enumerate(journals.itertuples(index=False, name=None), 1))
conferences_html = "\n".join(render_pub(row, idx) for idx, row in enumerate(conferences.itertuples(index=False, name=None), 1))

with open("publications.html", "r", encoding="utf-8") as f:
    html = f.read()

def replace_between(text, start_marker, end_marker, replacement):
    start = text.find(start_marker)
    end = text.find(end_marker)
    if start == -1 or end == -1:
        raise ValueError(f"Markers {start_marker} or {end_marker} not found.")
    return text[:start + len(start_marker)] + "\n" + replacement + "\n" + text[end:]

html = replace_between(html, "<!-- JOURNAL START -->", "<!-- JOURNAL END -->", journals_html)
html = replace_between(html, "<!-- CONF START -->", "<!-- CONF END -->", conferences_html)

with open("publications.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ publications.html updated successfully.")
