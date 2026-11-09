# Instalare prin MGU Store

1. Deschide MGU Store pe unitatea BMW.
2. Intră la Sources / Add source.
3. Adaugă repository-ul GitHub:
   `flash8523/bmw-weather-mgu`
4. Selectează ramura `main`.
5. Alege BMW Weather și pornește instalarea.

MGU Store va descărca sursa și va rula build-ul pe unitate. Build-ul folosește SDK-ul donor disponibil pe MGU și kitul public iDrive 7 fixat la un commit. Nu încărca SDK-ul BMW în GitHub.

## Înainte de instalare

- MGU Store / mgu-deploy trebuie să suporte repo-tree builds.
- Internet Uplink trebuie să fie instalat și conectat pentru descărcarea sursei și pentru API-ul meteo.
- La prima pornire, deschide Setări și introdu coordonatele locației.
- GPS nu este activat încă: interfața MGU de localizare nu a fost verificată pe firmware-ul acestei mașini.

## Stadiu

Aceasta este o versiune de dezvoltare. Manifestul repo-tree și codul de bază sunt publicate, dar build-ul pe unitate și afișarea widgetului trebuie validate pe MGU-ul real înainte de a considera aplicația gata de utilizare.
