
import csv
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


class JobTeaserScraper:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.driver = None
        self.candidatures = []
        
    def setup_driver(self):
        """Configure Edge (préinstallé sur Windows)"""
        print("Configuration de Microsoft Edge...")
        try:
            options = webdriver.EdgeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--start-maximized')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            self.driver = webdriver.Edge(options=options)
            self.driver.implicitly_wait(10)
            print("✓ Edge configuré!\n")
            return True
        except Exception as e:
            print(f"✗ Erreur: {str(e)}\n")
            print("Solution:")
            print("1. Téléchargez Edge WebDriver: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
            print("2. Extrayez msedgedriver.exe dans ce dossier")
            print("3. OU ajoutez-le à votre PATH")
            return False
        
    def handle_cookies(self):
        """Gérer la popup des cookies si elle apparaît"""
        try:
            print("Vérification popup cookies...")
            wait = WebDriverWait(self.driver, 5)
            cookie_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".didomi-continue-without-agreeing"))
            )
            cookie_button.click()
            print("✓ Cookies refusés")
            # Attendre que la popup disparaisse complètement
            time.sleep(3)
            return True
        except:
            print("  Pas de popup cookies (ou déjà gérée)")
            return False
    
    def login(self):
        """Se connecter à JobTeaser avec les sélecteurs exacts"""
        try:
            print("\nConnexion à JobTeaser...")
            self.driver.get("https://www.jobteaser.com/fr/users/sign_in")
            time.sleep(2)
            
            # Gérer les cookies et attendre
            cookies_handled = self.handle_cookies()
            if cookies_handled:
                print("Attente après refus des cookies...")
                time.sleep(2)
            
            wait = WebDriverWait(self.driver, 15)
            
            # Cliquer sur le bouton "JobTeaser Connect"
       
            print("Recherche du bouton JobTeaser Connect...")
            # Attendre que le bouton soit vraiment cliquable
            connect_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.jds-Button[href*='/users/auth/connect']"))
                )
                # Scroll vers le bouton au cas où
            self.driver.execute_script("arguments[0].scrollIntoView(true);", connect_button)
            time.sleep(1)
            print("Clic sur JobTeaser Connect...")
            connect_button.click()
            time.sleep(3)
            print("✓ Redirection vers la page de connexion")
            
            
            # Email
            print("Saisie de l'email...")
            email_input = wait.until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            time.sleep(1)
            email_input.clear()
            time.sleep(0.5)
            email_input.send_keys(self.email)
            time.sleep(1)
            print("✓ Email saisi")
            
            # Mot de passe
            print("Saisie du mot de passe...")
            password_input = wait.until(
                EC.presence_of_element_located((By.ID, "passwordInput"))
            )
            time.sleep(1)
            password_input.clear()
            time.sleep(0.5)
            password_input.send_keys(self.password)
            time.sleep(1)
            print("✓ Mot de passe saisi")
            
            # Clic sur le bouton de connexion
            print("Clic sur le bouton Connexion...")
            login_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'].bg-emerald-default"))
            )
            time.sleep(1)
            # Scroll vers le bouton pour s'assurer qu'il est visible
            self.driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
            time.sleep(0.5)
            login_button.click()
            time.sleep(1)
            
            print("Connexion en cours...")
            time.sleep(5)
            
            # Vérifier si connecté
            current_url = self.driver.current_url
            if "dashboard" in current_url or "sign_in" not in current_url:
                print("✓ Connexion réussie!\n")
                return True
            else:
                print("⚠ Vérification de la connexion...")
                time.sleep(3)
                if "dashboard" in self.driver.current_url:
                    print("✓ Connexion réussie!\n")
                    return True
                else:
                    print("⚠ Vérifiez vos identifiants dans le navigateur")
                    input("Appuyez sur Entrée quand vous êtes connecté...")
                    return True
            
        except Exception as e:
            print(f"⚠ Erreur: {str(e)}")
            print("Tentative de connexion manuelle...")
            input("Connectez-vous manuellement dans le navigateur puis appuyez sur Entrée...")
            return True
    
    def navigate_to_applications(self):
        """Naviguer vers la page des candidatures"""
        try:
            print("Navigation vers les candidatures...")
            time.sleep(2)
            
            # Option 1: Essayer de cliquer sur le lien dans le dashboard
            try:
                wait = WebDriverWait(self.driver, 10)
                applications_link = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/fr/dashboard/my_applications']"))
                )
                time.sleep(1)
                # Scroll vers le lien
                self.driver.execute_script("arguments[0].scrollIntoView(true);", applications_link)
                time.sleep(1)
                applications_link.click()
                time.sleep(3)
                print("✓ Page chargée via le lien\n")
                return True
            except:
                # Option 2: Navigation directe
                print("  Navigation directe...")
                self.driver.get("https://www.jobteaser.com/fr/dashboard/my_applications")
                time.sleep(4)
                print("✓ Page chargée\n")
                return True
                
        except Exception as e:
            print(f"✗ Erreur: {str(e)}")
            return False
    
    def scrape_applications(self):
        """Scraper les candidatures avec les sélecteurs exacts"""
        print("Scraping en cours...\n")
        
        try:
            # Scroll pour charger toutes les candidatures
            print("Chargement des candidatures...")
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 15
            
            while scroll_attempts < max_scrolls:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_attempts += 1
                print(f"  Scroll {scroll_attempts}...")
            
            print("\nRecherche des candidatures...")
            
            # Utiliser le sélecteur exact : li contenant des cards avec data-testid="applications-card"
            applications = self.driver.find_elements(By.CSS_SELECTOR, "li div[data-testid='applications-card']")
            
            if not applications:
                print("  Tentative avec sélecteur alternatif...")
                # Essayer d'autres sélecteurs basés sur votre HTML
                selectors = [
                    "div[data-testid='applications-card']",
                    ".JobAdCard_main__1mTeA",
                    "div.sk-Card_main__0BVRy",
                    ".sk-CardContainer_container__PNt2O"
                ]
                
                for selector in selectors:
                    applications = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if applications:
                        print(f"✓ Sélecteur trouvé: {selector}")
                        break
            
            if not applications:
                print("\n⚠ Aucune candidature trouvée.")
                print("Sauvegarde du HTML pour analyse...\n")
                with open("jobteaser_debug.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print("✓ Fichier sauvegardé: jobteaser_debug.html")
                return False
            
            print(f"✓ {len(applications)} candidatures trouvées\n")
            
            # Extraire les données
            for idx, app in enumerate(applications, 1):
                try:
                    candidature = self.extract_application_data(app, idx)
                    if candidature and candidature['titre'] != 'N/A':
                        self.candidatures.append(candidature)
                        entreprise_display = candidature['entreprise'][:30]
                        titre_display = candidature['titre'][:40]
                        print(f"  [{idx:3d}] ✓ {entreprise_display:30s} | {titre_display}")
                except Exception as e:
                    print(f"  [{idx:3d}] ⚠ Erreur: {str(e)[:50]}")
                    continue
            
            print(f"\n{'='*60}")
            print(f"✓ {len(self.candidatures)} candidatures extraites avec succès!")
            print(f"{'='*60}\n")
            return True
            
        except Exception as e:
            print(f"\n✗ Erreur: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def extract_application_data(self, element, index):
        """Extraire les données d'une candidature avec les sélecteurs exacts"""
        candidature = {
            'id': index,
            'titre': 'N/A',
            'entreprise': 'N/A',
            'lieu': 'N/A',
            'date_candidature': 'N/A',
            'statut': 'En attente',
            'type_contrat': 'N/A',
            'url': 'N/A'
        }
        
        try:
            # Titre du poste - dans h3 avec classe JobAdCard_title__l2BSO
            try:
                titre_element = element.find_element(By.CSS_SELECTOR, "h3.JobAdCard_title__l2BSO a")
                candidature['titre'] = titre_element.text.strip()
            except:
                # Alternative
                try:
                    titre_element = element.find_element(By.CSS_SELECTOR, "h3 a")
                    candidature['titre'] = titre_element.text.strip()
                except:
                    pass
            
            # Entreprise - p avec data-testid="applications-card-company-name"
            try:
                entreprise_elements = element.find_elements(By.CSS_SELECTOR, "p[data-testid='applications-card-company-name']")
                if entreprise_elements:
                    candidature['entreprise'] = entreprise_elements[0].text.strip()
            except:
                # Alternative avec img alt
                try:
                    img = element.find_element(By.CSS_SELECTOR, "img[data-testid='applications-card-company-logo']")
                    candidature['entreprise'] = img.get_attribute('alt')
                except:
                    pass
            
            # Lieu - span dans div avec data-testid="applications-card-location"
            try:
                lieu_div = element.find_element(By.CSS_SELECTOR, "div[data-testid='applications-card-location'] span")
                candidature['lieu'] = lieu_div.text.strip()
            except:
                pass
            
            # Type de contrat - span dans div avec data-testid="applications-card-contract"
            try:
                contrat_div = element.find_element(By.CSS_SELECTOR, "div[data-testid='applications-card-contract'] span")
                candidature['type_contrat'] = contrat_div.text.strip()
            except:
                pass
            
            # Date de candidature - p avec data-testid="applications-card-application-date"
            try:
                date_element = element.find_element(By.CSS_SELECTOR, "p[data-testid='applications-card-application-date']")
                date_text = date_element.text.strip()
                # Extraire uniquement la date (ex: "Candidature envoyée le 01/11/2025" -> "01/11/2025")
                if "le " in date_text:
                    candidature['date_candidature'] = date_text.split("le ")[-1]
                else:
                    candidature['date_candidature'] = date_text
            except:
                pass
            
            # URL - lien dans h3 ou a.JobAdCard_link__LMtBN
            try:
                link = element.find_element(By.CSS_SELECTOR, "a.JobAdCard_link__LMtBN")
                href = link.get_attribute('href')
                if href:
                    # Construire l'URL complète si nécessaire
                    if href.startswith('/'):
                        candidature['url'] = f"https://www.jobteaser.com{href}"
                    else:
                        candidature['url'] = href
            except:
                pass
            
        except Exception as e:
            print(f"    Erreur extraction: {str(e)}")
        
        return candidature
    
    def save_to_csv(self):
        """Sauvegarder en CSV"""
        if not self.candidatures:
            print("⚠ Aucune candidature à sauvegarder")
            return False
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"candidatures_jobteaser_{timestamp}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['id', 'titre', 'entreprise', 'lieu', 'date_candidature', 
                             'statut', 'type_contrat', 'url']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.candidatures)
            
            print(f"\n{'='*60}")
            print(f"✓✓✓ SUCCÈS! ✓✓✓")
            print(f"{'='*60}")
            print(f"Fichier créé: {filename}")
            print(f"Nombre de candidatures: {len(self.candidatures)}")
            print(f"{'='*60}\n")
            return True
            
        except Exception as e:
            print(f"✗ Erreur sauvegarde: {str(e)}")
            return False
    
    def close(self):
        """Fermer le navigateur"""
        if self.driver:
            try:
                print("Fermeture du navigateur...")
                time.sleep(2)
                self.driver.quit()
                print("✓ Navigateur fermé")
            except:
                pass
    
    def run(self):
        """Exécuter le scraping"""
        try:
            if not self.setup_driver():
                return False
            
            if not self.login():
                print("Abandon...")
                return False
            
            if not self.navigate_to_applications():
                return False
            
            if not self.scrape_applications():
                return False
            
            self.save_to_csv()
            return True
            
        except KeyboardInterrupt:
            print("\n\n⚠ Interruption par l'utilisateur (Ctrl+C)")
            return False
        except Exception as e:
            print(f"\n✗ Erreur: {str(e)}")
            return False
        finally:
            self.close()


def main():
    print("\n" + "="*60)
    print("  JobTeaser Candidatures Scraper")
    print("  Version simplifiée - Microsoft Edge")
    print("="*60 + "\n")
    
    email = input("📧 Email JobTeaser: ").strip()
    password = input("🔒 Mot de passe: ").strip()
    
    if not email or not password:
        print("\n✗ Email et mot de passe requis!")
        return
    
    print("\n" + "="*60)
    scraper = JobTeaserScraper(email, password)
    success = scraper.run()
    
    if success:
        print("\n✓ Terminé avec succès!")
    else:
        print("\n⚠ Le scraping n'a pas pu être complété")
    
    print("="*60)
    input("\nAppuyez sur Entrée pour quitter...")


if __name__ == "__main__":
    main()
