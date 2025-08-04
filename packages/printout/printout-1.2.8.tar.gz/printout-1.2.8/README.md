Simple library that allows you to print message to the console and to any file you want. 
```

import printout

try:
    r = requests.get('https://httpbin.org/basic-auth/user/pass', auth=('user', 'pass'))
    r.status_code
    printout(f"{printout(r.text)}", "page_results.txt")
except Exception as ex:
    printout(f"Error: {ex}", ""error_log.txt")

```