import py_compile, glob, sys
files = glob.glob('**/*.py', recursive=True)
errs = 0
for f in files:
    try:
        py_compile.compile(f, doraise=True)
    except Exception as e:
        print(f'ERROR compiling {f}: {e}')
        errs += 1
print('Done. Failures:', errs)
if errs:
    sys.exit(1)
else:
    sys.exit(0)
