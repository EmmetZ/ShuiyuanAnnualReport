from flet import (
    Page,
    UserControl,
    Row,
    Column,
    Text,
    View,
    padding,
    colors,
    icons,
    ElevatedButton,
    TemplateRoute,
    TextField,
    AlertDialog,
    IconButton
)

from typing import Literal
from ui.layout import AppLayout
from client import Client


class App(UserControl):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.page.on_route_change = self.route_change
        self.cookie = None
        self.client = Client(self.showProgress)
    
    def build(self):
        self.layout = AppLayout(self, self.page)
        return self.layout
    
    def initialize(self):
        self.page.views.clear()
        self.page.views.append(
            View(
                '/',
                [self.layout],
                padding=padding.all(0),
                bgcolor=colors.WHITE
            )
        )
        self.page.update()
        self.page.go('/')
    

    def check_login_state(self):
        pass


    def route_change(self, e):
        print('route change')
        curr_route = TemplateRoute(self.page.route)
        if curr_route.match("/"):
            self.page.go("/main")
            self.layout.set_main_view()
        elif curr_route.match("/start"):
            self.page.go("/start")
            self.layout.set_start_view()
        self.page.update()

    
    def login(self, browser, login_method) -> str:
        if login_method == 'cookie':
            self.cookie_input()
            while self.tmp_cookie is None and self.page.dialog.open:
                continue
            if self.tmp_cookie == None:
                del self.tmp_cookie
                return 'noinput_cookie'
            try:
                flag = self.client.login_cookie(browser, self.tmp_cookie)
            except:
                raise
            if flag == True:
                return 'succ'
            else:
                return 'cookie_error'
        elif login_method == 'qrcode':
            flag = self.client.login_qrcode(browser)
            if flag:
                return 'succ'
            else:
                return 'timeout'
        elif login_method == 'mannual':
            try:
                flag = self.client.login_mannual(browser)
            except:
                raise
            if flag == True:
                    return 'succ'
            else:
                return 'error'
        
    
    def getUser(self):
        return self.client.getmUser()
        

    def start(self, year):
        print('start generate report')
        self.client.generateReport(year)

    
    def cookie_input(self):
        self.tmp_cookie = None
        def close_dlg(e):
            if (hasattr(e.control, "text") and not e.control.text == "Cancel") or (
                type(e.control) is TextField and e.control.value != ""
            ):
                self.tmp_cookie = dialog_text.value
            dialog.open = False
            self.page.update()

        def textfield_change(e):
            if dialog_text.value == "":
                create_button.disabled = True
                delete_button.disabled = True
            else:
                create_button.disabled = False
                delete_button.disabled = False
            self.page.update()

        def clear_textfield(e):
            if dialog_text.value != "":
                dialog_text.value = ""
                create_button.disabled = True
                delete_button.disabled = True
                dialog_text.focus()
                self.page.update()

        dialog_text = TextField(
            label="cookie(_t)的值", on_submit=close_dlg, on_change=textfield_change,
            width=180
        )
        create_button = ElevatedButton(
            text="ok", bgcolor=colors.BLUE_200, on_click=close_dlg, disabled=True
        )
        delete_button = IconButton(
            icon=icons.DELETE,
            bgcolor=colors.RED_200, 
            on_click=clear_textfield,
            disabled=True
            )
        dialog = AlertDialog(
            title=Text("请输入cookie(_t)的值"),
            content=Column(
                [   
                    Row(
                        [
                            dialog_text,
                            delete_button
                        ]
                    ),
                    Row(
                        [
                            ElevatedButton(text="Cancel", on_click=close_dlg),
                            create_button,
                        ],
                        alignment="spaceBetween",
                    ),
                ],
                tight=True,
            ),
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        dialog_text.focus()


    def showProgress(self, text: str=None, update: Literal['nl', 'el', 'n']='n'):
        if update == 'nl':
            self.process = Text(text if text != None else '')
            self.layout.controls[-1].controls.append(Row([self.process]))
        elif update == 'el':
            self.process = Text(text if text != None else '')
            self.layout.controls[-1].controls[-1].controls.append(Row([self.process]))
        elif update == 'n':
            self.process.value = text 
        self.page.update()
        