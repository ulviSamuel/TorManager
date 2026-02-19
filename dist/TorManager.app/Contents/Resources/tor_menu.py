#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rumps
import subprocess
import requests
import time
import os
import socket

# --- Configurazione ---
TOR_SOCKS_PORT = 9050
TOR_CONTROL_PORT = 9051
TOR_PROXY = f'socks5h://127.0.0.1:{TOR_SOCKS_PORT}'
CHECK_IP_URL = 'https://api.ipify.org'

# --- Funzioni di utilità ---

def is_tor_running():
    """Verifica se il demone Tor è in esecuzione (ascolta sulla porta SOCKS)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect(('127.0.0.1', TOR_SOCKS_PORT))
            return True
        except ConnectionRefusedError:
            return False

def get_current_ip(use_tor=False):
    """Ottiene l'IP pubblico, opzionalmente attraverso Tor."""
    try:
        if use_tor:
            proxies = {'http': TOR_PROXY, 'https': TOR_PROXY}
            response = requests.get(CHECK_IP_URL, proxies=proxies, timeout=10)
        else:
            response = requests.get(CHECK_IP_URL, timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        return f"Errore: {e}"

def set_system_proxy(state):
    """Attiva o disattiva il proxy SOCKS a livello di sistema per tutte le interfacce di rete."""
    try:
        result = subprocess.run(
            ["/usr/sbin/networksetup", "-listallnetworkservices"],
            capture_output=True, text=True, check=True
        )
        services = [line.strip() for line in result.stdout.split('\n')
                    if line.strip() and not line.startswith('An asterisk')]
    except subprocess.CalledProcessError:
        rumps.alert("Errore", "Impossibile ottenere la lista dei servizi di rete.")
        return

    if state == "on":
        for service in services:
            subprocess.run(
                ["/usr/sbin/networksetup", "-setsocksfirewallproxy", service, "127.0.0.1", str(TOR_SOCKS_PORT)],
                check=False
            )
            subprocess.run(
                ["/usr/sbin/networksetup", "-setsocksfirewallproxystate", service, "on"],
                check=False
            )
    else:  # "off"
        for service in services:
            subprocess.run(
                ["/usr/sbin/networksetup", "-setsocksfirewallproxystate", service, "off"],
                check=False
            )

def set_shell_proxy_env(state):
    """Imposta le variabili d'ambiente per il proxy nel Terminale (effetto limitato all'app)."""
    os.environ['ALL_PROXY'] = TOR_PROXY if state == "on" else ''
    os.environ['HTTP_PROXY'] = TOR_PROXY if state == "on" else ''
    os.environ['HTTPS_PROXY'] = TOR_PROXY if state == "on" else ''

def change_tor_identity():
    """Forza Tor a cambiare circuito (e quindi IP) tramite la porta di controllo."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', TOR_CONTROL_PORT))
            s.send(b'AUTHENTICATE ""\r\n')
            time.sleep(0.1)
            s.send(b'SIGNAL NEWNYM\r\n')
            time.sleep(0.1)
        return True
    except Exception as e:
        print(f"Errore nel cambio identità: {e}")
        return False

# --- App per la Menu Bar ---

class TorMenuApp(rumps.App):
    def __init__(self):
        # Rimuovi il quit predefinito di rumps
        super(TorMenuApp, self).__init__("TorManager", icon="icon_def.png", quit_button=None)
        self.menu = [
            rumps.MenuItem("Attiva Tor", callback=self.toggle_tor),
            rumps.MenuItem("Disattiva Tor", callback=self.toggle_tor),
            None,  # Separatore
            rumps.MenuItem("Mostra Stato e IP", callback=self.show_status),
            rumps.MenuItem("Cambia Identità (Nuovo IP)", callback=self.new_identity),
            None,  # Separatore
            rumps.MenuItem("Esci", callback=self.quit_app)
        ]
        # Determina lo stato iniziale di Tor
        self.tor_active = is_tor_running()
        print(f"Stato iniziale Tor: {self.tor_active}")
        self.update_menu_state()

    def toggle_tor(self, sender):
        """Attiva o disattiva Tor in base alla voce di menu cliccata."""
        print(f"toggle_tor chiamato con {sender.title}")
        if sender.title == "Attiva Tor":
            self.activate_tor()
        elif sender.title == "Disattiva Tor":
            self.deactivate_tor()

    def activate_tor(self):
        print("activate_tor: avvio Tor...")
        if not is_tor_running():
            subprocess.run(["/opt/homebrew/bin/brew", "services", "start", "tor"], check=False)
            time.sleep(3)  # Attendi l'avvio

        if is_tor_running():
            set_system_proxy("on")
            set_shell_proxy_env("on")
            self.tor_active = True
            self.update_menu_state()
            ip_tor = get_current_ip(use_tor=True)
            rumps.notification("Tor Attivato", "", f"Il tuo ip è {ip_tor}")
            print(f"Tor attivato, IP: {ip_tor}")
        else:
            rumps.alert("Errore", "Impossibile avviare Tor.")
            print("Errore: Tor non si avvia")

    def deactivate_tor(self):
        print("deactivate_tor: disattivo proxy e fermo Tor...")
        set_system_proxy("off")
        set_shell_proxy_env("off")
        # Ferma il demone Tor
        subprocess.run(["/opt/homebrew/bin/brew", "services", "stop", "tor"], check=False)
        self.tor_active = False
        self.update_menu_state()
        rumps.notification("Tor Disattivato", "", "Tor e proxy disattivati.")
        print("Proxy disattivato e Tor fermato")

    def update_menu_state(self):
        """Aggiorna le voci del menu in base allo stato di Tor."""
        if self.tor_active:
            # Tor attivo: Attiva Tor disabilitato, Disattiva Tor abilitato,
            # Cambia Identità abilitato, Mostra Stato abilitato
            self.menu["Attiva Tor"].set_callback(None)
            self.menu["Disattiva Tor"].set_callback(self.toggle_tor)
            self.menu["Cambia Identità (Nuovo IP)"].set_callback(self.new_identity)
            self.menu["Mostra Stato e IP"].set_callback(self.show_status)   # sempre abilitato
        else:
            # Tor spento: Attiva Tor abilitato, Disattiva Tor disabilitato,
            # Cambia Identità disabilitato, Mostra Stato abilitato
            self.menu["Attiva Tor"].set_callback(self.toggle_tor)
            self.menu["Disattiva Tor"].set_callback(None)
            self.menu["Cambia Identità (Nuovo IP)"].set_callback(None)
            self.menu["Mostra Stato e IP"].set_callback(self.show_status)   # sempre abilitato
        print(f"Menu aggiornato. Tor attivo: {self.tor_active}")

    def show_status(self, _):
        print("show_status chiamato")
        if self.tor_active and is_tor_running():
            ip_tor = get_current_ip(use_tor=True)
            rumps.notification(f"Tor Attivo", "", f"Il tuo ip è: {ip_tor}")
            print(f"Stato: attivo, IP Tor: {ip_tor}")
        else:
            ip_norm = get_current_ip(use_tor=False)
            rumps.notification("Tor Non Attivo", "", f"Il tuo ip è: {ip_norm}")
            print(f"Stato: non attivo, IP normale: {ip_norm}")

    def new_identity(self, _):
        print("new_identity chiamato")
        if not self.tor_active:
            rumps.alert("Tor Non Attivo", "Attiva Tor prima di cambiare identità.")
            return

        rumps.notification("Cambio Identità", "", "Richiedo un nuovo ip a Tor...")
        if change_tor_identity():
            time.sleep(2)  # Attendi il cambio
            nuovo_ip = get_current_ip(use_tor=True)
            rumps.notification("Nuova Identità", "", f"Nuovo ip assegnato: {nuovo_ip}")
            print(f"Nuovo IP: {nuovo_ip}")
        else:
            rumps.alert("Errore", "Non riesco a comunicare con Tor per cambiare ip.")

    def quit_app(self, _):
        print("quit_app chiamato")
        rumps.quit_application()

if __name__ == '__main__':
    TorMenuApp().run()