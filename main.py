from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.core.text import LabelBase
from kivy.utils import get_color_from_hex
import requests
import json
from kivy.clock import Clock

LabelBase.register(name='Roboto',
                   fn_regular='Roboto-Regular.ttf',
                   fn_bold='Roboto-Bold.ttf')
LabelBase.register(name='EpsonMX',
                   fn_regular='EpsonMxSeriesDmp-ZVRG8.ttf')

class CryptoApp(App):
    def build(self):
        self.b = BoxLayout(orientation='vertical')

        banner = Image(source='logo.png', size_hint_x=1, size_hint_y=0.1)
        self.b.add_widget(banner)

        self.cap_label = Label(text="", size_hint_x=1, size_hint_y=0.1, font_name='EpsonMX', font_size=71, color=get_color_from_hex("#FF0000"))
        self.b.add_widget(self.cap_label)

        self.crypto_box = BoxLayout(orientation='vertical', size_hint_y=None)
        self.crypto_box.bind(minimum_height=self.crypto_box.setter('height'))
        scroll_view = ScrollView(size_hint=(1, 0.8), do_scroll_x=False)
        scroll_view.add_widget(self.crypto_box)
        self.b.add_widget(scroll_view)

        # Initialize label scrolling logic
        self.temp_text = ""
        self.text_length = 0
        self.index = 0

        Clock.schedule_interval(self.update_label, 0.2)  # Update label text every 0.2 seconds
        Clock.schedule_interval(self.update_prices, 60)  # Update prices every 1 minute
        self.update_prices()

        return self.b

    def update_label(self, dt):
        self.cap_label.text = self.temp_text[self.index:self.index + 15]
        self.index += 1

        if self.index >= self.text_length:
            self.index = 0

    def update_prices(self, touch=None):
        response = requests.get('https://api.coinlore.net/api/tickers/')
        data = json.loads(response.text)

        def format_market_cap(market_cap):
            try:
                market_cap = float(market_cap)
            except ValueError:
                # Se non è possibile convertire in float, ritorna una stringa vuota
                return ""
            if market_cap >= 1e12:
                return f"{market_cap / 1e12:.0f}T"
            elif market_cap >= 1e9:
                return f"{market_cap / 1e9:.0f}B"
            elif market_cap >= 1e6:
                return f"{market_cap / 1e6:.0f}M"
            elif market_cap >= 1e3:
                return f"{market_cap / 1e3:.0f}K"
            else:
                return f"{market_cap:.0f}"

        response = requests.get('https://api.coinlore.net/api/tickers/')
        data = json.loads(response.text)

        # Estrai le prime tre criptovalute e le relative capitalizzazioni di mercato
        top_3_crypto = data['data'][:20]
        market_caps = [crypto['market_cap_usd'] for crypto in top_3_crypto]
        names = [crypto['name'] for crypto in top_3_crypto]

        formatted_caps = [format_market_cap(market_cap) for market_cap in market_caps]
        label_text = ", ".join([f"{name} ${formatted_cap}" for name, formatted_cap in zip(names, formatted_caps)])
        self.cap_label.text = f"Market cap: {label_text}"
        self.temp_text = self.cap_label.text + ' ' + self.cap_label.text
        self.text_length = len(self.cap_label.text)

        # Clear existing crypto rows
        self.crypto_box.clear_widgets()

        for crypto in data['data']:
            name = crypto['name']
            symbol = crypto['symbol']
            price = crypto['price_usd']
            percent_24 = crypto['percent_change_24h']
            market_cap = crypto['market_cap_usd']
            
        
            # Crea un BoxLayout orizzontale per ogni riga
            crypto_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
        
            # Label per nome, simbolo e prezzo
            crypto_label = Label(text=f"{symbol}: ${price}",
                                 font_name='Roboto',
                                 font_size=51,
                                 color=get_color_from_hex("#FFFFFF"))

        
            # Determina il colore in base al valore di percent_24
            if float(percent_24) >= 0:
                color_code = get_color_from_hex("#00FF00")  # Verde
            else:
                color_code = get_color_from_hex("#FF0000")  # Rosso
            
            # Label per la percentuale di cambio
            percent_label = Label(text=f"[{percent_24}%] 24H",
                                  font_name='Roboto',
                                  font_size=45,
                                  color=color_code)
        
            # Aggiungi entrambe le Label al BoxLayout della riga
            crypto_row.add_widget(crypto_label)
            crypto_row.add_widget(percent_label)
        
            # Aggiungi il BoxLayout della riga al layout principale
            self.crypto_box.add_widget(crypto_row)      
if __name__ == '__main__':
    CryptoApp().run()
