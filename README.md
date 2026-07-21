# Retkireitit

## Sovelluksen toiminnot

- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään reittejä sekä muokkaamaan ja poistamaan lisäämiään reittejä.
- Käyttäjä näkee sekä itse lisäämänsä että muiden käyttäjien lisäämät reitit.
- Käyttäjä pystyy etsimään reittejä reitin nimen tai alueen perusteella.
- Käyttäjäsivu näyttää tilastoja sekä käyttäjän lisäämät reitit ja retkiraportit.
- Käyttäjä pystyy valitsemaan reitille luokitteluja, kuten vaikeustason, maastotyypin ja saavutettavuuden.
- Käyttäjä pystyy lisäämään omiin ja muiden käyttäjien reitteihin retkiraportin, jossa hän voi arvioida reitin ja kertoa reitin kunnosta.
- Reitin sivulla näytetään reittiin lisätyt retkiraportit ja arvioiden keskiarvo.

## Sovelluksen nykytila

Sovelluksessa on toteutettu tunnuksen luominen ja kirjautuminen. Kirjautunut käyttäjä voi lisätä reittejä sekä muokata ja poistaa omia reittejään. Kaikki käyttäjät voivat selata reittejä ja etsiä niitä nimen tai alueen perusteella.

Käyttäjäsivut, reittien luokittelut ja retkiraportit toteutetaan myöhemmin.

## Sovelluksen asennus

Ohjeet on kirjoitettu Linux-ympäristölle. Tarkista ensin, että Python ja SQLite ovat käytettävissä:

```bash
python3 --version
sqlite3 --version
```

Esimerkiksi Ubuntussa tai WSL:ssä puuttuvat työkalut voi asentaa näin:

```bash
sudo apt update
sudo apt install python3 python3-venv sqlite3
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
pip install flask
```

Luo tietokanta:

```bash
sqlite3 database.db < schema.sql
```

Käynnistä sovellus:

```bash
flask run
```

Sovellusta voi käyttää osoitteessa <http://127.0.0.1:5000>.

## Sovelluksen testaaminen

1. Luo kaksi eri käyttäjätunnusta.
2. Lisää kummallakin tunnuksella vähintään yksi reitti.
3. Tarkista, että kaikki reitit näkyvät etusivulla ja että reitin tiedot saa avattua.
4. Kokeile reittien hakemista reitin nimellä ja alueella.
5. Muokkaa ja poista omia reittejä.
6. Tarkista, ettei toisen käyttäjän reitillä näy muokkaus- tai poistamislinkkejä.
