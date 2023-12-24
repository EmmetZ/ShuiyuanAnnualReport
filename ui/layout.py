from flet import (
    Page,
    Row,
    Column,
    Text,
    padding,
    colors,
    Control,
    Container,
    Icon,
    icons,
    TextThemeStyle,
    RadioGroup,
    ElevatedButton,
    ScrollMode,
    margin,
    IconButton,
    Dropdown,
    dropdown,
    ProgressRing,
    AlertDialog,
    Radio
)
from selenium.common.exceptions import SessionNotCreatedException
import os
# import sys
# sys.path.append(os.getcwd())
from utils.constant import Browser


class AppLayout(Row):
    def __init__(self, app, page: Page, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.page = page
        
       
        self.browser_radiogroup = RadioGroup(
            content=Column(
                [
                    Radio(value=Browser.EDGE, label="Edge"),
                    Radio(value=Browser.CHROME, label="Chrome")
                ]
            ),
            on_change=self.loginButton_enable
        )
        self.login_radiogroup = RadioGroup(
            content=Column(
                [
                    Radio(value="mannual", label="账号密码登陆"),
                    Radio(value="cookie", label="cookie登陆"),
                    Radio(value="qrcode", label="扫码登陆")
                ]
            ),
            on_change=self.loginButton_enable
        )
        self.loginButton = ElevatedButton(
            '登陆', 
            disabled=True,
            on_click=self.login)
        self.startButton = ElevatedButton(
            '开始', 
            disabled=True, 
            bgcolor=colors.GREEN_400, 
            icon=icons.PLAY_ARROW, 
            icon_color=colors.WHITE,
            on_click=self.start)
        self.login_text = Text()
        self.ProcessingRing = ProgressRing(
            visible=False, 
            width=20, 
            height=20,
            stroke_width=3)
        self.year_dropdown = Dropdown(
            width=70,
            text_size=14,
            options=[
                dropdown.Option("2023"),
                dropdown.Option("2022"),
                dropdown.Option("2021"),
                dropdown.Option("2020"),
            ],
            on_change=self.startButton_enable
        )
        self.user = [
            Text(no_wrap=True),
            Text(no_wrap=True)
        ]

        self.get_main_layout()
        self.start_layout = None
        self._active_view: Control = self.main_layout
        self.controls = [self.active_view]
        self.login_state = False
    

    @property
    def active_view(self):
        return self._active_view
    

    @active_view.setter
    def active_view(self, view):
        self._active_view = view
        self.controls[-1] = self._active_view
        self.update()
        # print(self.controls)

 
    def get_main_layout(self):
        self.main_layout = Column(
            [   
                Row(
                    [
                        Container(
                            Row(
                                [   
                                    Icon(icons.ACCOUNT_CIRCLE_ROUNDED),
                                    Text(value="登陆", style=TextThemeStyle.TITLE_LARGE,
                                    size=28
                                    )
                                ]
                            ),
                            expand=True,
                            padding=padding.only(top=-2, left=10), 
                            bgcolor=colors.BLUE_200,
                        ),
                    ]   
                ),
                Row(
                    [
                        Container(
                            Text(value="为了获取数据的只读权限，请您先登录"),
                            expand=True,
                            padding=padding.only(top=0, left=10),
                        )
                    ]
                ),
                Row(
                    [
                        Container(
                            Column(
                                [   
                                    Text("请选择浏览器："),
                                    self.browser_radiogroup,
                                    Container(
                                        self.loginButton,
                                        margin=margin.only(left=10),
                                    )
                                ],  
                            ),
                            margin=margin.only(top=4, left=10),
                        ),
                        Container(
                            Column(
                                [
                                    Text("请选择登陆方式："),
                                    self.login_radiogroup
                                ]
                            ),
                            margin=margin.only(top=5, left=10),
                        ),
                        Container(
                            Column(
                                [
                                    Text('选择年份：'),
                                    self.year_dropdown,
                                    Container(
                                        self.startButton,
                                        margin=margin.only(top=5, left=-10),
                                    )
                                ]
                            ),
                            margin=margin.only(top=-15, left=10),
                            padding=padding.only(top=0),
                        )
                    ]
                ),
                Container(
                    Row([   
                        self.ProcessingRing,
                        self.login_text
                    ]),
                    margin=margin.only(top=5, left=20),
                    
                ),
                Row(
                    [   
                        Container(
                            Column(
                                [
                                    self.user[0],
                                    self.user[1]
                                ]
                            ),
                            margin=margin.only(top=0, left=20),
                            width=250
                        )
                    ]
                )
            ],
            expand=True,
            scroll=ScrollMode.ALWAYS
        )


    def loginButton_enable(self, e):
        if self.browser_radiogroup.value != None and self.login_radiogroup.value != None and self.loginButton.disabled == True:
            self.loginButton.disabled = False
            self.page.update()


    def startButton_enable(self, e):
        if self.year_dropdown.value != None and self.startButton.disabled == True and self.login_state == True:
            self.startButton.disabled = False
            self.page.update()


    def start(self, e):
        self.page.route = '/start'
        self.page.update()


    def stop(self, e):
        self.page.route = '/'
        self.page.update()


    def set_start_view(self):
        print('start set start view')
        # if self.start_layout == None:
        self.get_start_layout()
        self.active_view = self.start_layout
        try:
            self.app.start(int(self.year_dropdown.value))
            self.backButton.disabled = False
            self.backButton.icon = icons.ARROW_BACK
            self.subTitle.value = "完成"
            self.backButton.tooltip = '返回登陆界面'
            self.page.update()
        except Exception as err:
            self.error('蜜汁错误(?)', err.__str__())
        # self.app.start(int(self.year_dropdown.value))
        # self.backButton.disabled = False
        # self.backButton.icon = icons.ARROW_BACK
        # self.subTitle.value = "完成"
        # self.backButton.tooltip = '返回登陆界面'
        # self.page.update()
    

    def set_main_view(self):
        self.active_view = self.main_layout
        self.page.update()


    def login(self, e):
        self.login_text.value = ""
        self.loginButton.disabled = True
        self.startButton.disabled = True
        self.ProcessingRing.visible = True
        self.browser_radiogroup.disabled = True
        self.login_radiogroup.disabled = True
        self.page.update()
        try:
            login_state = self.app.login(self.browser_radiogroup.value, self.login_radiogroup.value)
        except SessionNotCreatedException as err:
            self.error('请检查浏览器驱动版本')
        except Exception as err:
            self.error('蜜汁错误(?)', err.__str__())
        if login_state == 'noinput_cookie':
            self.login_state = False
            self.login_text.value = "已取消"
        if login_state == 'cookie_error':
            self.login_state = False
            self.login_text.value = "登陆失败，请检查cookie"
        if login_state == 'error':
            self.login_state = False
            self.login_text.value = "未知错误(?)"
        if login_state == 'timeout':
            self.login_state = False
            self.login_text.value = '登陆超时，请重新登陆'
        if login_state == 'succ':
            username, name = self.app.getUser()
            self.login_state = True
            self.login_text.value = "登陆成功"
            self.user[0].value = f'用户名：{username}'
            self.user[1].value = f'昵称：{name}'
            if not self.year_dropdown.value:
                self.startButton.disabled = True
            else:
                self.startButton.disabled = False
        if self.app.client.driver != None:
            self.app.client.driver.quit()
        self.ProcessingRing.visible = False
        self.loginButton.disabled = False
        self.browser_radiogroup.disabled = False
        self.login_radiogroup.disabled = False
        self.page.update()


    def get_start_layout(self):
        self.backButton = IconButton(
                        icon=icons.CLOUD_DOWNLOAD,
                        on_click=self.stop,
                        icon_size=30,
                        disabled=True,
                        icon_color=colors.WHITE
                    )
        self.subTitle = Text(
            "正在生成",    
            style=TextThemeStyle.TITLE_LARGE,
            size=30
            )
        self.start_layout = Column(
            [   
                Row(
                    [
                        Container(
                            Row(
                                [   
                                    self.backButton,
                                    self.subTitle, 
                                ]
                            ),
                            expand=True,
                            padding=padding.only(top=0, left=10), 
                            bgcolor=colors.BLUE_200,
                        ),
                    ],
                )
            ],
            expand=True
        )


    def error(self, title, text=None):
        exit_button = ElevatedButton(
                text="ok", bgcolor=colors.BLUE_200, on_click=lambda e: self.page.window_destroy() or os._exit(0)
            )
        if text == None:
            dialog = AlertDialog(
                title=Text(title),
                content=exit_button
            )
        else:
            dialog = AlertDialog(
                title=Text(title),
                content=Column(
                            [
                                Text(text, selectable=True),
                                exit_button,
                            ],
                    tight=True,
                    scroll=ScrollMode.AUTO
                ),
            )
        self.page.dialog = dialog
        dialog.open = True
        if self.app.client.driver.service.process.returncode == None:
            self.app.client.driver.quit()
        self.page.update()
        while dialog.open:
            continue
        