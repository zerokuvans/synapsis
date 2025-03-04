from flask import Flask, request, jsonify
from datetime import date

app = Flask(__name__)

@app.route('/check_submission', methods=['GET'])
def check_submission():
    user_id = request.args.get('user_id')
    submission_date = request.args.get('date')
    
    # Replace with your actual database query logic
    # Example: Check if a record exists in the database for the given user_id and date
    submission_exists = False  # Replace with actual database check

    # Example database check (pseudo-code):
    # submission_exists = db.session.query(Submission).filter_by(user_id=user_id, date=submission_date).first() is not None

    return jsonify({'submitted': submission_exists})

if __name__ == '__main__':
    app.run(debug=True)