from tsal.tools.code_understanding import summarize_python
import sys

if __name__ == "__main__":
    code = sys.stdin.read()
    for name in summarize_python(code):
        print(name)
