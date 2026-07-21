# CityBeach Frankfurt Anwendung

Eine hochwertige, für iOS und Android vorbereitete Web-Anwendung für **CityBeach Frankfurt** und **CityAlm** mit Technik von A+.

## Enthaltene Funktionen

- Anmeldung für Kunden, Mitarbeiter und Inhaber
- Kundenanmeldung mit „Mit Apple fortfahren“
- Gemeinsames A+ Pay Guthabenkonto für CityBeach und CityAlm
- Digitale Mitgliedskarte mit QR-Code und Kamerascanner für Mitarbeiter
- Vom Kunden bestätigte Zahlungen mit einstellbarem Trinkgeld
- Mitgliedsstufen Strand, Sonnenuntergang und Panorama
- Digitale Belege und Buchungsverlauf
- Bereichsspezifische Angebote, Veranstaltungskarten und Bildhochladen
- Sofortige Zahlungsmitteilungen für den Inhaber
- Verknüpfungen zu sozialen Netzwerken, Internetseiten und Reservierungen
- Programmierschnittstelle und Endgeräte-Registrierung für zukünftige iOS- und Android-Anwendungen
- Installierbare Web-Anwendung mit für Mobilgeräte optimierter Oberfläche

## Gestaltung

Die visuelle Gestaltung orientiert sich am dunklen Auftritt von CityBeach mit orangefarbener Sonne, türkisfarbenem Wasser, pinkfarbenem Ring, Frankfurter Hochhäusern und sommerlicher Dachterrassen-Atmosphäre.

## Lokale Entwicklung

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec web python manage.py seed_demo
```

Danach ist die Anwendung unter `http://127.0.0.1:8022` erreichbar.

## Bereitstellung

Änderungen auf `main` werden automatisch geprüft und auf dem Hetzner-Server bereitgestellt. Dafür werden folgende GitHub-Geheimnisse verwendet:

- `HOST`
- `PASS`

Die erste Bereitstellung erstellt `/root/citybeach/.env`. Die Demozugänge stehen anschließend in:

```bash
cat /root/citybeach/.initial-credentials
```

Die Hauptadresse lautet:

```text
https://citybeach.smarbiz.sbs
```

## Apple-Anmeldung

Für die echte Apple-Anmeldung müssen zusätzlich diese GitHub-Geheimnisse hinterlegt werden:

- `APPLE_SERVICE_ID`
- `APPLE_BUNDLE_ID` – optional für die spätere iOS-Anwendung
- `APPLE_KEY_ID`
- `APPLE_TEAM_ID` – bei abweichender Kennung den App-ID-Präfix verwenden
- `APPLE_PRIVATE_KEY_B64` – der Inhalt der von Apple geladenen `.p8`-Datei als einzeilige Base64-Zeichenfolge

Die bei Apple einzutragende Rücksprungadresse lautet:

```text
https://citybeach.smarbiz.sbs/accounts/apple/login/callback/
```
