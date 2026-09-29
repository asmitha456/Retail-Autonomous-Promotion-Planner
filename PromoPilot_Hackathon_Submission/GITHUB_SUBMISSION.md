# GitHub submission steps

1. Create a new public GitHub repository, for example:
   `promopilot-autonomous-promotion-planner`
2. Upload the contents of this folder.
3. Confirm the repository root contains `app.py`, `planner.py`, `requirements.txt`, `README.md`, and `sample_data/`.
4. In the repository, open **Actions/Code** only if you want to add CI later; the prototype already includes pytest tests.

### Local commands
```bash
git init
git add .
git commit -m "Initial PromoPilot hackathon prototype"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/promopilot-autonomous-promotion-planner.git
git push -u origin main
```

### 60-second judge setup
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Demo values
- Marketing budget: ₹10,000
- Minimum margin: 20%
- Target inventory clearance: 35%
- Business context: `Diwali festive campaign for India. Prioritize inventory clearance without damaging margin.`
