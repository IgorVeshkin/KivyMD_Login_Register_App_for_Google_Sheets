import os

os.environ['KIVY_IMAGE'] = 'pil,sdl2'

from kivy.lang import Builder
from kivy.properties import StringProperty

from kivy.uix.floatlayout import FloatLayout

from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, SwapTransition

from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.bottomsheet import MDListBottomSheet
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.snackbar import Snackbar

from kivy.clock import mainthread

import time
from threading import Thread

import sqlite3 as sql

import httplib2
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

# https://pictogrammers.com/library/mdi/
# https://medium.com/nerd-for-tech/how-to-change-the-screen-transition-in-kivy-b05fbfe82d81
# https://stackoverflow.com/questions/59343604/kivymd-accessing-label-id-from-screen-class
# https://stackoverflow.com/questions/58862489/how-can-i-call-an-on-pre-enter-function-in-kivy-for-my-root-screen


# Переменная, в которой будут храниться данные залогиненного пользователя

user_data = []

# Интерфейс, формируемы фреймворком Kivy можно написать на своем собственном языке

KV = '''
WindowsManager:
    id: WindowsManager

    LoginFormLayout:
        size_hint_x: None
        width: "300dp"
        hint_text: "Password"
        pos_hint: {"center_x": .5, "center_y": .5}

    EditingForm:

    RegisterForm:  
        size_hint_x: None
        width: "300dp"
        hint_text: "Password"
        pos_hint: {"center_x": .5, "center_y": .5}


<EditingForm>:

    name: "EditingForm"


    BoxLayout:
        orientation: "vertical"
        size: root.width, root.height

        MDIconButton:
            icon: "exit-to-app"
            pos_hint: {"left": 1, "center_y": 1}
            on_release: root.logout_from_profile()

        ScrollView:

            GridLayout:
                cols: 2
                rows: 7

                padding: 10
                spacing: 20


                Label:
                    text: "Номер строки:"
                    size_hint: None, None
                    width: 120
                    height: 40

                    font_size: 18
                    color: "black"

                MDRaisedButton:
                    id: LineNumber
                    text: "Строка 2"
                    width: 200
                    on_release: root.show_example_list_bottom_sheet()
                    pos_hint: {"center_x": .5, "center_y": .5}         


                Label:
                    text: "Имя:"
                    size_hint: None, None
                    width: 100
                    height: 40

                    font_size: 18
                    color: "black"

                TextInput:
                    id: FirstName
                    multiline: False

                    size_hint: 0.85, None
                    width: 200
                    height: 40

                    font_size: 18
                    color: "black"

                    disabled: True


                Label:

                    text: "Фамилия:"
                    size_hint: None, None
                    width: 100
                    height: 40

                    font_size: 18
                    color: "black"

                TextInput:
                    id: FamilyName
                    multiline: False

                    size_hint: 0.85, None
                    width: 200
                    height: 40

                    font_size: 18
                    color: "black"

                    disabled: True

                Label:

                    text: "Отчество:"
                    size_hint: None, None
                    width: 100
                    height: 40

                    font_size: 18
                    color: "black"

                TextInput:
                    id: FathersName
                    multiline: False

                    size_hint: 0.85, None
                    width: 200
                    height: 40

                    font_size: 18
                    color: "black"

                    disabled: True


                Button:                    
                    #:import C kivy.utils.get_color_from_hex

                    id: Birthday_btn
                    text: "Дата Рождения"
                    background_color: C("#2196F3")
                    size_hint: None, None
                    width: 160
                    height: 40

                    font_size: 18
                    color: "white"

                    on_press:
                        root.show_date_picker()

                    on_release:
                        background_color: C("#219403")

                    disabled: True


                Label:
                    id: Birthday
                    text: "Нет даты"
                    size_hint: 0.5, None
                    width: 200
                    height: 40

                    font_size: 18
                    color: "black"


                Label:

                    text: "Email:"
                    size_hint: None, None
                    width: 100
                    height: 40

                    font_size: 18
                    color: "black"

                TextInput:
                    id: Email
                    multiline: False

                    size_hint: 0.85, None
                    width: 200
                    height: 40

                    font_size: 18
                    color: "black"

                    disabled: True


        Button:
            id: save_record_btn
            text: "Save record in Google Sheets"
            font_size: 18
            size_hint_y: None
            height: 60
            on_release:
                root.save_in_google_sheets()

            disabled: True


<RegisterForm>:

    name: "RegisterForm"

    size_hint_y: None
    height: register_password_field.height

    MDRelativeLayout:

        MDIcon:
            icon: "account"
            font_size: dp(30)
            pos: Register_Caption_label.width/2 - self.width - dp(125), 170  

        MDLabel:
            id: Register_Caption_label
            text: "Register Form"
            font_size: dp(20)    
            pos: Register_Caption_label.width/2 - self.width/2 + dp(30), 150    

        MDTextField:
            id: register_login_field
            hint_text: "Login"
            pos: Register_Caption_label.width/2 - self.width/2 + dp(0), 100
            required: False
            helper_text_mode: "on_error"
            helper_text: "No login entered"

            on_text:
                root.select_register_login_field()


        MDTextField:
            id: register_password_field
            hint_text: root.hint_text
            text: root.text
            password: True
            pos: Register_Caption_label.width/2 - self.width/2 + dp(0), 40
            required: False
            helper_text_mode: "on_error"
            helper_text: "No password entered"


            on_text:
                root.select_register_password_field()


        MDIconButton:
            icon: "eye-off"
            pos: register_password_field.width - self.width + dp(8), register_password_field.height - dp(15)
            theme_text_color: "Hint"
            on_release:
                self.icon = "eye" if self.icon == "eye-off" else "eye-off"
                register_password_field.password = False if register_password_field.password is True else True

        MDCheckbox:
            id: nameChange_permission
            size_hint: None, None
            size: "48dp", "48dp"
            pos: register_password_field.width/2 - self.width - dp(115), register_password_field.height - dp(62)

        MDLabel: 
            text: "Add 'Name Change' Permission"
            pos: register_password_field.width - self.width + dp(30), register_password_field.height - dp(70)


        MDCheckbox:
            id: birthdateChange_permission
            size_hint: None, None
            size: "48dp", "48dp"
            pos: register_password_field.width/2 - self.width - dp(115), register_password_field.height - dp(102)

        MDLabel: 
            text: "Add 'Birthdate Change' Permission"
            pos: register_password_field.width - self.width + dp(30), register_password_field.height - dp(110)

        MDCheckbox:
            id: emailChange_permission
            size_hint: None, None
            size: "48dp", "48dp"
            pos: register_password_field.width/2 - self.width - dp(115), register_password_field.height - dp(142)

        MDLabel: 
            text: "Add 'Email Change' Permission"
            pos: register_password_field.width - self.width + dp(30), register_password_field.height - dp(150)



        MDRectangleFlatIconButton:
            icon: "check-circle"
            text: "Create account"
            theme_text_color: "Custom"
            text_color: "black"
            line_color: "gray"
            theme_icon_color: "Custom"
            icon_color: "black"

            font_size: dp(20)   

            size_hint: 1, None

            pos_hint: {"center_x": .5}
            pos: 0, -120    

            on_release:
                root.check_profile_in_database_before_creation() 

        #: import NoTransition kivy.uix.screenmanager.NoTransition
        #: import FadeTransition kivy.uix.screenmanager.FadeTransition
        #: import FallOutTransition kivy.uix.screenmanager.FallOutTransition
        #: import RiseInTransition kivy.uix.screenmanager.RiseInTransition
        #: import SwapTransition kivy.uix.screenmanager.SwapTransition

        MDRectangleFlatIconButton:
            icon: "keyboard-return"
            text: "Go back"
            theme_text_color: "Custom"
            text_color: "black"
            line_color: "gray"
            theme_icon_color: "Custom"
            icon_color: "black"

            font_size: dp(20)   

            size_hint: 1, None

            pos_hint: {"center_x": .5}
            pos: 0, -170    

            on_release:
                root.go_back_to_login_page() 



<LoginFormLayout>:

    name: "LoginForm"

    size_hint_y: None
    height: password_field.height

    MDRelativeLayout:

        MDIcon:
            icon: "account"
            font_size: dp(30)
            pos: Login_Caption_label.width - self.width - dp(275), 170  

        MDLabel:
            id: Login_Caption_label
            text: "Login Form"
            font_size: dp(20)    
            pos: password_field.width - self.width + dp(30), 150    

        MDTextField:
            id: login_field
            hint_text: "Login"
            pos: password_field.width - self.width + dp(0), 75
            required: False
            helper_text_mode: "on_error"
            helper_text: "No login entered"

            on_text:
                root.select_login_field()


        MDTextField:
            id: password_field
            hint_text: root.hint_text
            text: root.text
            password: True
            icon_left: "key-variant"

            required: False
            helper_text_mode: "on_error"
            helper_text: "No password entered"

            on_text:
                root.select_password_field()

        MDIconButton:
            icon: "eye-off"
            pos_hint: {"center_y": .5}
            pos: password_field.width - self.width + dp(8), 0
            theme_text_color: "Hint"
            on_release:
                self.icon = "eye" if self.icon == "eye-off" else "eye-off"
                password_field.password = False if password_field.password is True else True

        MDRectangleFlatIconButton:
            icon: "check-circle"
            text: "Login"
            theme_text_color: "Custom"
            text_color: "black"
            line_color: "gray"
            theme_icon_color: "Custom"
            icon_color: "black"

            font_size: dp(20)   
            increment_width: dp(password_field.width)

            size_hint: 1, None
            size: 400, 200
            width: root.width

            pos_hint: {"center_x": .5}
            pos: 0, -50    

            on_release:
                root.search_for_profile() 

        MDRectangleFlatIconButton:
            icon: "account-plus"
            text: "Register"
            theme_text_color: "Custom"
            text_color: "black"
            line_color: "gray"
            theme_icon_color: "Custom"
            icon_color: "black"

            font_size: dp(20)   
            increment_width: dp(password_field.width)

            size_hint: 1, None
            size: 400, 200
            width: root.width

            pos_hint: {"center_x": .5}
            pos: 0, -100 

            on_release:
                root.register_new_profile() 


<DatabaseCheckDialogContent>:

    spacing: dp(20)
    size_hint_y: None

    height: dp(120)

    anchor_x: "center"
    anchor_y: "center"

    MDIcon:
        icon: "database-sync"
        font_size: dp(40)

        size: min(root.size), min(root.size)
        size_hint: None, None
        pos_hint: {'center_x': .5, 'center_y': .5}
        pos: 0, 0        

        MDSpinner:
            id: checkspinner

            size: dp(90), dp(90)
            size_hint: None, None
            pos_hint: {'center_x': .5, 'center_y': .5}

            active: True

'''


# Класс, который представляет собой отдельный элемент уровня разметки в KV-файле


class DatabaseCheckDialogContent(FloatLayout):
    pass


# Функция, которая подключается к базе данных и проверяет есть ли там пользователь с логином и паролем,
# как те что ввел пользовател. Так же программа специально будет проигрывать анимацию поиска пользователя,
# как минимум 2 секунды (Для наилучшего User Experience)

def loading_from_database_wait(app, dialog, seconds_to_load=2.0):
    time1 = time.time()

    sql_con = sql.connect(os.path.join(os.getcwd(), 'Users.sqlite3'))
    sql_cursor = sql_con.cursor()

    sql_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Users';")
    tb_name = sql_cursor.fetchall()

    if len(tb_name) == 0:
        sql_cursor.execute("""
                    CREATE TABLE Users (
                        UserID INTEGER PRIMARY KEY autoincrement,
                        Login varchar(255),
                        Password varchar(255),
                        ChangeFullName varchar(255),
                        ChangeBirthDate varchar(255),
                        ChangeEmail varchar(255)
                        );
                        """)

    sql_cursor.execute("SELECT * FROM Users us WHERE Login=? AND Password=?;",
                       (str(app.ids.login_field.text), str(app.ids.password_field.text)))

    global user_data

    user_data = sql_cursor.fetchall()

    sql_cursor.close()

    time2 = time.time()

    if time2 - time1 < seconds_to_load:
        time.sleep(2.0)

    if len(user_data) != 1:
        app.draw_snackbar()
        dialog.dismiss()
        return

    dialog.dismiss()

    app.enter_app()


# Функция, которая подключается к Google Api и сохраняет введенные пользователем в Google Sheets


def GoogleSheets(FirstName, FamilyName, FathersName, Birthday, Email, LineNumber):
    # Файл, полученный в Google Developer Console
    # Json-Файл, представляет собой, ключ, который позволяет приложению редактировать данные таблицы
    # Файл называется grounded-datum-XXXXXX-XXXXXXXXXXXX.json

    CREDENTIALS_FILE = os.path.join(os.getcwd(), 'grounded-datum-XXXXXX-XXXXXXXXXXXX.json')

    # ID Google Sheets документа (можно взять из его URL)
    spreadsheet_id = 'Здесь должен быть ID Google Sheets'

    # Авторизуемся и получаем service — экземпляр доступа к API
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = discovery.build('sheets', 'v4', http=httpAuth)

    # Записываем в таблицу имя пользователя

    if FirstName:
        values = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": f"B{LineNumber}:B{LineNumber}",
                     "majorDimension": "ROWS",
                     "values": [[FirstName]]
                     }
                ]
            }
        ).execute()

    # Записываем в таблицу фамилию пользователя

    if FamilyName:
        values = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": f"C{LineNumber}:C{LineNumber}",
                     "majorDimension": "ROWS",
                     "values": [[FamilyName]]
                     }
                ]
            }
        ).execute()

    # Записываем в таблицу отчество пользователя

    if FathersName:
        values = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": f"D{LineNumber}:D{LineNumber}",
                     "majorDimension": "ROWS",
                     "values": [[FathersName]]
                     }
                ]
            }
        ).execute()

    # Записываем в таблицу дату рождения пользователя, если данные указаны

    if Birthday != "Нет даты":
        values = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": f"E{LineNumber}:E{LineNumber}",
                     "majorDimension": "ROWS",
                     "values": [[Birthday]]
                     }
                ]
            }
        ).execute()

    # Записываем в таблицу Email пользователя

    if Email:
        values = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": f"F{LineNumber}:F{LineNumber}",
                     "majorDimension": "ROWS",
                     "values": [[Email]]
                     }
                ]
            }
        ).execute()


line_number = 1
birthday_global = ''


# Класс Экрана, в котором происходит реализация основной логики
# Графическая составляющая описана в переменной KV


class EditingForm(Screen):

    # Функция, сохраняющая заданое значение строки в отдельной переменной при выборе строки

    def callback_for_menu_items(self, *args):
        toast(args[0])
        self.ids.LineNumber.text = str(args[0])
        global line_number

        line = args[0][-1:-3:-1]
        line2 = int(line[::-1])

        line_number = line2 + 1

    # Запуск нижнего меню выбора строки

    def show_example_list_bottom_sheet(self):
        bottom_sheet_menu = MDListBottomSheet()
        for i in range(2, 11):
            bottom_sheet_menu.add_item(
                f"Строка {i}",
                lambda x, y=i: self.callback_for_menu_items(
                    f"Строка {y}"
                ),
            )
        bottom_sheet_menu.open()

    # Функция, срабатывающая при выборе и сохранение даты рождения

    def on_save(self, instance, value, date_range):
        '''
        Events called when the "OK" dialog box button is clicked.

        :type instance: <kivymd.uix.picker.MDDatePicker object>;
        :param value: selected date;
        :type value: <class 'datetime.date'>;
        :param date_range: list of 'datetime.date' objects in the selected range;
        :type date_range: <class 'list'>;
        '''

        self.date_value = str(value)

        global birthday_global
        birthday_global = self.date_value
        self.ids.Birthday.text = self.date_value

    # Функция срабатывает при отмене выбора даты рождения

    def on_cancel(self, instance, value):
        '''Events called when the "CANCEL" dialog box button is clicked.'''

    # Функция, запускающая виджет выбора даты рождения

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

    # Функция, срабатывающая запускающая сохранение данных в Google Sheets
    # Происходит проверка веденных данных и запуск нового потока,
    # чтобы интерфейс не заморозился на период сохранения данных в таблице

    def save_in_google_sheets(self):
        global user_data
        FirstName, FamilyName, FathersName, Birthday, Email = '', '', '', '', ''

        if user_data[0][3] != "0":
            FirstName = self.ids.FirstName.text
            FamilyName = self.ids.FamilyName.text
            FathersName = self.ids.FamilyName.text

        if user_data[0][4] != "0":
            global birthday_global
            Birthday = birthday_global

        if user_data[0][5] != "0":
            Email = self.ids.Email.text

        GoogleSheets_thread = Thread(target=GoogleSheets, args=(
            FirstName,
            FamilyName,
            FathersName,
            Birthday,
            Email,
            line_number
        ))

        GoogleSheets_thread.start()

    # Функция, срабатывающая при выходе из текущего профиля пользователя

    def logout_from_profile(self):
        global user_data

        user_data = []

        self.ids.LineNumber.text = "Строка 2"
        self.ids.FirstName.text = ""
        self.ids.FamilyName.text = ""
        self.ids.FathersName.text = ""
        self.ids.Birthday.text = "Нет даты"
        self.ids.Email.text = ""

        self.manager.current = "LoginForm"
        self.manager.transition = SlideTransition()
        self.manager.duration = "2"

        # https://stackoverflow.com/questions/59343604/kivymd-accessing-label-id-from-screen-class

        self.manager.get_screen("LoginForm").ids.login_field.text = ""
        self.manager.get_screen("LoginForm").ids.password_field.text = ""


# Класс оконого менеджера, данный менеджер управляет всеми окнами приложения
# Интерфейс менеджера прописывается в переменной KV

class WindowsManager(ScreenManager):
    pass


# Класс Экрана регистрации, отвечающий за основную логику окна
# Интерфейс экрана прописывается в переменной KV


class RegisterForm(Screen):

    # Функция, вызываемая перед непосредственным переходом на этот экран
    def on_pre_enter(self, *args):
        pass

    # 2 текстовые переменные, хранящие данные текст и подсказку к нему

    text = StringProperty()
    hint_text = StringProperty()

    # Функция, вызываемая при обратном переходе на окна ввода логина/пароля

    def go_back_to_login_page(self):

        # Очищаем поля логина и пародя на экране формы логина

        self.manager.get_screen("LoginForm").ids.login_field.text = ""
        self.manager.get_screen("LoginForm").ids.password_field.text = ""

        # Очищаем поля логина и пароля на экране формы регистрации

        self.ids.register_login_field.text = ""
        self.ids.register_password_field.text = ""

        # Указываем анимацию перехода; экран, на который нужно совершить переход; и направление перехода

        self.manager.transition = SwapTransition()
        self.manager.current = "LoginForm"
        self.manager.transition.direction = "up"

    # Функция, вызываемая при выборе поля логина

    def select_register_login_field(self):

        # Поле ввода при required = True подсвечивается красным, что сигнализирует об ошибке ввода
        # В данном случае поля возвращается в исходное нормальное положение

        self.ids.register_login_field.required = False

    # Функция, вызываемая при выборе поля пароля

    def select_register_password_field(self):
        self.ids.register_password_field.required = False

    # Функция, вызываемая при проверке данных формы регистрации и уже имеющихся данных в базе данных

    def check_profile_in_database_before_creation(self):

        # Создаем виджет, который будет появляться если пользователь при региистрации не выберет ни одного
        # разрешения на редактирование

        self.snackbar = Snackbar(
            text="[color=#000000]There are no selected permissions! Select at least one to continue![/color]",
            snackbar_x="10dp",
            snackbar_y="10dp",
            bg_color=(1, 1, 1, 1),
        )
        self.snackbar.size_hint_x = (Window.width - (self.snackbar.snackbar_x * 2)) / Window.width
        self.snackbar.buttons = [
            MDFlatButton(
                text="CANCEL",
                text_color="black",
                on_release=self.snackbar.dismiss,
            ),
        ]

        sql_con = sql.connect(os.path.join(os.getcwd(), 'Users.sqlite3'))
        sql_cursor = sql_con.cursor()

        sql_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Users';")
        tb_name = sql_cursor.fetchall()

        # Если таблицы в базе нет, то создаем ее

        if len(tb_name) == 0:
            sql_cursor.execute("""
                            CREATE TABLE Users (
                                UserID INTEGER PRIMARY KEY autoincrement,
                                Login varchar(255),
                                Password varchar(255),
                                ChangeFullName varchar(255),
                                ChangeBirthDate varchar(255),
                                ChangeEmail varchar(255)
                                );
                                """)

        # Если в поле логина нет указанных данных

        if not self.ids.register_login_field.text:
            self.ids.register_login_field.required = True
            self.ids.register_login_field.helper_text = "No login entered"
            self.ids.register_login_field.focus = True
            self.ids.register_login_field.focus = False

        # Если в поле пароля нет указанных данных

        if not self.ids.register_password_field.text:
            self.ids.register_password_field.required = True
            self.ids.register_login_field.helper_text = "No password entered"
            self.ids.register_password_field.focus = True
            self.ids.register_password_field.focus = False

        if len(self.ids.register_login_field.text) == 0 and len(self.ids.register_password_field.text) == 0:
            return

        if len(self.ids.register_login_field.text) == 0:
            return

        if len(self.ids.register_password_field.text) == 0:
            return

        # Не выбрано ни одно разрешение

        if not self.ids.nameChange_permission.active \
                and not self.ids.birthdateChange_permission.active \
                and not self.ids.emailChange_permission.active:
            self.snackbar.open()
            return

        # Поиск пользователя по логину

        sql_cursor.execute("SELECT * FROM Users us WHERE Login=?;",
                           (str(self.ids.register_login_field.text),))

        found_data = sql_cursor.fetchall()

        # Если пользователь с таким логином уже существует, то это оотобразиться на экране и
        # новый пользователь создан не будет

        if len(found_data) != 0:
            self.ids.register_login_field.text = ""

            # Поле ввода логина на экране регистрации подсвечивается красным

            self.ids.register_login_field.required = True
            self.ids.register_login_field.helper_text = "Account with this login already exists"
            self.ids.register_login_field.focus = True
            self.ids.register_login_field.focus = False
            return

        # Выгрузка разрешений на редактирование из элементов интерфейса

        name_permission = 1 if self.ids.nameChange_permission.active else 0
        birthdate_permission = 1 if self.ids.birthdateChange_permission.active else 0
        email_permission = 1 if self.ids.emailChange_permission.active else 0

        sql_cursor.execute("SELECT COUNT(*) FROM Users")

        current_id = int(sql_cursor.fetchall()[0][0]) + 1

        # Создание нового пользователя, путем добавления записи в базу данных

        sql_cursor.execute("INSERT INTO Users VALUES (?, ?, ?, ?, ?, ?)",
                           (int(current_id),
                            str(self.ids.register_login_field.text),
                            str(self.ids.register_password_field.text),
                            int(name_permission),
                            int(birthdate_permission),
                            int(email_permission)
                            ))

        sql_con.commit()

        # Создание виджета, сигнализирующего об успешном создании нового аккаунта

        self.snackbar_created_account = Snackbar(
            text="[color=#000000]Account has been successfully created![/color]",
            snackbar_x="10dp",
            snackbar_y="10dp",
            bg_color=(1, 1, 1, 1),
        )
        self.snackbar_created_account.size_hint_x = (Window.width - (
                self.snackbar_created_account.snackbar_x * 2)) / Window.width
        self.snackbar_created_account.buttons = [
            MDFlatButton(
                text="CANCEL",
                text_color="black",
                on_release=self.snackbar_created_account.dismiss,
            ),
        ]

        # Отображение виджета

        self.snackbar_created_account.open()

        # Обнуление всех полей и элементов формы регистрации

        self.ids.register_login_field.text = ""
        self.ids.register_password_field.text = ""
        self.ids.nameChange_permission.active = False
        self.ids.birthdateChange_permission.active = False
        self.ids.emailChange_permission.active = False

        sql_cursor.close()


# Окно Экрана, отвечающее за общую логику окна формы входа по логину и паролю

class LoginFormLayout(Screen):
    # https://stackoverflow.com/questions/58862489/how-can-i-call-an-on-pre-enter-function-in-kivy-for-my-root-screen

    def on_pre_enter(self, *args):
        pass

    text = StringProperty()
    hint_text = StringProperty()

    def select_login_field(self):
        self.ids.login_field.required = False

    def select_password_field(self):
        self.ids.password_field.required = False

    # Функция, срабатывающая при переходе в окна ввода данных для Google Sheets таблицы

    @mainthread
    def enter_app(self):

        # Указываем оконому менеджеру, что переходим в окно формы ввода данных

        self.manager.current = "EditingForm"
        self.manager.duration = "1"

        # Подгружаем данные текущего пользователя из глобальной переменной

        global user_data

        # Указываем полям формы доступ согласно разрешениям текущего пользователя

        self.manager.get_screen("EditingForm").ids.FirstName.disabled = True if user_data[0][3] == "0" else False
        self.manager.get_screen("EditingForm").ids.FamilyName.disabled = True if user_data[0][3] == "0" else False
        self.manager.get_screen("EditingForm").ids.FathersName.disabled = True if user_data[0][3] == "0" else False
        self.manager.get_screen("EditingForm").ids.Birthday_btn.disabled = True if user_data[0][4] == "0" else False
        self.manager.get_screen("EditingForm").ids.Email.disabled = True if user_data[0][5] == "0" else False
        self.manager.get_screen("EditingForm").ids.save_record_btn.disabled = False

    # Функция, запускающая отображения виджета, в случае если пользователь не будет найден

    @mainthread
    def draw_snackbar(self):
        self.snackbar.open()

    # Функция начала поиска текущего аккаунта пользователя в базе данных (занимается только отображением анимации)

    def start_to_search(self):

        # Создание виджета загрузки с символом базы данных по середине

        self.dialog = MDDialog(title="Checking user in database",
                               text="Loading",
                               type="custom",
                               content_cls=DatabaseCheckDialogContent())

        # Открытие внетреннего окна

        self.dialog.open()

        # Создание виджета всплывающего текста снизу приложения, появляется если пользователь не найден

        self.snackbar = Snackbar(
            text="[color=#000000]Wrong Login and/or Password has/have been entered![/color]",
            snackbar_x="10dp",
            snackbar_y="10dp",
            bg_color=(1, 1, 1, 1),
        )
        self.snackbar.size_hint_x = (Window.width - (self.snackbar.snackbar_x * 2)) / Window.width
        self.snackbar.buttons = [
            MDFlatButton(
                text="CANCEL",
                text_color="black",
                on_release=self.snackbar.dismiss,
            ),
        ]

        # Создание и запуск нового потока, в котором будут подгружены данные из базы данных
        # Новый поток требуется, чтобы интерфейс не завис на момент поиска пользователя

        loading_thread = Thread(target=loading_from_database_wait, args=(self, self.dialog, 1.0,))
        loading_thread.start()

    # Функция перехода на экран формы создания нового пользователя (срабатывает по нажатию на кнопку)

    def register_new_profile(self):
        self.manager.transition = SwapTransition()
        self.manager.transition.direction = "up"
        self.manager.current = "RegisterForm"
        self.manager.duration = "1"

    # Функция, выполняющая проверку введены ли данные логина и пароля в соответсвующие поля
    # Функция выполяется перед поиском пользователя в базе данных

    def search_for_profile(self):
        self.dialog = None

        if not self.ids.login_field.text:

            # Поле ввода логина подсвечивается красным

            self.ids.login_field.required = True
            self.ids.login_field.focus = True
            self.ids.login_field.focus = False

        if not self.ids.password_field.text:

            # Поле ввода пароля подсвечивается красным

            self.ids.password_field.required = True
            self.ids.password_field.focus = True
            self.ids.password_field.focus = False

        # Если оба поля заполнены, то запускается функция анимации поиска пользователя, а вместе с ней и поиск в базе

        if len(self.ids.login_field.text) != 0 and len(self.ids.password_field.text) != 0:
            self.start_to_search()


# Класс основного приложения Kivy, в котором происходит рендер всего интерфейса из переменной KV


class App_Created_by_IgorVeshkinApp(MDApp):
    def build(self):
        return Builder.load_string(KV)


# Запуск приложения

if __name__ == "__main__":
    App_Created_by_IgorVeshkinApp().run()
