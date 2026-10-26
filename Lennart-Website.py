
import os
import sys
import subprocess
import webbrowser
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext

APP_NAME = "Lennart-Website"
URL_8080 = "http://10.11.11.111:8080"
URL_8580 = "http://10.11.11.111:8580"
TUNNEL_NAME = "lennart-website"

# Speicherort der Konfiguration unter Windows
APPDATA = Path(os.environ.get("APPDATA", str(Path.home())))
CONFIG_DIR = APPDATA / APP_NAME
CONFIG_FILE = CONFIG_DIR / "wireguard.conf"


class LennartWebsite:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("650x450")
        self.root.minsize(500, 350)

        if not CONFIG_FILE.exists():
            self.show_setup()
        else:
            self.show_main()
            self.check_vpn()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_setup(self):
        self.clear()

        tk.Label(
            self.root,
            text="Lennart-Website einrichten",
            font=("Arial", 18, "bold")
        ).pack(pady=15)

        tk.Label(
            self.root,
            text="Füge deine vollständige WireGuard-Konfiguration ein."
        ).pack(pady=5)

        self.config_text = scrolledtext.ScrolledText(
            self.root,
            width=75,
            height=15
        )
        self.config_text.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=10
        )

        tk.Button(
            self.root,
            text="Konfiguration speichern",
            command=self.save_config
        ).pack(pady=10)

    def save_config(self):
        config = self.config_text.get("1.0", "end").strip()

        if "[Interface]" not in config or "[Peer]" not in config:
            messagebox.showerror(
                "Fehler",
                "Die Konfiguration muss [Interface] und [Peer] enthalten."
            )
            return

        if not any(
            line.strip().startswith("PrivateKey")
            for line in config.splitlines()
        ):
            messagebox.showerror(
                "Fehler",
                "Die Konfiguration enthält keinen PrivateKey."
            )
            return

        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            CONFIG_FILE.write_text(
                config + "\n",
                encoding="utf-8"
            )

            messagebox.showinfo(
                APP_NAME,
                "WireGuard-Konfiguration wurde lokal gespeichert."
            )

            self.show_main()
            self.check_vpn()

        except OSError as exc:
            messagebox.showerror(
                "Speicherfehler",
                f"Konfiguration konnte nicht gespeichert werden:\n{exc}"
            )

    def show_main(self):
        self.clear()

        tk.Label(
            self.root,
            text=APP_NAME,
            font=("Arial", 20, "bold")
        ).pack(pady=20)

        tk.Button(
            self.root,
            text="Webseite :8080 öffnen",
            width=30,
            command=lambda: webbrowser.open(URL_8080)
        ).pack(pady=8)

        tk.Button(
            self.root,
            text="Webseite :8580 öffnen",
            width=30,
            command=lambda: webbrowser.open(URL_8580)
        ).pack(pady=8)

        self.status = tk.Label(
            self.root,
            text="VPN-Status wird geprüft ...",
            wraplength=500
        )
        self.status.pack(pady=20)

        tk.Button(
            self.root,
            text="VPN erneut prüfen",
            command=self.check_vpn
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Konfiguration neu einrichten",
            command=self.show_setup
        ).pack(pady=5)

    def check_vpn(self):
        if not hasattr(self, "status"):
            return

        try:
            result = subprocess.run(
                [
                    "sc.exe",
                    "query",
                    f"WireGuardTunnel${TUNNEL_NAME}"
                ],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
                creationflags=getattr(
                    subprocess,
                    "CREATE_NO_WINDOW",
                    0
                )
            )

            output = (
                result.stdout + "\n" + result.stderr
            ).upper()

            if "RUNNING" in output:
                status_text = "VPN verbunden"
            elif "STOPPED" in output:
                status_text = (
                    "VPN nicht verbunden: Tunnel ist gestoppt."
                )
            elif "1060" in output:
                status_text = (
                    "WireGuard-Tunnel nicht installiert."
                )
            else:
                status_text = (
                    "Tunnel nicht gefunden oder Status unbekannt."
                )

            self.status.config(text=status_text)

        except subprocess.TimeoutExpired:
            self.status.config(
                text="Zeitüberschreitung bei der VPN-Statusprüfung."
            )

        except OSError as exc:
            self.status.config(
                text=f"Windows-Dienst konnte nicht geprüft werden: {exc}"
            )


def main():
    if sys.platform != "win32":
        print(
            "Diese Anwendung ist für Windows vorgesehen. "
            "Für die Windows-EXE nutze den GitHub-Actions-Build."
        )
        return

    root = tk.Tk()
    LennartWebsite(root)
    root.mainloop()


if __name__ == "__main__":
    main()
