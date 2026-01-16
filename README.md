# WordPress GitOps Sync Tool

🔄 Synkronoi WordPress-teemat ja pluginit Gitin kanssa helposti ja turvallisesti.

## 📋 Ominaisuudet

- ✅ **Kaksisuuntainen synkronointi** - WordPress ↔ Git
- 🔒 **Automaattiset varmuuskopiot** - Turvallisuus ensin
- 🧪 **Dry-run tila** - Testaa ennen muutoksia
- 📊 **Selkeät raportit** - Kompakti tuloste (verbose-tila saatavilla)
- ⚙️ **Konfiguroitavuus** - Valitse mitä synkronoidaan
- 🚀 **Kevyt ja nopea** - Ei raskaita riippuvuuksia

## 🔧 Asennus

### Vaatimukset

- Python 3.7+
- Git
- WordPress-asennus
- Linux/Unix-pohjainen järjestelmä

### 1. Lataa skripti

```bash
# Kloonaa repositorio
git clone https://github.com/herrakoo/wordpress-gitops-sync.git
cd wordpress-gitops-sync

# Tai lataa suoraan
wget https://raw.githubusercontent.com/herrakoo/wordpress-gitops-sync/main/wp_gitops.py
chmod +x wp_gitops.py
```

### 2. Luo Git-repositorio

```bash
# Luo hakemisto Git-repolle
mkdir -p ~/wp-gitops-repo
cd ~/wp-gitops-repo
git init
git config user.email "sinun@email.com"
git config user.name "Sinun Nimi"
```

### 3. Luo alias (valinnainen mutta suositeltava)

```bash
# Lisää .bashrc-tiedostoon
echo 'alias wpgit="python3 ~/wordpress-gitops-sync/wp_gitops.py --wp-path /var/www/html/wordpress --git-repo ~/wp-gitops-repo"' >> ~/.bashrc

# Lataa uudet asetukset
source ~/.bashrc
```

**Huom:** Muuta polut vastaamaan omaa asennustasi:
- `--wp-path`: WordPress-asennuksen polku
- `--git-repo`: Git-repositorion polku

## 🚀 Käyttö

### Peruskäyttö (ilman aliasta)

```bash
python3 wp_gitops.py \
  --wp-path /var/www/html/wordpress \
  --git-repo ~/wp-gitops-repo \
  [KOMENTO]
```

### Käyttö aliaksen kanssa

```bash
wpgit [KOMENTO]
```

## 📚 Komennot

### `status` - Näytä tilanne

Näyttää nykyisen konfiguraation ja Git-tilanteen.

```bash
wpgit status
```

**Tuloste:**
```
📊 WordPress GitOps - Tilanne

WordPress-polku: /var/www/html/wordpress
Git-repositorio: /root/wp-gitops-repo
Viimeisin synkronointi: 2026-01-16T22:32:10

Asetukset:
  - Synkronoi teemat: True
  - Synkronoi pluginit: True
  - Synkronoi uploads: False
  - Poissuljetut pluginit: akismet, hello

Git: Ei committoimattomia muutoksia
```

---

### `push` - Synkronoi WordPress → Git

Kopioi teemat ja pluginit WordPressistä Git-repositorioon ja tekee commitin.

```bash
# Peruskomento
wpgit push

# Omalla commit-viestillä
wpgit push -m "Päivitetty teema ja lisätty uusi plugin"

# Dry-run (testaa ilman muutoksia)
wpgit push --dry-run

# Verbose-tila (yksityiskohtaiset tiedot)
wpgit -v push -m "Testi"
```

**Parametrit:**
- `-m, --message` - Commit-viesti
- `--dry-run` - Simuloi synkronointi ilman muutoksia
- `-v, --verbose` - Näytä yksityiskohtaiset tiedot

**Esimerkki:**
```bash
$ wpgit push -m "Lisätty custom-teema"

🔄 Synkronoidaan WordPress → Git...
✅ Synkronoitu: 4 teemaa, 3 pluginia
```

---

### `pull` - Synkronoi Git → WordPress

Kopioi teemat ja pluginit Git-repositoriosta WordPressiin.

```bash
# Peruskomento
wpgit pull

# Dry-run
wpgit pull --dry-run

# Verbose-tila
wpgit -v pull
```

**Parametrit:**
- `--dry-run` - Simuloi synkronointi ilman muutoksia
- `-v, --verbose` - Näytä yksityiskohtaiset tiedot

**Esimerkki:**
```bash
$ wpgit pull

🔄 Synkronoidaan Git → WordPress...
✅ Synkronoitu WordPressiin: 3 teemaa, 2 pluginia
```

**Huom:** Pull-komento luo automaattisesti varmuuskopion ennen muutoksia!

---

### `diff` - Vertaa eroja

Näyttää erot WordPress-asennuksen ja Git-repon välillä.

```bash
wpgit diff
```

**Esimerkki:**
```bash
$ wpgit diff

🔍 Vertaillaan eroja...

Teemat:
  Vain WordPressissä: custom-theme-2024
  Vain Gitissä: old-theme
  Molemmissa: twentytwentyfive, twentytwentyfour, twentytwentythree
```

---

## ⚙️ Konfiguraatio

Työkalu luo automaattisesti `wp-gitops-config.json` tiedoston Git-repositorioon ensimmäisellä ajolla.

**Oletuskonfiguraatio:**
```json
{
  "sync_themes": true,
  "sync_plugins": true,
  "sync_uploads": false,
  "excluded_plugins": ["akismet", "hello"],
  "last_sync": "2026-01-16T22:32:10.448636"
}
```

### Konfiguraation muokkaus

Muokkaa `wp-gitops-config.json` tiedostoa suoraan:

```bash
nano ~/wp-gitops-repo/wp-gitops-config.json
```

**Asetukset:**
- `sync_themes` - Synkronoi teemat (true/false)
- `sync_plugins` - Synkronoi pluginit (true/false)
- `sync_uploads` - Synkronoi uploads-kansio (true/false, **EI SUOSITELLA**)
- `excluded_plugins` - Lista plugineista joita ei synkronoida
- `last_sync` - Viimeisin synkronointiaika (automaattinen)

**Esimerkki - Sulje pois useita plugineja:**
```json
{
  "excluded_plugins": ["akismet", "hello", "woocommerce", "jetpack"]
}
```

---

## 🔄 Tyypilliset työnkulut

### 1. Ensimmäinen synkronointi

```bash
# Tarkista tilanne
wpgit status

# Testaa mitä synkronoitaisiin
wpgit push --dry-run

# Tee ensimmäinen synkronointi
wpgit push -m "Initial WordPress sync"

# Tarkista Git-historia
cd ~/wp-gitops-repo
git log
```

### 2. Päivitä teema WordPressissä ja synkronoi

```bash
# 1. Tee muutoksia WordPressin teemoihin
nano /var/www/html/wordpress/wp-content/themes/your-theme/style.css

# 2. Synkronoi Gitiin
wpgit push -m "Päivitetty teeman CSS"

# 3. Pushaa remote-repositorioon (jos käytössä)
cd ~/wp-gitops-repo
git push origin main
```

### 3. Palauta teema Gitistä

```bash
# 1. Tee muutoksia Git-repossa
cd ~/wp-gitops-repo/themes/your-theme
nano style.css
git add .
git commit -m "Korjattu CSS-bugi"

# 2. Synkronoi WordPressiin
wpgit pull

# 3. Tarkista että muutokset ovat WordPressissä
cat /var/www/html/wordpress/wp-content/themes/your-theme/style.css
```

### 4. Työskentely tiimissä (remote Git-repo)

```bash
# 1. Lisää remote-repositorio
cd ~/wp-gitops-repo
git remote add origin https://github.com/username/wp-gitops-repo.git

# 2. Synkronoi WordPress → Git
wpgit push -m "Päivitetty plugin"

# 3. Pushaa remote-repositorioon
git push origin main

# Toisella palvelimella:
# 1. Pullaa muutokset Gitistä
cd ~/wp-gitops-repo
git pull origin main

# 2. Synkronoi WordPressiin
wpgit pull
```

---

## 🛡️ Turvallisuus

### Varmuuskopiot

Työkalu luo automaattisesti varmuuskopion ennen `pull`-komentoa:

```bash
$ wpgit pull

🔄 Synkronoidaan Git → WordPress...
✓ Varmuuskopio luotu: /root/wp-gitops-repo/backups/pre_sync_20260116_223707
```

**Varmuuskopioiden sijainti:**
```
~/wp-gitops-repo/backups/
├── pre_sync_20260116_223707/
├── pre_sync_20260116_224843/
└── ...
```

### Dry-run tila

Testaa aina ensin `--dry-run` tilassa:

```bash
wpgit pull --dry-run
```

### Git-historia

Kaikki muutokset tallennetaan Git-historiaan:

```bash
cd ~/wp-gitops-repo
git log --oneline
git diff HEAD~1
```

### Mitä EI pitäisi synkronoida

- ❌ **wp-config.php** - Sisältää tietokanta-salasanat
- ❌ **uploads-kansio** - Voi olla erittäin suuri
- ❌ **cache-tiedostot** - Ei tarvita versionhallinnassa
- ❌ **Salaisuudet ja API-avaimet** - Käytä ympäristömuuttujia

---

## 🐛 Yleisimmät ongelmat

### 1. "Not a git repository" virhe

**Ongelma:**
```
Git-virhe: fatal: not a git repository
```

**Ratkaisu:**
```bash
cd ~/wp-gitops-repo
git init
git config user.email "sinun@email.com"
git config user.name "Sinun Nimi"
```

### 2. Oikeusongelmat

**Ongelma:**
```
Permission denied
```

**Ratkaisu:**
```bash
# Tarkista oikeudet
ls -la /var/www/html/wordpress/wp-content

# Korjaa tarvittaessa (käytä oikeita käyttäjiä)
sudo chown -R www-data:www-data /var/www/html/wordpress/wp-content
```

### 3. Väärä WordPress-polku

**Ongelma:**
```
ValueError: WordPress-polku ei löydy
```

**Ratkaisu:**
```bash
# Etsi WordPress-asennus
find /var -name "wp-config.php" 2>/dev/null

# Päivitä alias oikealla polulla
nano ~/.bashrc
```

### 4. Merge-konfliktit

**Ongelma:**
Git-merge-konfliktit kun työskennellään tiimissä.

**Ratkaisu:**
```bash
cd ~/wp-gitops-repo

# Tarkista konflikti
git status

# Ratkaise konflikti manuaalisesti
nano [konfliktoiva-tiedosto]

# Merkitse ratkaistuksi
git add [konfliktoiva-tiedosto]
git commit -m "Ratkaistu merge-konflikti"

# Synkronoi WordPressiin
wpgit pull
```

---

## 📁 Projektin rakenne

```
~/wp-gitops-repo/
├── .git/                          # Git-repositorio
├── backups/                       # Automaattiset varmuuskopiot
│   ├── pre_sync_20260116_223707/
│   └── pre_sync_20260116_224843/
├── themes/                        # WordPress-teemat
│   ├── twentytwentyfive/
│   ├── twentytwentyfour/
│   └── custom-theme/
├── plugins/                       # WordPress-pluginit
│   ├── contact-form-7/
│   └── custom-plugin/
├── wp-gitops-config.json         # Työkalun konfiguraatio
└── README.md                     # (valinnainen) Projektin dokumentaatio
```

---

## 🔮 Tulevat ominaisuudet

Suunnitteilla olevat ominaisuudet:

- [ ] wp-config.php hallinta (turvallisesti)
- [ ] Tietokanta-migraatiot
- [ ] Webhook-tuki automaattiseen deploymentiin
- [ ] Rollback-toiminto (palaa edelliseen versioon)
- [ ] CI/CD-integraatio (GitHub Actions, GitLab CI)
- [ ] Slack/Discord-notifikaatiot
- [ ] Web-käyttöliittymä

---

## 🤝 Kontribuutiot

Kontribuutiot ovat tervetulleita! 

1. Forkkaa projekti
2. Luo feature-branch (`git checkout -b feature/amazing-feature`)
3. Committaa muutokset (`git commit -m 'Add amazing feature'`)
4. Pushaa branch (`git push origin feature/amazing-feature`)
5. Avaa Pull Request

---

## 📄 Lisenssi

MIT License - vapaasti käytettävissä ja muokattavissa.

---

## 💬 Tuki

Ongelmia? Kysymyksiä?

- 🐛 Avaa issue GitHubissa
- 📖 Lue dokumentaatio: [Wiki](https://github.com/username/wordpress-gitops-sync/wiki)

---

## 🙏 Kiitokset

Kehitetty DevOps- ja WordPress-yhteisön tarpeisiin.

**Tekijä:** [Kimmo Näveri](https://github.com/herraKoo)  
**Versio:** 1.0.0  
**Viimeisin päivitys:** Tammikuu 2026

---

## ⭐ Pidätkö projektista?

Anna tähti GitHubissa ja jaa projekti eteenpäin! 🚀
