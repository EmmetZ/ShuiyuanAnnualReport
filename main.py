from ui.app import App
from os import fspath
from flet import Page, Theme, app
from utils.constant import BASE_FILEPATH


def main(page: Page):
    def window_event(e):
        if e.data == "close":
            print('close')
            page.views.clear()
            try:
                if app.client.driver.service.process.returncode == None:
                    print('driver process exit')
                    app.client.driver.quit()
            except: pass
            page.window_destroy()
    page.title = 'Shuiyuan Annual Report Generator'
    # page.padding = 0
    page.window_height = 400
    page.window_width = 400
    page.fonts = {
        'msyh': fspath(BASE_FILEPATH.joinpath('resources', 'Font', 'msyh.ttc'))
    }

    page.theme = Theme(font_family="msyh")
    page.window_center()
    app = App(page)
    page.add(app)
    page.update()
    app.initialize()
    page.window_prevent_close = True
    page.on_window_event = window_event


# flet_core\page.py:466 ctrl.page = None 改为 if ctrl.page != self: ctrl.page = None
# 'https://github.com/flet-dev/examples/issues/102'
if __name__ == "__main__":
    app(target=main)

