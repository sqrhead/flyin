import re

if __name__ == '__main__':
    regex = r'(?P<name>#\s*?.*)'

    if re.match(regex, '#ok'):
        print("\033[92m[OK]\033[0m")  # green
    else:
        print("\033[91m[OK]\033[0m")  # red