from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from classes.database import Database, Zamestnanec, Kategorie
# Import aplikačního
from kivy.app import App
# Importy Kivy komponent
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
# Importy potřebných MD komponent
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton, MDFillRoundFlatIconButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, ImageLeftWidget, IconRightWidget, ThreeLineIconListItem, \
    ThreeLineAvatarListItem, IconLeftWidget
from kivymd.uix.menu import MDDropdownMenu


class ZamestnanecContent(BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)


class FirmaContent(BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)


class FirmaDialog(MDDialog):
    def __init__(self, id, *args, **kwargs):
        super(FirmaDialog, self).__init__(
            type="custom",
            content_cls=FirmaContent(),
            title='Nová firma',
            text='Zadejte text',
            size_hint=(.8, 1),
            buttons=[
                MDFlatButton(text='Save', on_release=self.save_dialog),
                MDFlatButton(text='Cancel', on_release=self.cancel_dialog)
            ]
        )
        self.id = id

    def save_dialog(self, *args):
        # Slovník, ve kterém budou údaje z dialogu
        app = App.get_running_app()
        zamestnanec = {}
        zamestnanec['nazev'] = self.content_cls.ids.nazev.text
        zamestnanec['odvetvi'] = self.content_cls.ids.odvetvi.text
        zamestnanec['misto'] = self.content_cls.ids.misto.text
        zamestnanec['tel'] = self.content_cls.ids.tel.text
        if self.id:
            zamestnanec['id']=self.id
            app.firma.db.update(zamestnanec)
        else:
            app.firma.db.create_firma(zamestnanec)
        self.dismiss() # zavření dialogového okna

    def cancel_dialog(self, *args):
        self.dismiss()


class DialogZamestnance(MDDialog):
    def __init__(self, id, *args, **kwargs):
        zamestnanec = Zamestnanec()
        super(DialogZamestnance, self).__init__(
            type="custom",
            content_cls=ZamestnanecContent(),
            title="Aktualizace zaměstnance",
            text="Dialog zaměstnance",
            size_hint=(.8, 1),
            buttons=[
                MDFlatButton(text='Uložit', on_release=self.save_dialog),
                MDFlatButton(text='Zavřít', on_release=self.cancel_dialog)
            ]
        )
        self.id = id

    def save_dialog(self, *args):
        # Slovník, ve kterém budou údaje z dialogu
        app = App.get_running_app()
        zamestnanec = {}
        zamestnanec['jmeno'] = self.content_cls.ids.jmeno.text
        zamestnanec['pozice'] = self.content_cls.ids.pozice.text
        zamestnanec['firma'] = self.content_cls.ids.firma.text
        if self.id:
            zamestnanec['id']=self.id
            app.zamestnanci.db.update()
        else:
            app.zamestnanci.db.create_zamestnanec(zamestnanec)
        self.dismiss() # zavření dialogového okna

    def cancel_dialog(self, *args):
        self.dismiss()


class UdajeZamestnanec(BoxLayout):
    def __init__(self, id, *args, **kwargs):
        super().__init__(**kwargs)
        if id:
            zamestnanec = vars(app.zamestnanci.database.read_zamestnanec_by_id(id))
        else:
            zamestnanec = {"id":"", "jmeno":"","pozice":"","firma":""}

        self.ids.zamestnanec_jmeno.text = zamestnanec['jmeno']
        firmy = app.zamestnanci.database.read_firma()
        menu_items = [{"viewclass": "OneLineListItem", "text": f"{firma.nazev}", "on_release": lambda x=f"{firma.nazev}": self.set_item(x)} for firma in firmy]
        self.menu_firmy = MDDropdownMenu(
            caller=self.ids.firma_nazev,
            items=menu_items,
            position="center",
            width_mult=5,
        )
        self.ids.nazev.set_item(zamestnanec['firma'])
        self.ids.pozice.text = zamestnanec['pozice']

    def set_item(self, text_item):
        self.ids.nazev.set_item(text_item)
        self.ids.nazev.text = text_item
        # Zavření menu
        self.menu_firmy.dismiss()


# Třída, která souvisí se zaměstnancem a jeho údaji u databáze
class MyItem(ThreeLineAvatarListItem):
    def __init__(self, item, *args, **kwargs):
        super(MyItem, self).__init__()
        app = App.get_running_app()
        self.id = item.id
        '''if item['titul']:
            self.text = item['titul'] + " " + item['jmeno']
        else:'''
        self.text = item.jmeno
        self.secondary_text = item.pozice
        self.tertiary_text = item.firma.nazev
        self._no_ripple_effect = True
        self.icon = IconLeftWidget(icon="delete", on_release=self.delete)
        self.add_widget(self.icon)

    def on_press(self):
        self.dialog = DialogZamestnance(id=self.id)
        self.dialog.open()

    def delete(self, *args):
        #app.zamestnanci.db.delete_zamestnanec(self.id)
        yes_button = MDFlatButton(text='Ano', on_release=self.yes_btn)
        no_button = MDFlatButton(text='Ne', on_release=self.no_btn)
        self.dialog_confirm = MDDialog(type="confirmation", title='Delete item', text="Opravdu tento záznam chcete smazat?", buttons=[yes_button, no_button])
        self.dialog_confirm.open()

    def yes_btn(self, *args):
        app.zamestnanci.db.delete_zamestnanec(self.id)
        self.dialog_confirm.dismiss()
        self.clear_widgets()

    def no_btn(self, *args):
        self.dialog_confirm.dismiss()


class Employees(BoxLayout):
    def __init__(self, *args, **kwargs):
        super(Employees, self).__init__(orientation="vertical")
        # kontent aplikace
        global app
        app = App.get_running_app()
        rolovaci = ScrollView()
        self.list = MDList()
        self.db = Database(dbtype='sqlite', dbname='firmy.db')
        self.vypis_prepis()
        rolovaci.add_widget(self.list)
        self.add_widget(rolovaci)

        #Tlačítko pro vytvoření nové firmy
        button1 = MDFlatButton()
        button1.text = "NOVÁ FIRMA"
        button1.size_hint = (0, .1)
        button1.font_style = "Button"
        button1.on_release = self.create_firma
        self.add_widget(button1)

        button2 = MDFlatButton()
        button2.text = "NOVÝ ZAMĚSTNANEC"
        button2.size_hint = (0, .1)
        button2.font_style = "Button"
        button2.on_release = self.create_zamestnanec
        self.add_widget(button2)

    def vypis_prepis(self):
        self.list.clear_widgets()
        zamestnanci = self.db.read_all()
        print(zamestnanci)
        for i in zamestnanci:
            self.list.add_widget(MyItem(item=i))

    def create_firma(self):
        self.dialog = FirmaDialog(id=None)
        self.dialog.open()

    def create_zamestnanec(self):
        self.dialog = DialogZamestnance(id=None)
        self.dialog.open()

    def delete_zam(self, id):
        self.db.delete_zamestnanec(id)
        self.vypis_prepis()


class ZamestnanciScreen(Screen):
    pass


class Test(MDApp):

    def build(self):
        self.theme_cls.primary_palette = "Gray"
        builder = Builder.load_file("main.kv")
        self.zamestnanci = Employees()
        builder.ids.navigation.ids.tab_manager.screens[0].add_widget(self.zamestnanci)
        return builder


Test().run()
