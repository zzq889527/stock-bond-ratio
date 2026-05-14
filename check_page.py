from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    console_errors = []
    page.on('console', lambda msg: 
        console_errors.append(f'[{msg.type}] {msg.text}') if msg.type in ('error', 'warning') else None
    )
    
    page.on('pageerror', lambda err: console_errors.append(f'[PAGE ERROR] {err.message}'))
    
    print('Navigating to page...')
    page.goto('https://zzq889527.github.io/stock-bond-ratio')
    page.wait_for_load_state('networkidle')
    page.wait_for_timeout(3000)
    
    print('\n=== Console Errors/Warnings ===')
    for e in console_errors:
        print(e)
    
    print('\n=== Page Title ===')
    print(page.title())
    
    print('\n=== Checking for IndexSelector ===')
    # Look for the index selector buttons
    buttons = page.locator('button').all()
    print(f'Found {len(buttons)} buttons on page')
    for btn in buttons:
        text = btn.text_content()
        if text:
            print(f'  Button: "{text.strip()}"')
    
    print('\n=== Checking for "选择指数" text ===')
    selector_text = page.locator('text=选择指数').count()
    print(f'"选择指数" found: {selector_text > 0}')
    
    print('\n=== Checking for index names ===')
    for name in ['沪深300', '沪深300等权', '中证500', '中证500等权', '中证全指', '中证全指等权']:
        count = page.locator(f'text={name}').count()
        print(f'  "{name}" found: {count > 0} (count={count})')
    
    print('\n=== Checking ERP value ===')
    erp_text = page.locator('text=ERP').count()
    print(f'"ERP" text found: {erp_text > 0}')
    
    print('\n=== Page Content (first 2000 chars) ===')
    content = page.content()
    print(content[:2000])
    
    page.screenshot(path='e:/Trae Project/page_screenshot.png', full_page=True)
    print('\nScreenshot saved to page_screenshot.png')
    
    browser.close()