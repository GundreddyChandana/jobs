from flask import Flask, request, jsonify, render_template
import pandas as pd
import pickle
import re

app = Flask(__name__)

# Load the dataset from a pickle file
with open("Jobs_Dataset.pkl", "rb") as file:
    df = pickle.load(file)

# Function to clean and normalize skills
def clean_skills(skills):
    if pd.isna(skills) or skills.strip() == "":
        return ""  # Handle NaN values
    skills = skills.lower().strip()  # Convert to lowercase and remove extra spaces
    skills = re.sub(r'[\{\}\[\]\(\)"]', '', skills)  # Remove unwanted characters ({}, [], (), "")
    skills = skills.replace("|", ", ").replace("/", ", ")  # Ensure proper separation
    return skills

# Clean the skills column
df["skills"] = df["skills"].apply(clean_skills)

def recommend_jobs(user_skills):
    """Recommend jobs based on user input skills."""
    
    # Convert user skills into a set
    user_skills = set(user_skills.lower().replace('"', '').split(", "))

    print("User entered skills:", user_skills)  # Debug print

    # Ensure correct skill matching
    df["skill_match"] = df["skills"].apply(
        lambda x: len(user_skills.intersection(set(x.split(", "))))
    )

    # Get jobs with at least one skill match
    recommended_jobs = df[df["skill_match"] > 0].sort_values(by="skill_match", ascending=False)

    # Debugging output
    if not recommended_jobs.empty:
        print("✅ Matching jobs found!")
        print(recommended_jobs[['jobTitle', 'location', 'jobType', 'minBudget', 'maxBudget', 'skills']].head()) 
    else:
        print("❌ No matching jobs found.")

    return recommended_jobs[['jobTitle', 'location', 'jobType', 'minBudget', 'maxBudget']].to_dict(orient="records")

@app.route('/')
def home():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    """Handle job recommendation requests."""
    try:
        user_input = request.json.get("skills", "")
        recommendations = recommend_jobs(user_input)

        if recommendations:
            return jsonify({"status": "success", "jobs": recommendations})
        else:
            return jsonify({"status": "error", "message": "No matching jobs found."})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
