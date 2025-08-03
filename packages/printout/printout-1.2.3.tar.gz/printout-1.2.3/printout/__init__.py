from .printout import printout

# Make the package callable
def __call__(*args, **kwargs):
    return printout(*args, **kwargs)

# Expose the function so "from printout import printLog" also works
__all__ = ["printout"]