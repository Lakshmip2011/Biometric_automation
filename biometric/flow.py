import re
import os
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright


def run(playwright):
    print("Running automation...")

    # ✅ automatic dates (NO input)
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    print("Start Date:", start_date)
    print("End Date:", end_date)

    browser = playwright.chromium.launch(headless=True)

    # Enable downloads
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

     # ---------------- LOGIN ----------------

    page.goto("http://192.168.1.109:8081/", wait_until="domcontentloaded")
    print("Page URL:", page.url)

    # wait for login form fields
    page.wait_for_selector("input[name='username']", timeout=30000)

    # fill credentials
    page.locator("input[name='username']").first.fill("admin")
    page.locator("input[name='password']").first.fill("admin")

    # wait explicitly for visible button
    login_button = page.locator("button[type='submit']:visible")

    login_button.wait_for(state="visible", timeout=30000)

    # force click (important for Jenkins/headless)
    login_button.first.click(force=True)

    # wait for navigation after login
    page.wait_for_load_state("networkidle")
    # ---------------- NAVIGATION ----------------
    page.get_by_role("link", name="Attendance", exact=True).click()
    page.get_by_role("link", name=" Reports").click()
    page.get_by_role("link", name="Calculate").click()

    page.locator("#calculation-tree-control").get_by_title("Select All").click()
    page.get_by_role("button", name="calculate").click()

    page.get_by_role("link", name="Reports", exact=True).click()
    page.locator("li").filter(has_text=re.compile(r"^First In Last Out$")).click()

    page.locator("#firstInLastOutReport-dept-tree-control").get_by_title("Select All").click()

    page.wait_for_timeout(2000)

    # ---------------- FILTERS ----------------
    # Expand Position section
    # Wait for tree container
    page.wait_for_selector("#firstInLastOutReport-tree", timeout=15000)

    # Expand ALL nodes (IMPORTANT)
    expand_buttons = page.locator(".button.switch")  # tree expand arrows
    count = expand_buttons.count()

    for i in range(count):
        try:
            expand_buttons.nth(i).click()
        except:
            pass  # ignore already expanded

    page.wait_for_timeout(2000)

    # Now click the checkbox properly
    position = page.locator("#firstInLastOutReport-tree-position_9_check")

    position.wait_for(state="attached", timeout=10000)

    # Use JS click (bypass hidden overlay issue)
    page.evaluate("(el) => el.click()", position)

    page.wait_for_timeout(2000)

    # Select checkbox inside it
    position_checkbox = page.locator("#firstInLastOutReport-tree-position_9_check")

    position_checkbox.wait_for(state="attached")
    position_checkbox.click(force=True)

    # ---------------- DATE INPUT ----------------
    page.locator("#firstInLastOutReport-start-date").fill(start_date)
    page.locator("#firstInLastOutReport-end-date").fill(end_date)

    page.wait_for_timeout(2000)

    # ---------------- SEARCH + EXPORT ----------------
    page.locator(".button-3d.firstInLastOutReport-search > .fa").click()
    page.locator(".fa.fa-fw.fa-share").click()
    page.get_by_text("Excel Export").click()
    page.get_by_text("").click()

    page.wait_for_timeout(2000)

    # ---------------- DOWNLOAD ----------------
    with page.expect_download() as download_info:
        with page.expect_popup() as page1_info:
            page.click("//a[text()='Confirm']")
        page1 = page1_info.value

    download = download_info.value

    # ---------------- SAVE FILE ----------------
    download_dir = r"C:\Users\Admin\Downloads\biometric\downloads"
    os.makedirs(download_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"First_In_Last_Out_Report_{timestamp}.xlsx"
    file_path = os.path.join(download_dir, file_name)

    download.save_as(file_path)

    print(f"File saved at: {file_path}")

    page1.close()

    context.close()
    browser.close()


# ✅ Proper entry point (important for Jenkins)
if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
