from .brnldist import brnldist

class brnldistWrapper:
    def __call__(self, *args, **kwargs):
        return brnldist(*args, **kwargs)

# Now, when user writes: import brnldist
# brnldist(...) works because licome is an instance of brnldistWrapper
import sys
sys.modules[__name__] = brnldistWrapper()