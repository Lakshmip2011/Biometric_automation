import re
import os
from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright


def run(playwright: Playwright) -> None:
    # -------- TAKE INPUT FROM USER --------
    # start_date = input("Enter start date (format: YYYY-MM-DD, e.g. 2026-04-26): ")
    # end_date = input("Enter end date (format: YYYY-MM-DD, e.g. 2026-04-30): ")

from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright


def run(playwright):
    print("Running automation...")

    #  automatic dates (NO input)
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    print("Start Date:", start_date)
    print("End Date:", end_date)

    # 👉 your existing logic continues here

    browser = playwright.chromium.launch(headless=False)

    # Enable downloads
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    # ---------------- LOGIN ----------------
    page.goto("http://127.0.0.1:8081/login/?next=/")
    page.get_by_role("textbox", name="Username").fill("admin")
    page.get_by_role("textbox", name="Password").fill("admin")
    page.get_by_role("button", name="Login").click()

    page.wait_for_timeout(2000)

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

    # Optional zoom
    page.evaluate("document.body.style.zoom='65%'")

    page.wait_for_timeout(2000)

    # ---------------- FILTERS ----------------
    page.get_by_role("listitem").filter(has_text="Position").click()
    page.get_by_role("listitem").filter(has_text="Position").click()
    page.locator("#firstInLastOutReport-tree-position_9_check").click()

    page.wait_for_timeout(2000)

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
    file_name = f"First In Last Out Report_{timestamp}.xlsx"
    file_path = os.path.join(download_dir, file_name)

    download.save_as(file_path)

    print(f"File saved at: {file_path}")

    page1.close()

    # ---------------- CLOSE ----------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
