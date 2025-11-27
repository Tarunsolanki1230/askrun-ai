import importlib
m = importlib.import_module('askrun_gpt4all')
print('OK:', getattr(m, '_HAS_TK', None))
