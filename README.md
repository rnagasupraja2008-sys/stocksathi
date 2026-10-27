StockSathi 📦

Simple inventory management for small shops.

StockSathi is a Python-based web application designed to help small shop owners manage their inventory, track sales, and monitor stock levels.

✨ Features

- Product Management — Add products and set reorder levels.
- Stock Tracking — View and manage product quantities.
- Sales Management — Record sales and update stock levels.
- Restocking — Record replenished stock.
- Stock Validation — Prevent sales that exceed available stock.
- Dashboard — View inventory information in one place.
- CSV Data — CSV data is available, but downloading it through the application is not currently working.

🛠️ Tech Stack

- Python — Application logic
- Streamlit — Web interface
- SQLite — Database

🚀 Getting Started

Prerequisites

- Python installed on your system
- Git installed on your system

1. Clone the repository

git clone https://github.com/rnagasupraja2008-sys/stocksathi.git
cd stocksathi

2. Install dependencies

pip install -r requirements.txt

3. Run the application

streamlit run app.py

The application will open in your browser.

📁 Project Structure

stocksathi/
├── app.py
├── database.py
├── requirements.txt
├── .gitignore
└── stocksathi.db

⚠️ Current Limitations

- Data may not persist after refreshing or revisiting the deployed application.
- CSV downloading is not currently working as expected.
- The application needs further testing and feedback from small shop owners.

🔮 Future Improvements

- Improve data persistence in the deployed application.
- Fix and test CSV downloading.
- Gather feedback from small shop owners.
- Improve usability based on real-world testing.

👩‍💻 Author

R. Naga Supraja

- GitHub: "rnagasupraja2008-sys" (https://github.com/rnagasupraja2008-sys)
- Project Repository: "StockSathi" (https://github.com/rnagasupraja2008-sys/stocksathi)

---

Built with Python as part of my REVHACK journey to explore practical solutions for small businesses.