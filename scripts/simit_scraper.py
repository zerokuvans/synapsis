from playwright.sync_api import sync_playwright, TimeoutError
import pandas as pd
import time
import random
import sys
import re
import os
import requests

SIMIT_PROXY_SERVER = None
SIMIT_PROXY_LIST = None
SIMIT_PROXY_INDEX = 0

def get_simit_proxy_server(reset=False):
    global SIMIT_PROXY_SERVER, SIMIT_PROXY_LIST, SIMIT_PROXY_INDEX
    if reset:
        SIMIT_PROXY_SERVER = None
    if SIMIT_PROXY_SERVER is not None:
        return SIMIT_PROXY_SERVER
    v = os.getenv('SIMIT_PROXY')
    if v:
        SIMIT_PROXY_SERVER = v.strip()
        return SIMIT_PROXY_SERVER
    if SIMIT_PROXY_LIST is None:
        try:
            list_url = os.getenv('SIMIT_PROXY_LIST_URL')
            if not list_url:
                key = os.getenv('PROXYSCRAPE_API_KEY')
                if key:
                    list_url = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all&auth=' + key.strip()
                else:
                    list_url = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'
            r = requests.get(list_url, timeout=5)
            proxies = []
            if r.status_code == 200:
                for line in r.text.splitlines():
                    line = (line or '').strip()
                    if not line:
                        continue
                    if not line.startswith('http'):
                        line = 'http://' + line
                    proxies.append(line)
            SIMIT_PROXY_LIST = proxies
            SIMIT_PROXY_INDEX = 0
        except Exception:
            SIMIT_PROXY_LIST = []
            SIMIT_PROXY_INDEX = 0
    if SIMIT_PROXY_LIST:
        if SIMIT_PROXY_INDEX >= len(SIMIT_PROXY_LIST):
            return None
        SIMIT_PROXY_SERVER = SIMIT_PROXY_LIST[SIMIT_PROXY_INDEX]
        SIMIT_PROXY_INDEX += 1
        return SIMIT_PROXY_SERVER
    return None

def scrape_placas(placas, headless=True, timeout=120000, pause_range=(7, 10), max_retries=2):
    resultados = []
    with sync_playwright() as p:
        proxy_server = get_simit_proxy_server()
        if proxy_server:
            browser = p.chromium.launch(headless=headless, proxy={"server": proxy_server}, args=["--disable-blink-features=AutomationControlled"])
        else:
            browser = p.chromium.launch(headless=headless, args=["--disable-blink-features=AutomationControlled"])
        page = browser.new_page()
        page.goto('https://www.fcm.org.co/simit/#/consultas', timeout=timeout)
        try:
            page.wait_for_selector("text=Por placa", timeout=timeout)
        except Exception:
            pass
        try:
            for txt in ['Aceptar','Acepto','Entendido','Continuar','Cerrar']:
                cand = page.locator(f"button:has-text('{txt}')")
                if cand.count() > 0:
                    cand.first.click()
                    break
        except Exception:
            pass
        for placa in placas:
            t0 = time.time()
            res = {'PLACA': placa, 'TIENE_MULTA': None, 'VALOR': None}
            for attempt in range(max_retries):
                try:
                    page.wait_for_timeout(1000)
                    try:
                        page.fill("input[type='text']", "")
                    except Exception:
                        pass
                    try:
                        por_placa = page.get_by_text('Por placa', exact=False)
                        if por_placa.count() > 0:
                            por_placa.first.click()
                        else:
                            lnk = page.locator("a[href*='por-placa'], button:has-text('Por placa')")
                            if lnk.count() > 0:
                                lnk.first.click()
                    except Exception:
                        pass
                    # Buscar input visible
                    filled = False
                    cand_inp = page.locator("input[formcontrolname='placa'], input[ng-reflect-form-control-name*='placa'], input[placeholder*='placa' i], input[name*='placa' i], input[id*='placa' i], input[type='text']")
                    if cand_inp.count() > 0:
                        try:
                            cand_inp.first.fill(placa)
                            filled = True
                        except Exception:
                            pass
                    if not filled:
                        try:
                            inp = page.locator("xpath=//*[contains(text(),'Placa')]/following::input[1]")
                            if inp.count() > 0:
                                inp.first.fill(placa)
                                filled = True
                        except Exception:
                            pass
                    try:
                        btn = page.locator("button:has-text('Consultar')")
                        if btn.count() == 0:
                            btn = page.get_by_role('button', name='Consultar', exact=False)
                        if btn.count() > 0:
                            btn.first.click()
                        else:
                            page.keyboard.press('Enter')
                    except Exception:
                        page.keyboard.press('Enter')
                    try:
                        page.wait_for_function("()=>{ const t=(document.body.innerText||''); return /NO REGISTRA COMPARENDOS|NO REGISTRA MULTAS|TOTAL A PAGAR/i.test(t); }", timeout=15000)
                    except Exception:
                        pass
                    page.wait_for_timeout(2000)
                    try:
                        contenido = page.inner_text('body').upper()
                    except Exception:
                        contenido = ''
                    if 'NO REGISTRA COMPARENDOS' in contenido or 'NO REGISTRA MULTAS' in contenido:
                        res['TIENE_MULTA'] = 'NO'
                        res['VALOR'] = 0
                        resultados.append(res)
                        break
                    if 'TOTAL A PAGAR' in contenido:
                        try:
                            body_txt = page.inner_text('body')
                            m = re.search(r"TOTAL\s*A\s*PAGAR\s*\$?\s*([\d\.,]+)", body_txt, flags=re.IGNORECASE)
                            val_s = m.group(1) if m else None
                            val_f = float(str(val_s).replace('.', '').replace(',', '.')) if val_s else None
                        except Exception:
                            val_f = None
                        if val_f is not None:
                            res['TIENE_MULTA'] = 'SI'
                            res['VALOR'] = val_f
                            resultados.append(res)
                            break
                    raise Exception('Resultado no claro')
                except Exception as e:
                    if attempt == max_retries - 1:
                        res['ERROR'] = str(e)
                        resultados.append(res)
                finally:
                    page.wait_for_timeout(random.randint(pause_range[0], pause_range[1]) * 1000)
            dt = time.time() - t0
            wait_s = random.randint(pause_range[0], pause_range[1])
            if dt < wait_s:
                time.sleep(wait_s - dt)
        browser.close()
    return resultados

if __name__ == '__main__':
    placas = ['TON81E', 'IVS28F', 'YAB59E', 'LVA91E', 'APU64G', 'CZE19E']
    headless = True
    if len(sys.argv) > 1:
        placas = [x.strip().upper() for x in sys.argv[1:] if x.strip()]
    resultados = scrape_placas(placas, headless=headless)
    df = pd.DataFrame(resultados)
    df.to_csv('resultado_simit.csv', index=False)
    try:
        df.to_excel('resultado_simit.xlsx', index=False)
    except Exception:
        pass
    print(df)
