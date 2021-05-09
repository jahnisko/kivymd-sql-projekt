'''
Testovací aplikace, zdali databáze funguje, jak má
'''
from database import *

db = Database(dbtype='sqlite', dbname='../firmy.db')


firma = Firma()


firma.nazev = 'Prestar'
firma.ico = 64609219
firma.misto = 'Opava-Vávrovice'
firma.tel_cislo = 553759720
firma.kategorie_id = 2
firma.odvetvi = 'nábytkářský průmysl'
db.create_firma(firma)

print(db.read_firma_by_kategorie('s. r. o.'))



zamestnanec = Zamestnanec()
zamestnanec.jmeno = 'Tereza Procházková'
zamestnanec.pozice = 'sekretářka'
zamestnanec.titul = 'Bc.'
zamestnanec.firma_id = 2
db.create_zamestnanec(zamestnanec)

print(db.read_zamestnanec_by_id(1))
