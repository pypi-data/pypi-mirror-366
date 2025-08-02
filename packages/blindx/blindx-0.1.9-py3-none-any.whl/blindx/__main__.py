import re
import sys
import html
import base64
import urllib.parse
import requests
import argparse

BANNER = r'''   ___      __    _               __   _  __  
  / _ )    / /   (_)   ___    ___/ /  | |/_/  
 / _  |   / /   / /   / _ \  / _  /   _>  <   
/____/   /_/   /_/   /_//_/  \,_/    /_/|_|      

     ----- blindx V1.0 by progprnv | pr0gx | Pranav Jayan 
'''

def show_usage():
    print("""[36mUsage:[0m
  [32mblindx[0m             Launch interactive Blind XSS testing mode
  [32mblindx -h / --help[0m Show this help message

[36mWorkflow:[0m
  1. Paste a raw POST request (copied from BurpSuite)
  2. Select value(s) in the body to be replaced with payload
  3. Enter your payload
  4. Choose encoding (HTML, URL, JS, Unicode, Base64)
  5. Add optional headers with {{payload}} placeholder
  6. blindx will send all encoded payloads and show response status

[33m⚠️  Use this tool only on targets where you have explicit permission.[0m
[31m❌  Unauthorized testing may be illegal and unethical.[0m
[32m✅  For bug bounty, follow program scopes carefully.[0m
""")

def html_encode(s, times):
    for _ in range(times):
        s = html.escape(s)
    return s

def url_encode(s, times):
    for _ in range(times):
        s = urllib.parse.quote(s)
    return s

def js_escape(s, times):
    for _ in range(times):
        s = s.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
    return s

def unicode_escape(s, times):
    for _ in range(times):
        s = ''.join(f"\\u{ord(c):04x}" for c in s)
    return s

def base64_encode(s, times):
    for _ in range(times):
        s = base64.b64encode(s.encode()).decode()
    return s

def parse_raw_request(raw):
    parts = raw.split('\r\n\r\n', 1)
    header_lines = parts[0].split('\r\n')
    body = parts[1] if len(parts) > 1 else ''
    method, path, _ = header_lines[0].split()

    headers = {}
    for line in header_lines[1:]:
        k, v = line.split(':', 1)
        headers[k.strip()] = v.strip()

    host = headers.get('Host')
    url = f"http://{host}{path}" if not path.startswith('http') else path
    return method, url, headers, body

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    args = parser.parse_args()

    if args.help:
        print(BANNER)
        show_usage()
        sys.exit(0)

    print(BANNER)
    print('\u001b[35m\nPaste your raw POST (with CRLF) and end with an empty line:\u001b[0m')
    lines = []
    while True:
        line = sys.stdin.readline()
        if line.strip() == '':
            break
        lines.append(line.rstrip('\n'))
    raw = '\r\n'.join(lines)

    try:
        method, url, headers, body = parse_raw_request(raw)
    except Exception as e:
        print(f"\u001b[31m[!] Failed to parse request: {e}\u001b[0m")
        sys.exit(1)

    values_to_replace = []
    while True:
        val = input('\u001b[33mEnter the exact value to replace with payload (e.g., \"hi\"): \u001b[0m').strip()
        values_to_replace.append(val)
        if input('\u001b[36mAdd another value to replace? (Y/N): \u001b[0m').lower() != 'y':
            break

    payload = input('\u001b[33mEnter your payload: \u001b[0m')

    options = [f"{i+1}) {name}" for i, name in enumerate([
        'HTML encode x1','HTML encode x2','HTML encode x3',
        'URL encode x1','URL encode x2','URL encode x3',
        'JS escape x1','JS escape x2','JS escape x3',
        'Unicode escape x1','Unicode escape x2','Unicode escape x3',
        'Base64 encode x1','Base64 encode x2','Base64 encode x3',
        'All variants','No encode'
    ])]
    print('\n'.join([f'\u001b[32m{o}\u001b[0m' for o in options]))
    choice = int(input('\u001b[35mSelect option number (1-17): \u001b[0m'))

    variants = []
    if 1 <= choice <= 15:
        funcs = [html_encode, html_encode, html_encode,
                 url_encode, url_encode, url_encode,
                 js_escape, js_escape, js_escape,
                 unicode_escape, unicode_escape, unicode_escape,
                 base64_encode, base64_encode, base64_encode]
        variants.append(funcs[choice-1](payload, ((choice-1)%3)+1))
    elif choice == 16:
        for i, fn in enumerate([html_encode]*3 + [url_encode]*3 + [js_escape]*3 + [unicode_escape]*3 + [base64_encode]*3):
            variants.append(fn(payload, (i%3)+1))
    else:
        variants.append(payload)

    add_headers = {}
    if input('\u001b[33mInject headers? (Y/N): \u001b[0m').lower() == 'y':
        while True:
            hn = input('Header name: ').strip()
            hv = input('Header value (use {{payload}}): ').strip()
            add_headers[hn] = hv
            if input('\u001b[36mAdd another header? (Y/N): \u001b[0m').lower() != 'y':
                break

    session = requests.Session()
    for i, var in enumerate(variants, start=1):
        mod_body = body
        for old_val in values_to_replace:
            mod_body = mod_body.replace(old_val, var)

        h = headers.copy()
        for hn, hv in add_headers.items():
            h[hn] = hv.replace('{{payload}}', var)

        try:
            print(f"\u001b[34m[{i}] Sending payload: {var[:30]}...\u001b[0m")
            resp = session.request(method, url, headers=h, data=mod_body, timeout=10)
            print(f"\u001b[32m[{i}] {url} -> {resp.status_code}\u001b[0m")
        except requests.exceptions.RequestException as e:
            print(f"\u001b[31m[{i}] Request failed: {e}\u001b[0m")

if __name__ == '__main__':
    main()

