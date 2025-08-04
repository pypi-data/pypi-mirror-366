INLINE_SCRIPT_PREFIX = "exec"
SCRIPT_PREFIX = "script"
APP_NAME = "quick_actions"

ACTION_KEYWORDS_TO_RESOLVE_RELATIVE_PATHS = ["script"]


# Launcher
DEFAULT_PROMPT = "wofi --prompt='{prompt}' --dmenu --width=70% --height=60%"

DEFAULT_PANDOC_ID_STYLE = '<span color="gray">{id}</span>'
DEFAULT_PANDOC_PREFIX_STYLE = '<sup><b>{prefix}</b><span color="#7a251f">☐☐☐☐</span></sup>'

DEFAULT_PANDOC_TAG_STYLE = '<span color="gray" style="oblique"><sub>{tag}</sub></span>'
DEFAULT_PANDOC_TAG_SEPARATOR = ' '

DEFAULT_MENU_PROMPT = "Quick Menu"


# Persistance
DEFAULT_PERSISTANCE_BACKEND = "pickle"

PICKLE_STATE_KEY_TEMPLATE = "state-{key}"
PICKLE_FRECENCY_STORE_KEY = "frecency-store"