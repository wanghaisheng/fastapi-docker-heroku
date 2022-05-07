from pywebio.output import put_html
from pywebio.platform import seo
from pywebio.platform.page import config
from pywebio.session import run_js
from .constants import GA_JS_CODE, GA_JS_FILE,SEO_DESCRIPTION, SEO_TITLE
from .constants import FOOTER, LANDING_PAGE_HEADING


@config(theme="minty", title=SEO_TITLE, description=SEO_DESCRIPTION)
def t() -> None:
    # Page heading
    put_html(LANDING_PAGE_HEADING)
    lang = 'English'
    if lang == 'English':
        LANDING_PAGE_DESCRIPTION = LANDING_PAGE_DESCRIPTION_English
    session.run_js(
        'WebIO._state.CurrentSession.on_session_close(()=>{setTimeout(()=>location.reload(), 40000})')
    session.run_js(FOOTER
)