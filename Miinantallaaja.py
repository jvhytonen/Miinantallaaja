import haravasto
import random
import time
import pelitilastointi

"""
Lopullinen versio (versio 21) 
5.1.2021 klo 10.31:
Tässä pelissä on nyt kaikki tarvittavat osat.

Miinantallaaja.py: Ohjelma pyörii tämän tiedoston varassa. Jokaisen funktion alle on kuvattu, mitä se tekee.
Pelitilastointi.py: Tallentaa ja lataa pelihistorian (mikäli tietokanta siirretään pelin mukana sinne, missä sitä pelataan) 
viisi vaikeinta kenttää SQL-tietokantaan. Tässä tallennetaan tietoja sekä txt-, että db- tiedostoihin, koska tässä työssä opeteltiin
tiedostoon tallennusta.  
Haravasto: Oulun yliopiston luoma kirjasto graafisen käyttöliittymän helppoon toteutukseen.
Tuodut modulit: time, random, haravasto (Miinantallaaja.py) ja sqlite3 (pelitilastointi.py)

"""

tila = {
    """
    Tässä sanakirjassa miinakenttä on koneen tekemä kenttä, pelikenttä on se missä pelataan peliä. Miinattomat-listaan avulla pyöritetään peliä.
    Peli jatkuu niin kauan kunnes miinattomat-lista on tyhjä tai kun on astuttu miinaan.
    Alla lyhyesti sanakirjan eri muuttujien tarkoitukset
    Miinakentta: Käyttäjän antamien syötteiden perusteella luotu miinakenttä, joka on pelin perusta.
    Pelikentta: Käyttäjä pelaa tämän kentän perusteella graafisessa käyttöliittymässä. 
    Vuorot: Tallentaa tilastoihin, montako klikkausta pelaaja teki pelikierroksen aikana. 
    Tulos: Apu tilastoinnissa, näyttää tilastoissa voittiko pelin vai ei. Ohjaa myös paivitys_kasittelijan ja muutaman muun funktion toimintaa
    sen mukaan onko peli kesken vai päättynyt.
    Miinat, leveys, pituus: Käyttäjän antamat tiedot, millaisella kentällä hän haluaa pelata. 
    Pelaaja: Pelaajan antama nimi. Annetaan oletusnimi, mikäli käyttäjä ei anna nimeään. 
    Aloistusaika, lopetusaika: Peliajankohdan ja keston tilastointiin. Juokseva sekuntikello on näkyvillä myös peli-ikkunassa. 
    Jaljella: Pelaajalle näytetään peli-ikkunan yläruudussa, montako avaamatonta "turvallista" ruutua on vielä jäljellä.



    """
    "miinakentta": [],
    "pelikentta": [],
    "miinattomat": [],
    "vuorot": 0,
    "tulos": 'keskeytys',
    "miinat": 0,
    "leveys": 0,
    "pituus": 0,
    "pelaaja": "Tuntematon pelaaja",
    "jaljella": 0,
    "aloitusaika": 0,
    "lopetus": 0
    
}

def pelin_tiedot():
   
    """ 
    Tämä funktio kerää tilastotietoja pelattavasta pelistä.
    """ 
    
    #Tarkoitus on tallentaa tilastoihin vain sellaisia peljä, jotka päättyvät (ei sellaisia, josssa ohjelma kaatuu kesken kaiken). Lopetusaika-leima tulee vasta, 
    # kun peli loppuu joko miinaan tai kaikkien vapaiden ruutujen klikkaamiseen, jolloin peli on päättynyt. 
    
    if tila["aloitusaika"] and tila["lopetus"]:
        pelin_kesto = round(tila["lopetus"] - tila["aloitusaika"])
                    
        minuutit = round(pelin_kesto/60)
        sekunnit = round(pelin_kesto%60)
        if minuutit >= 1:
            #rint("Pelin kesto: {min} min ja {sek} sek".format(min=minuutit, sek= sekunnit))
            pelin_kesto = str(minuutit) + " min " + str(sekunnit) + " sek"
        else:
            #print("Pelin kesto: {} sek".format(sekunnit))
            pelin_kesto = str(sekunnit) + " sek"
    pelin_kesto = (pelin_kesto + "               "*13)[:13]
     
    
    tiedot = []
    tiedot = lataa_tilastot('tilastot.txt')
    
    #Jos tiedostossa on enemmän tietoja kuin 20 kpl niin ne poistetaan. Käytännössä siis poistetaan aina vanhin, mikäli pelattuja pelejä
    # on tiedostossa 20 kpl. 
    
    while len(tiedot) > 19:
            tiedot.pop(0)
    tiedot.extend((tila["aloitushetki"], ',', tila["pelaaja"], ',', tila["leveys"], ',', tila["pituus"], ',' ,tila["miinat"], ',', tila["tulos"], ',', tila["vuorot"], ',', pelin_kesto))
    tallenna_tiedot('tilastot.txt', tiedot)

    if tila["tulos"] == 'Voitto':
        vaikeat_kentat()
        
        
def vaikeat_kentat():

    """ 
    Tämä funktio kerää ja käsittelee tietoa pelihistorian vaikeimmista läpäistyistä kentistä. 
    Funktio yhdessä pelitilastointi-moduulin kanssa tallentaa voitetun pelin SQL-tietokantaan, jossa on tallennettuna max. 5 vaikeinta läpäistyä kenttää.
    Yksinkertaisesti: Läpäisty kenttä tallennetaan aina tauluun. Mikäli taulussa on 6 kenttää, poistetaan tietokannasta se kenttä, joka on vaikeusasteeltaan 
    helpoin. Mitä suurempi on lukema ((leveys x pituus) / miinojen määrä), sitä helpompi kenttä on. 
    """ 

    pelitilastointi.create_tables(pelitilastointi.connect())
    vaikeusaste = (tila["leveys"] * tila["pituus"]) / tila["miinat"]
    pelitilastointi.lisaa_tietoa(pelitilastointi.connect(), tila["pelaaja"], tila["aloitushetki"], tila["leveys"], tila["pituus"], tila["miinat"], vaikeusaste)
    vanhat_vaikeat = pelitilastointi.vastaanota(pelitilastointi.connect())
    
    while len(vanhat_vaikeat) > 5:
        pelitilastointi.poista_tietoa(pelitilastointi.connect())
        vanhat_vaikeat = pelitilastointi.vastaanota(pelitilastointi.connect())



           
def tallenna_tiedot(tiedosto, tallennettava):
    """
    Tallentaa tietoja tiedostoon.
    """
    with open(tiedosto, "w") as kohde:
           
        for i in range(0,len(tallennettava)):
            kohde.write(str(tallennettava[i]))
        kohde.write('\n')
    

def lataa_tilastot(tiedosto):
    """
    Lataa tilastoja tiedostosta.
    """
    sisalto = []  
    
    try:
        with open(tiedosto) as kohde:
        
            for rivi in kohde.readlines():
                sisalto.append(rivi)
           
            return sisalto
    #Vaikka tiedostoa ei olisi, palautetaan silti tyhjä lista. 
    except FileNotFoundError:
        return sisalto

def nayta_tilastot():
    """
    Tänne tullaan päävalikosta painamalla t-kirjainta. Printtaa nätisti tilastot. 
    """
    print()
    print("Kaksikymmentä viimeisintä peliä:")
    print()
    
    tilastot = []
    with open("tilastot.txt") as kohde:
        print("|Päivä ja kellonaika | Pelaaja                   | Kentän koko    | Miinat    | Tulos  | Vuorot | Pelin kesto  | ")
        print("|--------------------|---------------------------|----------------|-----------|--------|--------|--------------| ")
        for rivi in kohde.readlines():
           osat = rivi.split(',')
           tilastot.append(osat)
        
        for rivit in reversed(tilastot):
            print("|{aika} | {pelaaja} | {leveys} x {pituus} ruutua | {miinat} miinaa | {tulos} | {vuorot} kpl | {kesto}|".format(aika = rivit[0], pelaaja = rivit[1], leveys = str(rivit[2]) if len(str(rivit[2]))==2 else str(rivit[2])+" ", 
            pituus = str(rivit[3]) if len(str(rivit[3])) == 2 else str(rivit[3]) + " ", miinat = str(rivit[4]) if len(str(rivit[4])) == 2 else str(rivit[4]) + " ", tulos = rivit[5], vuorot = str(rivit[6]) if len(str(rivit[6])) == 2 else str(rivit[6]) + " ", kesto = rivit[7].strip('\n')))  
     
    print('\n' * 4)

    vaikeat_kentat = pelitilastointi.vastaanota(pelitilastointi.connect())

    print("Top 5 vaikeimmat läpäistyt kentät: ")
    print()
    print("|Päivä ja kellonaika | Pelaaja                   | Kentän koko    | Miinat    |")
    print("|--------------------|---------------------------|----------------|-----------|")
    x = 0
    for x in range(0, len(vaikeat_kentat)):
        print("|{aika} | {pelaaja} | {leveys} x {pituus} ruutua | {miinat} miinaa |"
        .format(aika = vaikeat_kentat[x][2], pelaaja = vaikeat_kentat[x][1], leveys = str(vaikeat_kentat[x][3]) if len(str(vaikeat_kentat[x][3])) == 
        2 else str(vaikeat_kentat[x][3]) + " " , pituus = str(vaikeat_kentat[x][4]) if len(str(vaikeat_kentat[x][4])) == 2 else str(vaikeat_kentat[x][4]) + " " , 
        miinat = str(vaikeat_kentat[x][5]) if len(str(vaikeat_kentat[x][5])) == 2 else str(vaikeat_kentat[x][5]) + " " ))
        x = x +1
    print('\n' * 4)


def maarittele_miinakentta():
    kentta = 'kesken'
    while kentta == 'kesken':
        while True:
            #Nimen pitää olla riittävän lyhyt, jotta tilastot näyttävät tulostuessaan kauniilta.
            #Lisäksi pilkun syöttäneen käyttäjän nimi korvataan pisteellä (pilkku hajottaa tilastoinnin).
            #Piste saa luvan kelvata.
            nimi = input("Anna nimesi? " )
            if ',' in nimi:
               nimi = nimi.replace(",",".")
            if len(nimi) < 1:
                nimi = "Tuntematon pelaaja"
                nimi = (nimi +"               "*25)[:25]
                tila["pelaaja"] = nimi
                break
            elif len(nimi) < 25:
                nimi = (nimi + "              "*25)[:25]
                tila["pelaaja"] = nimi
                break
            else:
                print("Anna sopivan lyhyt nimi (alle 25 merkkiä)")
            
        while True:    
            try:
                leveys = int(input("Anna kentän leveys ruutuina: "))
            except ValueError:
                print("Leveys on annettava kokonaislukuna!")
            else:    
                break
        
        while True:
            try:
                pituus = int(input("Anna kentän pituus ruutuina: "))
            except ValueError:
                print("Pituus on annettava kokonaislukuna!")
            else:
                break
        while True:   
            try:  
                lukumaara = int(input("Anna miinojen lukumäärä: "))
                tila["jaljella"] = lukumaara
            except ValueError:
                print("Miinojen määrä on annettava kokonaislukuna!")
            else:
                break
       
        #Tarkistetaan, onko kentässä vähemmän miinoja kuin ruutuja. Jos on, muodostetaan se, merkataan ruudut joko tyhjiksi, numeroiksi, tai miinoiksi. 
        if lukumaara < leveys * pituus and leveys > 0 and pituus > 0 and lukumaara > 0:
            print("Olet määrittänyt miinakentän, jonka leveys on {}, pituus {}, ja jossa on {} miinaa. ".format(leveys, pituus, lukumaara))
            print()
            kentta = 'ok'
            #Tallennetaan kentän tiedot sanakirjaan tilastoja varten.
            tila["leveys"] = leveys
            tila["pituus"] = pituus
            tila["miinat"] = lukumaara
            tila["tulos"] = 'keskeytys'
            #Ensin mennään muodostamaan kenttä, ja miinoittamaan se
            muodosta_kentta(leveys, pituus, lukumaara)
            #Tämän jälkeen luodaan numeroruudut miinojen viereisiin ruutuihin.
            laske_viereiset_miinat()
            #Tehdään kopio miinakentästä. Kopio on käyttäjälle näkyvä pelikenttä, jota piirretään pelin aikana grafiikkaan.
            tee_pelikentta(leveys, pituus)
            #Tallennetaan alkuhetki
            tila["aloitusaika"] = time.time()
            tila["aloitushetki"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            #Poistutaan tästä funktiosta rakentamaan grafiikkaa ja pelaamaan.
            peli()
            
        else:
            print("Tehdään kunnon kenttä! Annetut luvut on oltava suurempia kuin 0, eikä miinakentässä saa olla enempää miinoja kuin ruutuja!")
  
    
def laske_viereiset_miinat():
    """
    Tässä funktiossa käydään läpi kentän jokainen ruutu, lasketaan sen ympärillä olevat miinat, ja merkitään numero.
    """
    kentta = tila["miinakentta"]
    for i in range(len(kentta)):
        for y in range(len(kentta[0])):
            if kentta[i][y] == ' ':
                #Lähetetään muuttuja viereiset ruudut tarkistavaan funktioon, joka palauttaa arvon, joka ruudulle kuuluu antaa.
                viereiset_miinat = laske_viereiset_ruudut(y, i, kentta)
                #Merkitään palautettu numero ruutuun. Jos ympärillä on 0 miinaa, jätetään se rauhaan.
                if viereiset_miinat > 0:
                    kentta[i][y] = viereiset_miinat
    
def jatkuuko_peli():
    """
    Tässä funktiossa tutkitaan jatkuuko peli vielä. Mikäli miinattomia ruutuja on jäljellä, peli jatkuu. Mikäli ei ole. Peli päättyy.
    """
    if len(tila["miinattomat"]) == 0:
                print("Selvitit kentän! Onnea")
                print()
                print("Ikkuna sulkeutuu klikkaamalla hiiren painiketta ikkunassa")
                print()
                tila["lopetus"] = time.time()
                tila["tulos"] = 'Voitto'
                pelin_tiedot()
                
                
    else:
        pass

def laske_viereiset_ruudut (x, y, lista):
   """
   Funktio laskee, montako miinaa turvallisen ruudun ympärillä on.
   Käytännössä sama funktio, kuin harjoitustehtävien laske_ninjat.
   """
   
   naapurit = 0 
   
   #Ensimmäinen silmukka laskee saman rivin naapurit. Samalla varmistetaan, ettei mennä huoneen ulkopuolelle. 
   for rivi in range(x-1, x+2):
        if rivi > -1 and rivi < len(lista[y]):
            if lista[y][rivi] == 'x':
                naapurit = naapurit + 1
        

   #Toinen silmukka laskee ylemmän rivin naapurit. Samalla varmistetaan, ettei mennä tutkimaan huoneen ulkopuolelle x- eikä y-akselilla.         
   for rivi in range(x-1, x+2):
        if rivi > -1 and rivi < len(lista[y]) and y+1 < len(lista):
            if lista[y+1][rivi] == 'x':
                naapurit = naapurit + 1
            
   #Kolmas silmukka laskee alemman rivin naapurit. Samalla varmistetaan, ettei mennä tutkimaan huoneen ulkopuolelle x- eikä y-akselilla. 
   for rivi in range(x-1, x+2):
        if rivi > -1 and rivi < len(lista[y]) and y-1 >= 0:
            if lista[y-1][rivi] == 'x':
                naapurit = naapurit + 1
         
    
    
   return naapurit


def miinoita(miinakentta, vapaat_ruudut, miina_lukumaara):
    """
    Funktio, joka miinoittaa ruudut satunnaisesti.
    """
    for i in range(miina_lukumaara):
        paikka = random.choice(vapaat_ruudut)
        rivi = paikka[1]
        sarake = paikka[0]
        miinakentta[sarake][rivi] = 'x'
        vapaat_ruudut.remove(paikka)
        tila["miinattomat"] = vapaat_ruudut
        
        
def muodosta_kentta(leveys, pituus, miinojen_maara):
    """
    Muodostetaan miinakenttä, käyttäjän antamien tietojen (leveys, pituus, miinojen määrä) mukaisesti.
    Muodostetaan myös lista "jäljellä" koordinaateista, jotka ovat vielä käyttämättä. Tämä helpottaa, ettei miinoja laiteta useampaa samaan ruutuun.
    Lopuksi asetetaan miinat omassa funktiossa.
    """
    kentta = []
    for rivi in range(pituus):
        kentta.append([])
        for sarake in range(leveys):
            kentta[-1].append(" ")

    tila["miinakentta"] = kentta  
    

    jaljella = []
    for x in range(pituus):
        for y in range(leveys):
            jaljella.append((x, y))

    miinoita(kentta, jaljella, miinojen_maara)
  
def tee_pelikentta(leveys, pituus):
    """
    Tässä funktiossa muodostetaan graafisen pelikentän pohja, millä itse peliä pelataan. Miinakenttä jää konepellin alle ja siitä tarkistetaan, mitä grafiikassa pitää tehdä.
    """
    kentta = []
    for rivi in range(pituus):
        kentta.append([])
        for sarake in range(leveys):
            kentta[-1].append(" ")
    tila["pelikentta"] = kentta
    

  
def tutki_ruutu (hiiren_nappi, x, y):
        
        kentta = tila["miinakentta"]
        pelikentta = tila["pelikentta"]
        merkki = kentta[y][x]
        lista = tila["miinattomat"]
        #Jos pelaaja avaa tyhjän ruudun, mennään tulvatutkimukseen.
        if hiiren_nappi == 1 and merkki == ' ':
            if (y,x) in lista:
                tila["vuorot"] += 1
                tulvataytto(tila["miinakentta"], tila["pelikentta"],x,y)
                         
        #Jos pelaaja avaa miinan, tehdään tämä.            
        elif hiiren_nappi == 1 and merkki == 'x':
            pelikentta[y][x] = merkki
            print("Astuit miinaan. Peli päättyi.")
            print()
            tila["vuorot"] += 1
            tila["lopetus"] = time.time()
            tila["tulos"] = 'Tappio'
            pelin_tiedot()
            #haravasto.lopeta()
                   
        #Jos ruutu on numeroruutu, tehdään tämä.    
        elif hiiren_nappi == 1:
            pelikentta[y][x] = merkki
            if (y,x) in lista:
                tila["miinattomat"].remove((y,x))
                tila["vuorot"] += 1
                jatkuuko_peli()
            
        #Jos pelaaja painaa hiiren oikeaa nappia, ja ruutua ei ole vielä avattu, se merkitään lipulla.
        elif hiiren_nappi == 4 and pelikentta[y][x] == ' ':
            pelikentta[y][x] = 'f'
            if tila["jaljella"] >= 1:
                tila["jaljella"] -= 1
        
        elif hiiren_nappi == 4 and pelikentta[y][x] == 'f':
            pelikentta[y][x] = ' '
            tila["jaljella"] += 1


def tulvataytto (lista, toinen, a, b):
    """
    Tähän funktioon saavutaan, mikäli pelaaja osuu ruutuun, jossa ei ole miinaa eikä numeroa. Miinattoman ja numerottoman ruudun viereistä avataan
    kaikki niin ikään miinattomat ja numerottomat ruudut. 

    Funktiossa selvitetään tyhjän ruudun ympärillä olevat muut tyhjät ruudut sekä niiden ympärillä olevat tyhjät ruudut
    Tyhjää ruutua avattaessa se on poistettava myös tila["miinattomat"] -sanakirjasta, sillä sen avulla pyöritetään itse peliä.
    """
    planeetan_pituus = len(lista)
    planeetan_leveys = len(lista[0])
    tutkittavat = [[b,a]]
    
    
    while len(tutkittavat) > 0:
        tutkittava_ruutu = tutkittavat.pop()
        x = tutkittava_ruutu[0]
        y = tutkittava_ruutu[1]
        planeetan_ruutu = lista[x][y]
    
        if planeetan_ruutu == ' ':
            lista[x][y] = '0'
            toinen[x][y] = '0'
            tila["miinattomat"].remove((x,y))
            jatkuuko_peli()
        #Planeetan ruudun sama rivi
            for rivi in range(y-1, y+2):
                if rivi > -1 and rivi < planeetan_leveys and lista[x][rivi] == ' ':
                    tutkittavat.append([x,rivi])
                elif rivi > -1 and rivi < planeetan_leveys and lista[x][rivi] != ' ' and lista[x][rivi] != 'x':
                    toinen[x][rivi] = lista[x][rivi]
                    if (x,rivi) in tila["miinattomat"]:
                        tila["miinattomat"].remove((x,rivi))
                        jatkuuko_peli()
        #Planeetan ruudun ylempi rivi        
            for rivi in range(y-1, y+2):
                if rivi > -1 and rivi < planeetan_leveys and x-1 >= 0 and lista[x-1][rivi] == ' ':
                    tutkittavat.append([x-1, rivi])
                elif rivi > -1 and rivi < planeetan_leveys and x-1 >= 0 and lista[x-1][rivi] != ' ' and lista[x-1][rivi] != 'x':
                    toinen[x-1][rivi] = lista[x-1][rivi]
                    if (x-1,rivi) in tila["miinattomat"]:
                        tila["miinattomat"].remove((x-1,rivi))
                        jatkuuko_peli()
        #Planeetan ruudun alempi rivi
            for rivi in range(y-1, y+2):
                if rivi > -1 and rivi < planeetan_leveys and x < planeetan_pituus-1 and lista[x+1][rivi] == ' ':
                    tutkittavat.append([x+1, rivi])
                elif rivi > -1 and rivi < planeetan_leveys and x < planeetan_pituus-1 and lista[x+1][rivi] != ' ' and lista[x+1][rivi] != 'x':
                    toinen[x+1][rivi] = lista [x+1][rivi]
                    if (x+1,rivi) in tila["miinattomat"]:
                        tila["miinattomat"].remove((x+1,rivi))
                        jatkuuko_peli()
      
     
def tutki_kentta (kentta):
    
        for rivi in range(0, len(kentta)):
          sarake = 0
          for i in kentta[rivi]:
             haravasto.lisaa_piirrettava_ruutu(i, rivi * 40, sarake * 40)
             sarake = sarake + 1
  
def piirra_kentta():
    """
    Luodaan pelin aluksi grafiikat. Funktion loppupuolella koordinoidaan peli-ikkunan yläosaa, jossa pelaajalle
    näytetään jäljellä olevien vapaiden ruutujen määrä, aika, sekä pelin päätyttyä se, voittiko vai hävisikö hän pelin.
    Jos pelaaja pelaa vain kapealla ruudukolla, eikä sinne mahdu tekstiä, tekstiä ei tule.
    """
    #Alustetaan graafinen puoli
    kentta = tila["pelikentta"] 
    haravasto.tyhjaa_ikkuna()
    haravasto.piirra_tausta()
    haravasto.aloita_ruutujen_piirto()    
    #Tässä luodaan ruudukkoa pelin alussa ja sen aikana.
    for rivi in range(0, len(kentta[0])):
          sarake = 0
          for i in range(0, len(kentta)):
             haravasto.lisaa_piirrettava_ruutu(str(kentta[i][rivi]), rivi * 40, sarake * 40)
             sarake = sarake + 1
      
    haravasto.piirra_ruudut()
    if tila["leveys"] > 4 and len(tila["miinattomat"]) != 0 and tila["tulos"] != 'Tappio':
        #Kirjoittaa ruudukon yläpuolelle, montako turvallista ruutua on vielä avaamatta, mutta vain jos tila riittää eli leveys on yli 4.
        haravasto.piirra_tekstia("Jäljellä: " + str(len(tila["miinattomat"])), 0, len(tila["miinakentta"]) * 40, koko=20)
    haravasto.piirra_tekstia(str(round(tila["lopetus"]-tila["aloitusaika"])), ((tila["leveys"] * 40) - 60), len(tila["miinakentta"]) * 40, vari=(255, 0, 0, 255), koko=20)
    
    if len(tila["miinattomat"]) == 0:
        haravasto.piirra_tekstia("Voitit!", 0, len(tila["miinakentta"]) * 40, koko=20)
        
    if tila["tulos"] == 'Tappio':
        haravasto.piirra_tekstia("Hävisit!", 0, len(tila["miinakentta"]) * 40, koko = 20)

def paivitys_kasittelija(kulunut_aika):
    """
    tila-lopetus-sanakirjalla on lopetusajankohdan merkkaamisen ohella toinenkin merkitys. Tässä funktiossa päivitetään jatkuvasti 
    lopetus-arvoa, sillä vähentämällä aloitushetki aina kulloisestakin hetkestä, päivitetään peli-ikkunan oikeassa reunassa olevaa 
    sekuntikelloa. Kts. tarkemmin piirra_kentta -funktion alaosa. 
    """
    if tila["tulos"] == 'keskeytys':
        tila["lopetus"] = time.time()



def kasittele_hiiri(hiiri_x, hiiri_y, painike, nappaimet):
    """
    Tässä funktiossa selvitetään, mitä ruutua painettiin hiirellä ja mitä klikkauksella tehdään.
    """
    # Spritet-ikkunan leveys ja korkeus on 40. Sen vuoksi klikatun ruudun saa selville jakamalla 
    # koordinaatit floor-division ('//')-operaattorilla.
    klikattu_ruutu_x = hiiri_x // 40
    klikattu_ruutu_y = hiiri_y // 40
    
    #Alla oleva if-else -lauseke jättää peli-ikkunan auki sen jälkeen kun peli päättyy. tila["tulos"] -sanakirja on päivittynyt
    # pelin päättymisen jälkeen joko "voittoon" tai "tappioon", joten ei mennä enää if-puolelle vaan else-puolelle, joka seuraavalla 
    # klikkauksella sulkee ikkunan, ja palataan päävalikkon.    
    if tila["tulos"] == 'keskeytys':
        if klikattu_ruutu_y < tila["pituus"]:
            tutki_ruutu(painike, klikattu_ruutu_x, klikattu_ruutu_y)
    else:
        haravasto.lopeta()
        
def peli():
    """    
    Lataa pelin grafiikat, luo peli-ikkunan ja asettaa siihen piirtokäsittelijän.
    """
    #Määritellään ikkunalle pituus ja leveys.
    kentta = tila["miinakentta"]
    leveys = len(kentta[0]) * 40
    korkeus = (len(kentta) * 40) + 40
    
    haravasto.lataa_kuvat('spritet.zip\spritet')
    haravasto.luo_ikkuna(leveys, korkeus)
    haravasto.aseta_piirto_kasittelija(piirra_kentta)
    haravasto.aseta_hiiri_kasittelija(kasittele_hiiri)
    haravasto.aseta_toistuva_kasittelija(paivitys_kasittelija, 1/60)
    haravasto.aloita()
    

def main():
    """
    Päävalikko. Käyttäjä voi valita kolmen eri toiminnon väliltä.
    """
    while True:
        print("Mitä haluat tehdä?")
        print("(P)elaa uusi peli")
        print("(T)ilasto pelatuista peleistä")
        print("(L)opeta")
        valinta = input("Anna valintasi: ").strip().lower()
        if valinta == "p":
            maarittele_miinakentta()
        elif valinta == "t":
            nayta_tilastot()
        elif valinta == "l":
            break    
        else:
            print("Valitsemaasi toimintoa ei ole olemassa")

if __name__ == "__main__":
    print("Tervetuloa pelaamaan Miinantallaajaa")
    main()            