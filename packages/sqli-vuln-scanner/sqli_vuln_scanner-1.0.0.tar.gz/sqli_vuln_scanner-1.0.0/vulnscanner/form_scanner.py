def scan_forms(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=7)
        soup = BeautifulSoup(res.text, "html.parser")
        forms = soup.find_all("form")
        vulnerable_forms = []

        for form in forms:
            action = form.get("action")
            method = form.get("method", "get").lower()
            inputs = form.find_all("input")
            data = {}
            username_field = ""
            password_field = ""
            injection_fields = []

            for inp in inputs:
                name = inp.get("name")
                typ = inp.get("type", "text")
                if not name:
                    continue
                if "user" in name.lower():
                    username_field = name
                elif "pass" in name.lower():
                    password_field = name
                else:
                    injection_fields.append(name)
                    data[name] = "test"

            full_url = urljoin(url, action)

            if username_field and password_field:
                for u, p in COMMON_CREDENTIALS:
                    data[username_field] = u
                    data[password_field] = p

                    r = requests.post(full_url, data=data, headers=HEADERS) if method == "post" \
                        else requests.get(full_url, params=data, headers=HEADERS)

                    if "invalid" not in r.text.lower() and "error" not in r.text.lower():
                        print(f"{Fore.RED}[!] Possible login bypass: {full_url} with {u}:{p}{Style.RESET_ALL}")
                        vulnerable_forms.append({
                            "url": full_url,
                            "user": u,
                            "pass": p,
                            "method": method
                        })
                        break

            elif injection_fields:
                for inj_field in injection_fields:
                    test_payloads = ["' OR 1=1--", "<script>alert(1)</script>"]
                    for payload in test_payloads:
                        inj_data = data.copy()
                        inj_data[inj_field] = payload

                        r = requests.post(full_url, data=inj_data, headers=HEADERS) if method == "post" \
                            else requests.get(full_url, params=inj_data, headers=HEADERS)

                        if payload in r.text or "sql" in r.text.lower():
                            print(f"{Fore.RED}[!] Input Injection Detected on {full_url} field '{inj_field}' with payload: {payload}{Style.RESET_ALL}")
                            vulnerable_forms.append({
                                "url": full_url,
                                "field": inj_field,
                                "payload": payload,
                                "method": method
                            })
                            break

        return vulnerable_forms

    except Exception as e:
        print(f"{Fore.YELLOW}[!] Error scanning forms on {url}: {e}{Style.RESET_ALL}")
        return []
