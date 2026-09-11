# Meteo.lt Weather Analysis

Python programa, naudojanti [Meteo.lt REST API](https://api.meteo.lt/) meteorologiniams duomenims nuskaityti, analizuoti ir vizualizuoti.

## Funkcionalumas

Programa:

* Nuskaito istorinius Vilniaus meteorologinius duomenis iš Meteo.lt API.
* Nuskaito orų prognozės duomenis.
* Apskaičiuoja:

  * vidutinę metų temperatūrą;
  * vidutinę metų oro drėgmę;
  * vidutinę dienos temperatūrą (08:00–20:00);
  * vidutinę nakties temperatūrą;
  * lietingų savaitgalių skaičių.
* Apjungia paskutinės savaitės istorinius temperatūros duomenis su prognoze.
* Atvaizduoja išmatuotos ir prognozuojamos temperatūros grafiką.
* Valandinius temperatūros duomenis interpoliuoja iki 5 minučių dažnio.
* Išsaugo istorinius duomenis CSV faile, kad jų nereikėtų kiekvieną kartą iš naujo atsisiųsti.

## Projekto struktūra

```text
METEO_API_PROJECT/
│
├── main.py
├── historical_weather.csv
├── requirements.txt
│
└── src/
    ├── meteo_api.py
    ├── weather_analysis.py
    ├── data_manager.py
    ├── interpolation.py
    └── plotting.py
```

### Pagrindiniai failai

**`main.py`**
Pagrindinis programos paleidimo failas. Jis sujungia duomenų nuskaitymą, analizę, prognozę, grafiką ir interpoliaciją.

**`src/meteo_api.py`**
`MeteoCLient` klasė, atsakinga už komunikaciją su Meteo.lt API.

Joje realizuoti:

* `get_historical()` – istorinių duomenų nuskaitymas;
* `get_forecast()` – prognozės duomenų nuskaitymas.

**`src/weather_analysis.py`**
`WeatherAnalysis` klasė, atsakinga už meteorologinių duomenų analizę.

**`src/data_manager.py`**
Istorinių duomenų išsaugojimas ir įkėlimas iš CSV failo.

**`src/interpolation.py`**
Temperatūros duomenų interpoliavimas iš valandinio į 5 minučių dažnį.

**`src/plotting.py`**
Temperatūros grafiko sudarymas naudojant Matplotlib.

## Reikalavimai

Reikalingas:

* Python 3.10 arba naujesnis
* Interneto prieiga Meteo.lt API pasiekimui

Naudojamos pagrindinės bibliotekos:

* pandas
* requests
* matplotlib

## Įdiegimas

Rekomenduojama naudoti virtualią aplinką.

### 1. Nuklonuokite projektą

```bash
git clone https://github.com/Deivydukas/METEO_API_PROJECT.git
cd METEO_API_PROJECT
```

### 2. Sukurkite virtualią aplinką

Windows:

```bash
python -m venv .venv
```

Aktyvuokite ją:

```bash
.venv\Scripts\activate
```

### 3. Įdiekite bibliotekas

```bash
pip install -r requirements.txt
```

Jeigu `requirements.txt` dar nėra:

```bash
pip install pandas requests matplotlib
```

## Programos paleidimas

Aktyvavus virtualią aplinką paleiskite:

```bash
python main.py
```

Pirmo paleidimo metu programa atsisiųs istorinius duomenis už paskutinius metus ir išsaugos juos:

```text
historical_weather.csv
```

Kituose paleidimuose programa patikrins, ar išsaugoti duomenys yra aktualūs. Jei duomenys neapima šiandienos datos, jie bus atsisiųsti iš naujo.

## API naudojimas

Programa naudoja Vilniaus meteorologijos stotį:

```text
Station: vilniaus-ams
Place: vilnius
API: https://api.meteo.lt/v1
```

Istoriniai duomenys Meteo.lt API yra pateikiami atskirų dienų pagrindu. API neturi galimybės vienu užklausimu grąžinti viso pasirinkto metų intervalo, todėl vienerių metų duomenims gauti atliekamos atskiros užklausos kiekvienai dienai.

Siekiant sumažinti vykdymo laiką, dienų užklausos atliekamos lygiagrečiai naudojant `ThreadPoolExecutor`.

Programa taip pat apdoroja `429 Too Many Requests` atsakymus ir pakartotinai bando atlikti užklausą.

## Laiko zona

Meteo.lt pateikiami laiko duomenys konvertuojami į:

```text
Europe/Vilnius
```

Todėl analizėje naudojamas Lietuvos vietinis laikas.

## Lietingi savaitgaliai

Lietingas savaitgalis nustatomas pagal istorinių duomenų `conditionCode` reikšmes.

Jeigu šeštadienį arba sekmadienį nustatoma lietaus sąlyga, visas savaitgalis skaičiuojamas kaip vienas lietingas savaitgalis.

Prognozuojamų lietingų savaitgalių skaičiavimas nebuvo atliktas, nes Meteo.lt pateikiami prognozės duomenys neapėmė pakankamai tolimo laikotarpio.

## Temperatūros interpoliacija

Istoriniai duomenys yra valandiniai. Funkcija `interpolate_temperature()`:

1. priima `pandas.Series`;
2. patikrina, ar indeksas yra `DatetimeIndex`;
3. surikiuoja duomenis pagal laiką;
4. perskaičiuoja dažnį į 5 minutes;
5. tarpines temperatūros reikšmes apskaičiuoja naudojant laiko interpoliaciją.

## API klaidų apdorojimas

Programa tikrina pagrindines API būsenas ir turi pakartotinių užklausų mechanizmą.

Apdorojamas:

* `404` – duomenų konkrečiai dienai nėra;
* `429` – per daug užklausų, todėl programa palaukia ir bando dar kartą;
* tinklo ir HTTP užklausų klaidos.

API komunikaciją būtų galima dar labiau išplėsti papildomai apdorojant kitas būsenas, pavyzdžiui, `403 Forbidden`, bei įdiegiant išsamesnį klaidų registravimą.

## Rezultatas

Paleidus programą konsolėje pateikiami apskaičiuoti meteorologiniai rodikliai, o naudojant Matplotlib parodomas grafikas su:

* paskutinės savaitės išmatuota temperatūra;
* ateinančio laikotarpio prognozuojama temperatūra.

## Duomenų šaltinis

Meteo.lt API:

https://api.meteo.lt/
