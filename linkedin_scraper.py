
import csv
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import os


class LinkedInScraper:
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
    
    def login(self):
        """Se connecter à LinkedIn"""
        try:
            print("\nConnexion à LinkedIn...")
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)
            
            wait = WebDriverWait(self.driver, 15)
            
            # Email
            print("Saisie de l'email...")
            email_input = wait.until(
                EC.presence_of_element_located((By.ID, "username"))
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
                EC.presence_of_element_located((By.ID, "password"))
            )
            time.sleep(1)
            password_input.clear()
            time.sleep(0.5)
            password_input.send_keys(self.password)
            time.sleep(1)
            print("✓ Mot de passe saisi")
            
            # Connexion
            print("Connexion en cours...")
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # Gérer la popup premium si elle apparaît
            self.handle_premium_popup()
            
            # Vérifier si connecté
            current_url = self.driver.current_url
            if "feed" in current_url or "login" not in current_url:
                print("✓ Connexion réussie!\n")
                return True
            else:
                print("⚠ Vérification de la connexion...")
                time.sleep(3)
                if "feed" in self.driver.current_url or "login" not in self.driver.current_url:
                    print("✓ Connexion réussie!\n")
                    return True
                else:
                    print("⚠ Vérifiez vos identifiants ou résolvez le captcha")
                    input("Appuyez sur Entrée quand vous êtes connecté...")
                    return True
            
        except Exception as e:
            print(f"⚠ Erreur: {str(e)}")
            print("Tentative de connexion manuelle...")
            input("Connectez-vous manuellement puis appuyez sur Entrée...")
            return True
    
    def handle_premium_popup(self):
        """Gérer la popup premium LinkedIn si elle apparaît"""
        try:
            print("Vérification popup premium...")
            wait = WebDriverWait(self.driver, 5)
            
            # Bouton "Ignorer" avec aria-label="Ignorer"
            dismiss_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Ignorer']"))
            )
            time.sleep(1)
            dismiss_button.click()
            print("✓ Popup premium fermée")
            time.sleep(2)
            return True
        except:
            print("  Pas de popup premium")
            return False
    
    def navigate_to_applications(self):
        """Naviguer vers la page des candidatures"""
        try:
            print("Navigation vers les candidatures...")
            time.sleep(2)
            
            wait = WebDriverWait(self.driver, 15)
            
            # Cliquer sur "Emplois" dans le menu principal
            try:
                print("Clic sur 'Emplois'...")
                jobs_link = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.global-nav__primary-link[href*='/jobs/']"))
                )
                time.sleep(1)
                jobs_link.click()
                time.sleep(3)
                print("✓ Page Emplois chargée")
            except:
                print("  Navigation directe vers /jobs/")
                self.driver.get("https://www.linkedin.com/jobs/")
                time.sleep(3)
            
            # Gérer popup premium si elle réapparaît
            self.handle_premium_popup()
            
            # Cliquer sur "Mes offres d'emploi"
            print("Clic sur 'Mes offres d'emploi'...")
            try:
                my_jobs_link = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.jobshome_nav_my_jobs[href*='/my-items/saved-jobs']"))
                )
                time.sleep(1)
                self.driver.execute_script("arguments[0].scrollIntoView(true);", my_jobs_link)
                time.sleep(1)
                my_jobs_link.click()
                time.sleep(3)
                print("✓ Page 'Mes offres d'emploi' chargée\n")
                return True
            except:
                print("  Navigation directe...")
                self.driver.get("https://www.linkedin.com/my-items/saved-jobs")
                time.sleep(4)
                print("✓ Page chargée\n")
                return True
                
        except Exception as e:
            print(f"✗ Erreur: {str(e)}")
            return False
    
    def scrape_applications(self):
        """Scraper les candidatures LinkedIn"""
        print("Scraping en cours...\n")
        
        try:
            # Scroll pour charger toutes les candidatures
            print("Chargement des candidatures...")
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 20
            
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
            
            # Trouver tous les li contenant les candidatures
            applications = self.driver.find_elements(By.CSS_SELECTOR, "li.yhpGAPjgHGjYzneFpAPodujlqkuDYHo")
            
            if not applications:
                print("\n⚠ Aucune candidature trouvée.")
                print("Sauvegarde du HTML pour analyse...\n")
                with open("linkedin_debug.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print("✓ Fichier sauvegardé: linkedin_debug.html")
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
        """Extraire les données d'une candidature LinkedIn"""
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
            # Titre du poste - dans le lien principal
            try:
                titre_element = element.find_element(By.CSS_SELECTOR, "span.mDxlVZpOEwYbVMZvoRMULBMbfAawZwfAKLs a")
                candidature['titre'] = titre_element.text.strip()
                
                # URL de l'offre
                href = titre_element.get_attribute('href')
                if href:
                    candidature['url'] = href.split('?')[0]  # Nettoyer les paramètres
            except:
                # Alternative
                try:
                    titre_element = element.find_element(By.CSS_SELECTOR, "a[href*='/jobs/view/']")
                    candidature['titre'] = titre_element.text.strip()
                    candidature['url'] = titre_element.get_attribute('href').split('?')[0]
                except:
                    pass
            
            # Entreprise - div avec classe JeisfcQxfDFFMdVSREsrAauYHRTcoJyOJlbQ
            try:
                entreprise_element = element.find_element(By.CSS_SELECTOR, "div.JeisfcQxfDFFMdVSREsrAauYHRTcoJyOJlbQ")
                candidature['entreprise'] = entreprise_element.text.strip()
            except:
                # Alternative avec l'image alt
                try:
                    img = element.find_element(By.CSS_SELECTOR, "img[alt]")
                    candidature['entreprise'] = img.get_attribute('alt')
                except:
                    pass
            
            # Lieu - div avec classe srGyRypJKeCgAbpbwRWldGAxUIsdaSKYRPYRPYY
            try:
                lieu_element = element.find_element(By.CSS_SELECTOR, "div.srGyRypJKeCgAbpbwRWldGAxUIsdaSKYRPYRPYY")
                candidature['lieu'] = lieu_element.text.strip()
            except:
                pass
            
            # Date de candidature - dans reusable-search-simple-insight__text
            try:
                date_element = element.find_element(By.CSS_SELECTOR, "span.pBvwPmReNorAKornIxcbjnEcTsSjWiJQ")
                date_text = date_element.text.strip()
                candidature['date_candidature'] = date_text
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
            filename = f"candidatures_linkedin_{timestamp}.csv"
            
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
    print("  LinkedIn Candidatures Scraper")
    print("  Version simplifiée - Microsoft Edge")
    print("="*60 + "\n")
    
    email = input("📧 Email LinkedIn: ").strip()
    password = input("🔒 Mot de passe: ").strip()
    
    if not email or not password:
        print("\n✗ Email et mot de passe requis!")
        return
    
    print("\n" + "="*60)
    scraper = LinkedInScraper(email, password)
    success = scraper.run()
    
    if success:
        print("\n✓ Terminé avec succès!")
    else:
        print("\n⚠ Le scraping n'a pas pu être complété")
    
    print("="*60)
    input("\nAppuyez sur Entrée pour quitter...")


if __name__ == "__main__":
    main()
