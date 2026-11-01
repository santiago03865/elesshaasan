"""
КАЛЬКУЛЯТОР ВАЛЮТ "DUSHENKA"
============================
Приложение для конвертации валют с реальными курсами (API open.er-api.com).
"""

import json
import os
import re
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.modalview import ModalView
from kivy.uix.widget import Widget
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

# =============================================================================
# ★★★ РАЗМЕР ОКНА ПРИЛОЖЕНИЯ ★★★
# =============================================================================
Window.size = (400, 780)
Window.clearcolor = get_color_from_hex("#3A3C3C")  

# =============================================================================
# ЦВЕТОВАЯ ПАЛИТРА
# =============================================================================
COLOR_BG_CARD = get_color_from_hex("#6A6A6AFF")      
COLOR_BORDER = get_color_from_hex("#000000FF")       
COLOR_TEXT_MAIN = get_color_from_hex("#050505FF")    
COLOR_TEXT_SUB = get_color_from_hex("#010101FF")     
COLOR_INPUT_BG = get_color_from_hex("#FBFBFEFF")     
COLOR_RESULT_BG = get_color_from_hex("#EFF6EFFF")    
COLOR_BLACK_RGBA = [0, 0, 0, 1]                      

COLOR_PRIMARY = get_color_from_hex("#FFFFFFFF")      
COLOR_SECONDARY = get_color_from_hex('#03DAC6FF')    
COLOR_SUCCESS = get_color_from_hex("#000000FF")      
COLOR_ERROR = get_color_from_hex("#FFFFFFFF")        

COLOR_BTN_FROM = get_color_from_hex("#FCFCFCFF")
COLOR_BTN_TO = get_color_from_hex('#FCFCFCFF')
COLOR_BTN_SWAP = get_color_from_hex("#FCFCFCFF")
COLOR_BTN_REFRESH = get_color_from_hex('#00E676FF')
COLOR_BTN_CLEAR = get_color_from_hex('#FF5252FF')
COLOR_BTN_COPY = get_color_from_hex('#6A6A6AFF')
COLOR_BTN_CANCEL = get_color_from_hex('#444444FF')
COLOR_BTN_SELECTED = get_color_from_hex("#717171FF")
COLOR_BTN_UNSELECTED = get_color_from_hex("#FFFFFFFF")

# =============================================================================
# ★★★ НАСТРОЙКИ КНОПОК ★★★
# =============================================================================
BTN_FROM_SIZE = (dp(70), dp(70))    
BTN_FROM_FONT = dp(18)              
BTN_TO_SIZE = (dp(70), dp(70))      
BTN_TO_FONT = dp(18)                
BTN_SWAP_SIZE = (dp(70), dp(50))    
BTN_SWAP_FONT = dp(24)              
BTN_REFRESH_SIZE = (None, dp(45))   
BTN_REFRESH_FONT = dp(14)           
BTN_CLEAR_SIZE = (None, dp(45))     
BTN_CLEAR_FONT = dp(14)             
BTN_COPY_FONT = dp(10)              
BTN_CANCEL_HEIGHT = dp(45)          
BTN_CANCEL_FONT = dp(16)            
BTN_CURRENCY_HEIGHT = dp(50)        
BTN_CURRENCY_FONT = dp(16)          

HISTORY_FILE = 'exchange_history_ru.json'
RATES_CACHE_FILE = 'rates_cache_ru.json'

CURRENCY_INFO_RU = {
    'USD': ('США', 'Доллар США'), 'EUR': ('Евросоюз', 'Евро'),
    'GBP': ('Великобритания', 'Фунт стерлингов'), 'JPY': ('Япония', 'Иена'),
    'CNY': ('Китай', 'Юань'), 'RUB': ('Россия', 'Рубль'),
    'KZT': ('Казахстан', 'Тенге'), 'UAH': ('Украина', 'Гривна'),
    'BYN': ('Беларусь', 'Белорусский рубль'), 'TRY': ('Турция', 'Лира'),
    'INR': ('Индия', 'Рупия'), 'AUD': ('Австралия', 'Австралийский доллар'),
    'CAD': ('Канада', 'Канадский доллар'), 'CHF': ('Швейцария', 'Франк'),
    'SGD': ('Сингапур', 'Сингапурский доллар'), 'HKD': ('Гонконг', 'Гонконгский доллар'),
    'NZD': ('Новая Зеландия', 'Новозеландский доллар'), 'THB': ('Таиланд', 'Бат'),
    'MYR': ('Малайзия', 'Ринггит'), 'IDR': ('Индонезия', 'Рупия'),
    'PHP': ('Филиппины', 'Песо'), 'VND': ('Вьетнам', 'Донг'),
    'ZAR': ('ЮАР', 'Рэнд'), 'NGN': ('Нигерия', 'Наира'),
    'EGP': ('Египет', 'Фунт'), 'ILS': ('Израиль', 'Шекель'),
    'AED': ('ОАЭ', 'Дирхам'), 'QAR': ('Катар', 'Риал'),
    'SAR': ('Саудовская Аравия', 'Риал'), 'BRL': ('Бразилия', 'Реал'),
    'ARS': ('Аргентина', 'Песо'), 'CLP': ('Чили', 'Песо'),
    'MXN': ('Мексика', 'Песо'), 'COP': ('Колумбия', 'Песо'),
    'PEN': ('Перу', 'Соль'), 'PLN': ('Польша', 'Злотый'),
    'CZK': ('Чехия', 'Крона'), 'SEK': ('Швеция', 'Крона'),
    'NOK': ('Норвегия', 'Крона'), 'DKK': ('Дания', 'Крона'),
    'RON': ('Румыния', 'Лей'), 'HUF': ('Венгрия', 'Форинт'),
    'BGN': ('Болгария', 'Лев'), 'ISK': ('Исландия', 'Крона'),
    'GEL': ('Грузия', 'Лари'), 'AMD': ('Армения', 'Драм'),
    'AZN': ('Азербайджан', 'Манат'), 'UZS': ('Узбекистан', 'Сом'),
    'TJS': ('Таджикистан', 'Сомони'), 'KGS': ('Кыргызстан', 'Сом'),
    'MNT': ('Монголия', 'Тугрик'), 'LKR': ('Шри-Ланка', 'Рупия'),
    'BDT': ('Бангладеш', 'Така'), 'PKR': ('Пакистан', 'Рупия'),
    'IRR': ('Иран', 'Риал'), 'IQD': ('Ирак', 'Динар'),
    'JOD': ('Иордания', 'Динар'), 'LBP': ('Ливан', 'Фунт'),
    'KWD': ('Кувейт', 'Динар'), 'OMR': ('Оман', 'Риал'),
    'BHD': ('Бахрейн', 'Динар'),
}


class BorderedTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.border_line = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.5)
        self.bind(pos=self._update_border, size=self._update_border)

    def _update_border(self, *args):
        if hasattr(self, 'border_line'):
            self.border_line.rectangle = (self.x, self.y, self.width, self.height)


class StyledCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=dp(15), spacing=dp(12), **kwargs)
        with self.canvas.before:
            Color(*COLOR_BG_CARD)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            Color(*COLOR_BORDER)
            self.border_line = Line(rectangle=(self.x+1, self.y+1, self.width-2, self.height-2), width=1)
        self.bind(pos=self._update_visuals, size=self._update_visuals)

    def _update_visuals(self, *args):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
            self.border_line.rectangle = (self.x+1, self.y+1, self.width-2, self.height-2)


class ResultCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=dp(12), spacing=dp(5), **kwargs)
        with self.canvas.before:
            Color(*COLOR_RESULT_BG)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            Color(*COLOR_SUCCESS)
            self.border_line = Line(rectangle=(self.x+1, self.y+1, self.width-2, self.height-2), width=1.5)
        self.bind(pos=self._update_visuals, size=self._update_visuals)

    def _update_visuals(self, *args):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
            self.border_line.rectangle = (self.x+1, self.y+1, self.width-2, self.height-2)


class CurrencySelector(ModalView):
    def __init__(self, currencies_dict, selected_code, callback, **kwargs):
        super().__init__(auto_dismiss=True, background_color=[0, 0, 0, 0.8], **kwargs)
        self.currencies = currencies_dict
        self.selected_code = selected_code
        self.callback = callback
        
        container = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        title_lbl = Label(text="Выберите валюту", font_size=dp(18), color=COLOR_PRIMARY, bold=True, size_hint_y=0.1)
        container.add_widget(title_lbl)
        
        search_input = TextInput(hint_text='Поиск страны или кода...', multiline=False, 
                                 font_size=dp(16), background_normal='', 
                                 background_color=COLOR_INPUT_BG, foreground_color=COLOR_TEXT_MAIN)
        search_input.bind(text=self.filter_list)
        container.add_widget(search_input)
        
        scroll = ScrollView(size_hint_y=12)
        self.list_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        scroll.add_widget(self.list_layout)
        container.add_widget(scroll)
        
        close_btn = Button(text='Отмена', size_hint_y=None, height=BTN_CANCEL_HEIGHT,  
                           font_size=BTN_CANCEL_FONT, background_color=COLOR_BTN_CANCEL, 
                           color=COLOR_TEXT_MAIN, bold=True)
        close_btn.bind(on_press=self.dismiss)
        container.add_widget(close_btn)
        
        self.add_widget(container)
        self.refresh_list(currencies_dict)

    def _get_display_name(self, code):
        if code in CURRENCY_INFO_RU:
            country, name = CURRENCY_INFO_RU[code]
            return f"{country} ({code}) - {name}"
        return f"Неизвестно ({code})"

    def refresh_list(self, data):
        self.list_layout.clear_widgets()
        available_codes = list(data.keys())
        known_items = [c for c in available_codes if c in CURRENCY_INFO_RU]
        unknown_items = [c for c in available_codes if c not in CURRENCY_INFO_RU]
        known_items.sort(key=lambda c: CURRENCY_INFO_RU[c][0])
        unknown_items.sort()
        for code in known_items + unknown_items:
            self._add_currency_button(code)

    def filter_list(self, instance, value):
        query = value.lower().strip()
        if not query:
            self.refresh_list(self.currencies)
            return
        filtered_codes = []
        for code in self.currencies.keys():
            if query in code.lower() or (code in CURRENCY_INFO_RU and (query in CURRENCY_INFO_RU[code][0].lower() or query in CURRENCY_INFO_RU[code][1].lower())):
                filtered_codes.append(code)
        known_filtered = sorted([c for c in filtered_codes if c in CURRENCY_INFO_RU], key=lambda c: CURRENCY_INFO_RU[c][0])
        unknown_filtered = sorted([c for c in filtered_codes if c not in CURRENCY_INFO_RU])
        self.rebuild_list_ui(known_filtered + unknown_filtered)

    def rebuild_list_ui(self, codes_list):
        self.list_layout.clear_widgets()
        for code in codes_list:
            self._add_currency_button(code)

    def _add_currency_button(self, code):
        is_selected = (code == self.selected_code)
        bg_col = COLOR_BTN_SELECTED if is_selected else COLOR_BTN_UNSELECTED
        txt_col = COLOR_BLACK_RGBA if is_selected else COLOR_TEXT_MAIN
        btn = Button(text=self._get_display_name(code), halign='left', valign='middle',
                     size_hint_y=None, height=BTN_CURRENCY_HEIGHT, font_size=BTN_CURRENCY_FONT,  
                     background_color=bg_col, color=txt_col, text_size=(dp(320), None), bold=is_selected)
        btn.code = code
        btn.bind(on_release=self.select_currency)
        self.list_layout.add_widget(btn)

    def select_currency(self, instance):
        self.callback(instance.code)
        self.dismiss()


class ExchangeApp(App):
    def build(self):
        self.title = 'FX Pro Calculator'
        
        root_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        header = Label(text="DUSHENKA", markup=True, font_size=dp(22), color=COLOR_PRIMARY, size_hint_y=0.08, bold=True)
        root_layout.add_widget(header)
        
        sep1 = BoxLayout(size_hint_y=0.01, orientation='horizontal')
        with sep1.canvas.after:
            Color(*COLOR_BORDER)
            Line(points=[sep1.x, sep1.y, sep1.right, sep1.y], width=1)
        root_layout.add_widget(sep1)

        calc_card = StyledCard(size_hint_y=0.45)
        
        amount_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(70))
        
        self.amount_input = BorderedTextInput(hint_text='Введите сумму', 
                                      font_size=dp(28), font_name='Roboto-Bold', multiline=False,
                                      background_color=COLOR_INPUT_BG, foreground_color=COLOR_TEXT_MAIN, 
                                      cursor_color=COLOR_PRIMARY, background_normal='', padding=[10, 10], size_hint_x=1)
        self.amount_input.bind(text=self.format_input_field)
        self.amount_input.bind(text=self.calculate_result)
        amount_row.add_widget(self.amount_input)
        
        self.from_currency = 'USD'
        self.from_btn = Button(text=f'{self.from_currency}', font_size=BTN_FROM_FONT,  
                               background_color=COLOR_BTN_FROM, color=COLOR_BLACK_RGBA, bold=True, 
                               size_hint=(None, None), size=BTN_FROM_SIZE)  
        self.from_btn.bind(on_press=lambda x: self.open_selector('from'))
        amount_row.add_widget(self.from_btn)
        calc_card.add_widget(amount_row)
        
        swap_row = BoxLayout(size_hint_y=None, height=BTN_SWAP_SIZE[1], orientation='horizontal')
        swap_row.add_widget(Widget(size_hint_x=1))
        
        self.swap_btn = Button(text='<—>', font_size=BTN_SWAP_FONT, background_color=COLOR_BTN_SWAP, 
                               color=COLOR_BLACK_RGBA, bold=True, size_hint=(None, None), size=BTN_SWAP_SIZE)  
        self.swap_btn.bind(on_press=self.swap_currencies)
        swap_row.add_widget(self.swap_btn)
        swap_row.add_widget(Widget(size_hint_x=0.005))
        calc_card.add_widget(swap_row)
        
        result_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(70))
        self.result_card = ResultCard(size_hint_x=1)
        
        self.result_label = Label(text='0', font_size=dp(28), color=COLOR_SUCCESS, halign='left', valign='middle', bold=True)
        self.result_label.bind(size=self.result_label.setter('text_size'))
        self.result_card.add_widget(self.result_label)
        
        self.rate_detail_label = Label(text="", font_size=dp(12), color=COLOR_TEXT_SUB, halign='left', valign='top')
        self.rate_detail_label.bind(size=self.rate_detail_label.setter('text_size'))
        self.result_card.add_widget(self.rate_detail_label)
        result_row.add_widget(self.result_card)
        
        self.to_currency = 'RUB'
        self.to_btn = Button(text=f'{self.to_currency}', font_size=BTN_TO_FONT, background_color=COLOR_BTN_TO, 
                             color=COLOR_BLACK_RGBA, bold=True, size_hint=(None, None), size=BTN_TO_SIZE)  
        self.to_btn.bind(on_press=lambda x: self.open_selector('to'))
        result_row.add_widget(self.to_btn)
        calc_card.add_widget(result_row)
        
        self.rate_info_label = Label(text="Загрузка данных...", font_size=dp(12), color=COLOR_TEXT_SUB, halign='center', size_hint_y=0.2)
        self.rate_info_label.bind(size=self.rate_info_label.setter('text_size'))
        calc_card.add_widget(self.rate_info_label)
        root_layout.add_widget(calc_card)
        
        history_header = Label(text="ИСТОРИЯ ОПЕРАЦИЙ", markup=True, font_size=dp(14), color=COLOR_TEXT_SUB, size_hint_y=0.05, bold=True)
        root_layout.add_widget(history_header)
        
        history_scroll = ScrollView(size_hint_y=0.35)
        self.history_grid = GridLayout(cols=1, spacing=dp(2), size_hint_y=None)
        self.history_grid.bind(minimum_height=self.history_grid.setter('height'))
        history_scroll.add_widget(self.history_grid)
        root_layout.add_widget(history_scroll)
        
        control_panel = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        refresh_btn = Button(text='ОБНОВИТЬ', background_color=COLOR_BTN_REFRESH, color=COLOR_BLACK_RGBA, 
                             font_size=BTN_REFRESH_FONT, bold=True, size_hint=(1, None), height=BTN_REFRESH_SIZE[1])  
        refresh_btn.bind(on_press=self.fetch_rates)
        
        clear_hist_btn = Button(text='ОЧИСТИТЬ', background_color=COLOR_BTN_CLEAR, color=COLOR_BLACK_RGBA, 
                                font_size=BTN_CLEAR_FONT, bold=True, size_hint=(1, None), height=BTN_CLEAR_SIZE[1])  
        clear_hist_btn.bind(on_press=self.clear_history)
        
        control_panel.add_widget(refresh_btn)
        control_panel.add_widget(clear_hist_btn)
        root_layout.add_widget(control_panel)

        self.rates = {}
        self.currency_names = {}
        self.load_local_data()
        Clock.schedule_once(lambda dt: self.fetch_rates(None), 0.5)
        
        return root_layout

    def load_local_data(self):
        try:
            if os.path.exists(RATES_CACHE_FILE):
                with open(RATES_CACHE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.rates = data.get('rates', {})
                    self.currency_names = {code: code for code in self.rates.keys()}
        except Exception as e:
            print(f"Load error: {e}")

    def save_rates_to_disk(self):
        try:
            with open(RATES_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump({'rates': self.rates}, f)
        except Exception as e:
            print(f"Save error: {e}")

    def fetch_rates(self, instance):
        self.rate_info_label.text = "Обновление..."
        url = "https://open.er-api.com/v6/latest/USD"
        UrlRequest(url, on_success=self.on_rates_loaded, on_error=self.on_rates_error)

    def on_rates_loaded(self, req, result):
        try:
            if result.get('result') == 'success':
                self.rates = result['rates']
                self.currency_names = {code: code for code in self.rates.keys()}
                self.save_rates_to_disk()
                self.rate_info_label.text = f"Обновлено: {datetime.now().strftime('%H:%M:%S')}"
                self.rate_info_label.color = COLOR_SUCCESS
                self.calculate_result()
            else:
                raise ValueError("API Error")
        except Exception as e:
            self.on_rates_error(req, str(e))

    def on_rates_error(self, req, error):
        self.rate_info_label.text = "Ошибка сети / Использование кэша"
        self.rate_info_label.color = COLOR_ERROR
        if not self.rates:
             self.rates = {'USD': 1.0, 'EUR': 0.92, 'RUB': 90.0}
             self.currency_names = {'USD': 'USD', 'EUR': 'EUR', 'RUB': 'RUB'}

    def format_input_field(self, instance, value):
        """Форматирует ввод: 555,486,595 или 343,698,669.54 (без .00 у целых)"""
        if not value:
            return

        # Запоминаем позицию курсора, чтобы он не прыгал в конец при форматировании
        cursor_col = instance.cursor_col
        
        # Очищаем от всего, кроме цифр и точки
        clean = value.replace(',', '').replace(' ', '')
        
        # Оставляем только одну точку
        parts = clean.split('.')
        if len(parts) > 2:
            clean = parts[0] + '.' + ''.join(parts[1:])
            
        # Удаляем все буквы и символы, кроме цифр и одной точки
        clean_raw = ""
        dot_seen = False
        for char in clean:
            if char.isdigit():
                clean_raw += char
            elif char == '.' and not dot_seen:
                clean_raw += char
                dot_seen = True
                
        if not clean_raw or clean_raw == '.':
            if instance.text != clean_raw:
                instance.text = clean_raw
                instance.cursor = (0, len(clean_raw))
            return

        try:
            parts = clean_raw.split('.')
            # Форматируем целую часть с запятыми: 343698669 -> 343,698,669
            whole_formatted = f"{int(parts[0]):,}"
            
            if len(parts) > 1:
                # Если есть дробная часть, добавляем точку и до 2 цифр (343,698,669.54)
                decimal_part = parts[1][:2]
                formatted = f"{whole_formatted}.{decimal_part}"
            else:
                # Если дробной части нет, просто целое число с запятыми (555,486,595)
                formatted = whole_formatted
            
            if instance.text != formatted:
                instance.text = formatted
                # Корректируем позицию курсора с учетом добавленных/удаленных запятых
                diff = len(formatted) - len(value)
                new_cursor = max(0, min(cursor_col + diff, len(formatted)))
                instance.cursor = (0, new_cursor)
                
        except ValueError:
            pass

    def format_number(self, value):
        """Форматирует вывод: 555,486,595 или 343,698,669.54"""
        abs_value = abs(value)
        if abs_value >= 1e11 or (abs_value < 1e-4 and abs_value != 0):
            return f"{value:.4e}"
        
        # Если число целое, убираем .00 и ставим запятые для тысяч
        if value.is_integer():
            return f"{int(value):,}"
        else:
            # Если дробное, ставим запятые для тысяч и точку для дробной части
            return f"{value:,.2f}"

    def calculate_result(self, *args):
        try:
            amount_str = self.amount_input.text.strip()
            if not amount_str or amount_str == '.':
                self.result_label.text = '0'
                self.rate_detail_label.text = ''
                return
            
            # Удаляем запятые и пробелы для корректного преобразования в float
            clean_str = amount_str.replace(',', '').replace(' ', '')
            amount = float(clean_str)
            
            if self.from_currency not in self.rates or self.to_currency not in self.rates:
                self.result_label.text = 'Ошибка'
                self.rate_detail_label.text = 'Валюта недоступна'
                return

            usd_amount = amount / self.rates[self.from_currency]
            final_amount = usd_amount * self.rates[self.to_currency]
            
            formatted_val = self.format_number(final_amount)
            self.result_label.text = formatted_val
            
            rate_value = self.rates[self.to_currency] / self.rates[self.from_currency]
            self.rate_detail_label.text = f"Курс: 1 {self.from_currency} = {self.format_number(rate_value)} {self.to_currency}"
            
            if amount > 0:
                self.log_transaction(amount, self.from_currency, final_amount, self.to_currency)

        except ValueError:
            self.result_label.text = 'Неверно'
            self.rate_detail_label.text = 'Введите число'
        except ZeroDivisionError:
            self.result_label.text = 'Инфинити'
        except Exception as e:
            print(f"Calc error: {e}")
            self.result_label.text = 'Ошибка'

    def swap_currencies(self, instance):
        temp_cur = self.from_currency
        self.from_currency = self.to_currency
        self.to_currency = temp_cur
        self.from_btn.text = self.from_currency
        self.to_btn.text = self.to_currency
        self.calculate_result()

    def open_selector(self, direction):
        if not self.currency_names:
            self.rate_info_label.text = "Нет данных!"
            return
        current_sel = self.from_currency if direction == 'from' else self.to_currency
        selector = CurrencySelector(
            currencies_dict=self.currency_names,
            selected_code=current_sel,
            callback=lambda code: self.set_currency(direction, code)
        )
        selector.open()

    def set_currency(self, direction, code):
        if direction == 'from':
            self.from_currency = code
            self.from_btn.text = code
        else:
            self.to_currency = code
            self.to_btn.text = code
        self.calculate_result()

    def log_transaction(self, amt_in, cur_in, amt_out, cur_out):
        entry = {
            "time": datetime.now().strftime("%d.%m %H:%M"),
            "in_amount": self.format_number(amt_in),
            "in_cur": cur_in,
            "out_amount": self.format_number(amt_out),
            "out_cur": cur_out,
            "raw_out": amt_out
        }
        history = []
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                history = []
        history.insert(0, entry)
        history = history[:15]
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f)
        except:
            pass
        self.render_history(history)

    def render_history(self, history_list):
        self.history_grid.clear_widgets()
        if not history_list:
            lbl = Label(text="История пуста.", color=COLOR_TEXT_SUB, font_size=dp(14))
            self.history_grid.add_widget(lbl)
            return

        for i, item in enumerate(history_list):
            row = BoxLayout(size_hint_y=None, height=dp(65), spacing=dp(5), padding=dp(5))
            time_lbl = Label(text=item['time'], size_hint_x=0.22, font_size=dp(12), color=COLOR_TEXT_SUB,
                             halign='left', valign='middle')
            time_lbl.bind(size=time_lbl.setter('text_size'))
            
            conv_box = BoxLayout(orientation='vertical', size_hint_x=0.53, spacing=dp(2))
            line1_lbl = Label(text=f"{item['in_amount']} {item['in_cur']}",
                              font_size=dp(13), color=COLOR_TEXT_MAIN, halign='left', valign='bottom')
            line1_lbl.bind(size=line1_lbl.setter('text_size'))
            line2_lbl = Label(text=f"{item['out_amount']} {item['out_cur']}",
                              font_size=dp(13), color=COLOR_SUCCESS, halign='left', valign='top')
            line2_lbl.bind(size=line2_lbl.setter('text_size'))
            conv_box.add_widget(line1_lbl)
            conv_box.add_widget(line2_lbl)
            
            copy_btn = Button(text="КОПИРОВАТЬ", size_hint_x=0.22, background_color=COLOR_BTN_COPY, 
                              color=COLOR_BLACK_RGBA, font_size=BTN_COPY_FONT, bold=True)
            copy_btn.out_value = str(item['raw_out'])
            copy_btn.bind(on_press=self.copy_to_clipboard)
            
            row.add_widget(time_lbl)
            row.add_widget(conv_box)
            row.add_widget(copy_btn)
            self.history_grid.add_widget(row)

    def copy_to_clipboard(self, instance):
        from kivy.core.clipboard import Clipboard
        Clipboard.copy(instance.out_value)
        old_text = instance.text
        instance.text = "ГОТОВО"
        Clock.schedule_once(lambda dt: setattr(instance, 'text', old_text), 1.5)

    def clear_history(self, instance):
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        self.render_history([])

if __name__ == '__main__':
    ExchangeApp().run()
