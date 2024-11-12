import functools
import os


@functools.cache
def set_env() -> dict:
    """
    GIT_TERMINAL_PROMPT=0 disallows spurious Git https password prompts
    https://github.blog/2015-02-06-git-2-3-has-been-released/#the-credential-subsystem-is-now-friendlier-to-scripting
    """

    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env
