# CityBeach Frankfurt App

A premium, native-ready PWA for **CityBeach Frankfurt** and **CityAlm**, powered by A+.

## What is included

- Customer, staff and owner login
- Shared A+ Pay wallet for CityBeach and CityAlm
- QR member card and staff camera scanner
- Customer-confirmed payments with configurable tips
- Beach, Sunset and Skyline loyalty levels
- Digital receipts and transaction history
- Venue-specific offers, event cards and image uploads
- Owner payment notifications
- Social, website and reservation links
- REST API and push-device registration for future iOS/Android apps
- PWA manifest and mobile-first interface

## Brand foundation

The visual system follows CityBeach's dark Instagram presentation with the orange sun, turquoise water, magenta ring, skyline photography and a premium summer-rooftop feeling.

## Local development

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec web python manage.py seed_demo
```

Open `http://127.0.0.1:8022`.

## Production deployment

Pushes to `main` run tests and deploy to the Hetzner server using GitHub secrets:

- `HOST`
- `PASS`

The first deployment creates `/root/citybeach/.env` and stores demo credentials in:

```bash
cat /root/citybeach/.initial-credentials
```

Until a domain is connected, the app is served through the server IP on port 80.
