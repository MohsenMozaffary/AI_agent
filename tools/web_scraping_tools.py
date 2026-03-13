from langchain_core.tools import tool
from playwright.sync_api import sync_playwright
import base64


playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=True)
page = browser.new_page()

@tool 
def go_to_url(url:str) -> str:
    """
    This tool can be used to go to the input url for scraping
    It just opens a url and keeps it opened
    """

    page.goto(url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_load_state("networkidle")

    return f"latest returned url is: {url}"

@tool
def get_buttons_from_page()-> list:
    """
    This function gets the existing buttons from an opened website
    Args:
    Output:
        buttons_list: list of buttons in a URL
    """

    buttons = page.locator("button")
    buttons_list = [b.strip() for b in buttons.all_text_contents() if b.strip()]
    
    return buttons_list


@tool
def get_clickables_from_page()-> list:
    """
    This function gets the existing clickable fields from a URL
    Args:
        Output:
            buttons_list: list of clickable fields in a URL
    """

    buttons = page.locator("button, a, [role='button']")
    buttons_list = [b.strip() for b in buttons.all_text_contents() if b.strip()]
    buttons_list = list(set(buttons_list))
    
    return buttons_list


@tool
def click_button(button: str) -> str:
    """
    Clicks a button on a webpage that is opened before.

    Args:
        button: text of the button to click
    """

    try:
        locator = page.locator(f"button:has-text('{button}'), a:has-text('{button}'), [role='button']:has-text('{button}')")

        locator.wait_for(timeout=5000)

        locator.first.click()
        page.wait_for_load_state("networkidle")

        return f"Clicked button '{button}'"

    except Exception as e:

        return f"Button '{button}' not found"

@tool
def get_page_text()-> str:
    """
    Returns visible text from the page.
    """
    text = page.inner_text("body")
    return text[:3000]

@tool
def take_screenshot()->str:
    """
    Takes a screenshot of the currently opened page
    and returns it as a base64 encoded string.
    """
    screenshot_bytes = page.screenshot(full_page=True)
    screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")

    return screenshot_base64

@tool
def get_links_from_page() -> list:
    """
    Returns visible links from the page.
    """

    links = page.locator("a")
    hrefs = links.evaluate_all("els => els.map(e => e.href)")
    
    return hrefs[:20]

@tool
def click_link(link_text: str) -> str:
    """
    Clicks a link using its visible text.
    """

    try:
        locator = page.locator(f"a:has-text('{link_text}')")

        locator.first.wait_for(timeout=5000)

        locator.first.click()

        page.wait_for_load_state("networkidle")

        return f"Clicked link '{link_text}'"

    except:
        return f"Link '{link_text}' not found"
    
@tool
def get_tables_from_page() -> list:
    """
    Extracts tables from the page.
    """

    tables = page.locator("table")

    table_data = tables.evaluate_all("""
        tables => tables.map(table => 
            Array.from(table.rows).map(row => 
                Array.from(row.cells).map(cell => cell.innerText)
            )
        )
    """)

    return table_data

@tool
def scroll_page() -> str:
    """
    Scrolls the page to load dynamic content.
    """

    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    page.wait_for_timeout(2000)

    return "Page scrolled"

@tool
def fill_input(placeholder: str, text: str) -> str:
    """
    Fills an input field identified by placeholder text.
    """

    try:
        page.get_by_placeholder(placeholder).fill(text)

        return f"Filled input '{placeholder}'"

    except:
        return "Input field not found"
    
@tool
def press_enter() -> str:
    """
    Presses Enter key.
    """

    page.keyboard.press("Enter")

    page.wait_for_load_state("networkidle")

    return "Pressed Enter"

@tool
def get_page_metadata() -> dict:
    """
    Returns metadata about the current page.
    """

    return {
        "url": page.url,
        "title": page.title()
    }