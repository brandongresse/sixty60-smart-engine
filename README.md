# Sixty60 Smart Substitution & Cold-Chain Engine

A targeted backend logic engine and real-time monitoring dashboard prototype built with **Python (Flask)** and **SQLite**, designed to address core logistics challenges for on-demand grocery delivery platforms like Shoprite Sixty60.

---

## ⚡ Key Features

* **Smart Substitution Algorithm:** Automatically checks inventory status and identifies valid same-category product alternatives with price matching when an item is out of stock.
* **Cold-Chain Risk Monitor:** Tracks live delivery ETAs and temperature risks for perishable goods (dairy, frozen) to minimize spoilage and improve order quality.
* **Sixty60 Branded Dashboard:** Responsive Bootstrap interface featuring high-contrast visual cues for out-of-stock items and risk levels.
* **RESTful Endpoints:** Clean JSON endpoints for real-time inventory queries and substitution lookup.

---

## 🛠️ Tech Stack

* **Backend:** Python 3, Flask, SQLite
* **Frontend:** HTML5, CSS3, Bootstrap 5 (Sixty60 Custom Theme)
* **API Architecture:** RESTful APIs (JSON)
* **Version Control:** Git & GitHub

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Renders the live Sixty60 Smart Engine dashboard |
| `GET` | `/api/substitute/<id>` | Returns recommended substitution options for out-of-stock item |
| `GET` | `/api/deliveries` | Returns real-time status and cold-chain risk levels for active deliveries |

---

## 🎓 Disclaimer
*This project is an independent technical demonstration built for educational and portfolio purposes, inspired by Checkers Sixty60 operations.*
