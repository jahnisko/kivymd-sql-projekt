# Import potřebných knihoven
from sqlalchemy import create_engine, Column, ForeignKey, desc
from sqlalchemy.types import Integer, String, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Globální proměnné
SQLITE = 'sqlite'
MYSQL = 'mysql'


Base = declarative_base()


# Tabulka představující kategorii, do které daná firma spadá (a. s., s. r. o. atd.)


# Tabulka představující údaje o firmě
class Firma(Base):
    __tablename__ = 'firma'

    id = Column(Integer, primary_key=True)
    nazev = Column(String(100), nullable=True)
    kategorie = Column(String(5), nullable=True)
    zamestnanci = relationship('Zamestnanec', backref='firma')


# Tabulka představující údaje o zaměstnanci, který pracuje v dané firmě
class Zamestnanec(Base):
    __tablename__ = 'zamestnanci'

    id = Column(Integer, primary_key=True)
    jmeno = Column(String(30), nullable=False)
    pozice = Column(String(40), nullable=False)
    # Zde přebíráme cizí klíč pro zařazení zaměstnance do firmy
    firma_id = Column(Integer, ForeignKey('firma.id'))


# Třída představující celou databázi
class Database:
    DB_ENGINE = {
        SQLITE: 'sqlite:///{DB}',
        MYSQL: 'mysql+mysqlconnector://{USERNAME}:{PASSWORD}@localhost/{DB}'
    }

    # Konstruktor třídy
    def __init__(self, dbtype='sqlite', username='', password='', dbname='../firmy.db'):
        dbtype = dbtype.lower()

        if dbtype in self.DB_ENGINE.keys():
            engine_url = self.DB_ENGINE[dbtype].format(DB=dbname, USERNAME=username, PASSWORD=password)
            self.engine = create_engine(engine_url, echo=False)
        else:
            print('DBType is not found in DB_ENGINE')

        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    # Metody pro správu databáze (CRUD)
    def create_firma(self, firma):
        try:
            self.session.add(firma)
            self.session.commit()
            return True
        except:
            return False

    def read_all(self, order=Zamestnanec.jmeno):
        try:
            result = self.session.query(Zamestnanec).all()
            return result
        except:
            return False

    def create_zamestnanec(self, zamestnanec):
        try:
            self.session.add(zamestnanec)
            self.session.commit()
            return True
        except:
            return False

    def read_firma(self, order=Firma.nazev):
        try:
            result = self.session.query(Firma).order_by(order).all()
            return result
        except:
            return False

    def read_firma_by_id(self, id):
        try:
            result = self.session.query(Firma).get(id)
            return result
        except:
            return False


    def read_zamestnanec_by_id(self, id):
        try:
            result = self.session.query(Zamestnanec).get(id)
            return result
        except:
            return False

    def update(self):
        try:
            self.session.commit()
            return True
        except:
            return False

    def delete_firma(self, id):
        try:
            firma = self.read_firma_by_id(id)
            self.session.delete(firma)
            self.session.commit()
            return True
        except:
            return False


    def delete_zamestnanec(self, id):
        try:
            zamestnanec = self.read_zamestnanec_by_id(id)
            self.session.delete(zamestnanec)
            self.session.commit()
            return True
        except:
            return False