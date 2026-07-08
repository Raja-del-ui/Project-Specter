Project Specter: AI-Driven EDR vs. Advanced Persistent Threats

Author: Raja Zulqarnain | Institution: AUST | Date: 2026

Overview

Project Specter is an advanced, dual-component cybersecurity research framework designed to simulate modern ransomware behaviors and counter them using unsupervised Machine Learning.

Traditional antivirus systems rely on static signatures, rendering them blind to zero-day, polymorphic threats. This project abandons signatures entirely, utilizing Shannon Entropy and I/O Modification Velocity to mathematically identify cryptographic anomalies in real-time.

Architecture

The Red Team: Multithreaded Cryptographic Engine

The attack simulator replicates the "Swarm" methodology used by modern ransomware cartels.

Concurrency: Utilizes ThreadPoolExecutor to map encryption routines across all available logical CPU cores, maximizing destruction speed.

Cryptography: Implements AES-256-CBC with strict PKCS7 padding.

Exfiltration: Simulates the "Double-Extortion" pipeline via localized data staging.

The Blue Team: Behavioral AI EDR

The defensive daemon monitors the host filesystem for mathematical anomalies.

Feature Extraction: Calculates the base-2 Shannon Entropy of modified files. (Plaintext ~3.5 | AES Ciphertext ~7.99).

Isolation Forest Model: An unsupervised ML model evaluates the entropy against I/O velocity to classify the behavior.

Execution Race Condition: Upon detecting an anomaly (predict == -1), the EDR triggers an automated OS-level kill switch via psutil, assassinating the malicious process in milliseconds.

⚠️ Lab Safety & Disclaimer

This software is an air-gapped academic simulation. It does not possess lateral network movement (worm) capabilities and strictly targets a designated local dummy sandbox. It is engineered specifically for defensive research at Abbottabad University of Science and Technology (AUST).

Copyright & Originality Declaration

Copyright © 2026 Zuni. All Rights Reserved.
This repository and its contents (including the Swarm logic, ML implementation, and mathematical models) are the exclusive intellectual property of the author. Unauthorized cloning, reproduction, or presentation of this logic by third parties constitutes academic plagiarism.