import os

from pyme.registry import builtin

builtin("file-exists?")(os.path.exists)

builtin("mkdir")(os.mkdir)
