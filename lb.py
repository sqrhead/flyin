from typing import Optional, Any
import re

if __name__ == '__main__':
    # .*+[]\d\s\w\S
    pattern = r'\d+'
    cmp = '12'
    if re.match(pattern, cmp):
        print('[OK]')
