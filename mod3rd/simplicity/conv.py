# https://www.w3.org/International/questions/qa-escapes
def simple_esc_html(s):
    html = {
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot",
        "'": "&apos;",
        "&": "&amp;",
    }
    for e, r in html.items():
        s = s.replace(e, r)
    return s
