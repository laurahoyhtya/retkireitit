# Retkireitit

## Sovelluksen toiminnot

- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään reittejä sekä muokkaamaan ja poistamaan
  lisäämiään reittejä.
- Käyttäjä näkee sekä itse lisäämänsä että muiden käyttäjien lisäämät reitit.
- Käyttäjä pystyy etsimään reittejä reitin nimen tai alueen perusteella.
- Käyttäjäsivu näyttää käyttäjän lisäämien reittien ja retkiraporttien määrät
  sekä listat käyttäjän lisäämistä reiteistä ja retkiraporteista.
- Käyttäjä valitsee reitille vaikeustason, maastotyypin ja saavutettavuuden.
  Luokittelujen vaihtoehdot on tallennettu tietokantaan.
- Käyttäjä pystyy lisäämään omiin ja muiden käyttäjien reitteihin
  retkiraportin, jossa hän arvioi reitin ja kertoo sen kunnosta.
- Reitin sivulla näytetään retkiraportit ja arvioiden keskiarvo.
- Käyttäjä pystyy poistamaan oman retkiraporttinsa.

## Projektin nykytila

Projekti on edistetty välipalautuksen 3 tasolle. Välipalautuksen 2 arvioija voi
hyvin keskittyä vain kyseiseen välipalautukseen vaadittuihin toimintoihin:
käyttäjätunnuksiin, reittien hallintaan, reittilistaan ja hakuun.

Välipalautuksen 3 toiminnot eli käyttäjäsivut, tietokantaan tallennetut
luokittelut ja retkiraportit on toteutettu. Lopulliseen palautukseen jäävät
vielä suuren tietomäärän testaus, sivutus ja sitä tukeva indeksi sekä
lopulliselle versiolle tehtävä Pylint-tarkastus ja sen raportti.

## Sovelluksen asennus

Ohjeet toimivat macOS- ja Linux-ympäristöissä. Tarkista ensin, että Python ja
SQLite ovat käytettävissä:

```bash
python3 --version
sqlite3 --version
```

Kloonaa repositorio ja siirry sen hakemistoon:

```bash
git clone https://github.com/laurahoyhtya/retkireitit.git
cd retkireitit
```

Luo virtuaaliympäristö ja asenna Flask:

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install flask
```

Luo tietokannan taulut ja lisää luokittelujen vaihtoehdot:

```bash
sqlite3 database.db < schema.sql
sqlite3 database.db < init.sql
```

Käynnistä sovellus:

```bash
flask run
```

Sovellusta voi käyttää osoitteessa <http://127.0.0.1:5000>.

## Sovelluksen testaaminen

1. Luo kaksi eri käyttäjätunnusta.
2. Lisää ensimmäisellä tunnuksella reitti. Valitse jokaisesta luokittelusta
   vaihtoehto ja kirjoita kuvaukseen tekstiä usealle riville.
3. Tarkista, että reitti ja sen luokittelut näkyvät reitin sivulla ja että
   kuvauksen rivinvaihdot säilyvät.
4. Kokeile reitin etsimistä reitin nimellä ja alueella.
5. Muokkaa reitin tietoja ja luokitteluja.
6. Lisää reitille retkiraportti, jossa on arvosana, reitin kunto ja havaintoja.
7. Kirjaudu toisella tunnuksella ja lisää retkiraportti ensimmäisen käyttäjän
   reitille.
8. Tarkista reitin sivulta raporttien määrä, arvioiden keskiarvo ja molemmat
   retkiraportit.
9. Avaa kummankin käyttäjän käyttäjäsivu käyttäjänimestä ja tarkista tilastot
   sekä käyttäjän lisäämät reitit ja retkiraportit.
10. Tarkista, ettei toisella käyttäjällä näy ensimmäisen käyttäjän reitin
    muokkaus- tai poistamislinkkejä.
11. Poista oma retkiraportti ja tarkista, että se poistuu reitin sivulta.
12. Kirjaudu takaisin ensimmäisellä tunnuksella ja poista reitti.
