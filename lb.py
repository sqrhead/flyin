from typing import Optional, Any
import re

if __name__ == '__main__':
    # .*+[]\d\s\w\S
    pattern = r'\w+=\w+'
    stack = '[color=green]'

    result = re.findall(pattern, stack)
    print(result)
