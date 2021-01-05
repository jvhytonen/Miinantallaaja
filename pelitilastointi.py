import sqlite3

"""
Tämä osa tallentaa ja lukee tietoja SQL-tietokannasta, jonne tallennetaan viisi vaikeinta 
all time-läpäistyä pelikenttää (vaikeusaste lasketaan kaavalla: kaikkien ruutujen määrä/miinojen määärä).
Tänne olisi voinut tuoda vielä tuon normaalin tilastoinninkin, mutta aloitteleva koodari halusi kokeilla tiedostoon tallennusta kahdella eri tavalla.

"""

LUO_VAIKEA_TAULU = "CREATE TABLE IF NOT EXISTS vaikeat (id INTEGER PRIMARY KEY, pelaaja TEXT NOT NULL, pvm TEXT NOT NULL, leveys INTEGER NOT NULL, pituus INTEGER NOT NULL, miinat INTEGER NOT NULL, vaikeus REAL NOT NULL);"
LISAA_TIETO = "INSERT INTO vaikeat (pelaaja, pvm, leveys, pituus, miinat, vaikeus) VALUES (?,?,?,?,?,?);"
VASTAANOTA_TIETO = "SELECT * FROM vaikeat ORDER BY vaikeus;"
POISTA_TIETO = "DELETE FROM vaikeat WHERE vaikeus = (SELECT MAX(vaikeus) FROM vaikeat);"


def connect():
   return sqlite3.connect('testikanta.db')

def create_tables(conn): 
    with conn:
        conn.execute(LUO_VAIKEA_TAULU)

def lisaa_tietoa(conn, pelaaja, paiva, leveys, pituus, miinat, vaikeus): 
    with conn:
        conn.execute(LISAA_TIETO, (pelaaja, paiva, leveys, pituus, miinat, vaikeus))

def vastaanota(conn):
    with conn:
        return conn.execute(VASTAANOTA_TIETO).fetchall()

def poista_tietoa(conn): 
    with conn:
        conn.execute(POISTA_TIETO)
