from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import json

app = Flask(__name__)

# Function to create a database connection
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="153.92.15.25",
            user="u407283636_amitbidlan",
            password="l]7d9@]XVo0%",
            database="u407283636_TOWN_WORK_JOB"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None
        
@app.route('/')
def hello():
    return "Hello, World!"
    
# Route to get data from a table based on brand_code, job_type, and translation code
@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        brand_code = request.args.get('brand_code')
        translation_code = request.args.get('translation_code')
        job_type = request.args.get('job_type')

        if not brand_code or not translation_code:
            return jsonify({"error": "brand_code and translation_code are required parameters"}), 400

        valid_translation_columns = [
            "jp_translation", "en_translation", "hi_translation", "es_translation",
            "fr_translation", "de_translation", "ch_translation", "ne_translation",
            "my_translation", "vi_translation"
        ]

        if translation_code not in valid_translation_columns:
            return jsonify({"error": "Invalid translation_code"}), 400

        connection = create_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor(dictionary=True)  # Use dictionary=True to get column names

        # Build the query based on provided parameters
        query = f"""
            SELECT 
                job_id, job_type, brand_code, prefecture, end_point, listing_date, expiry_date, {translation_code} 
            FROM 
                aichi_featured_jobs 
            WHERE 
                brand_code = %s
        """
        params = [brand_code]

        if job_type:
            query += " AND job_type = %s"
            params.append(job_type)

        cursor.execute(query, tuple(params))
        result = cursor.fetchall()

        cursor.close()
        connection.close()

        # Convert translation_code field to JSON if possible
        for row in result:
            if row.get(translation_code):
                try:
                    row[translation_code] = json.loads(row[translation_code])
                except json.JSONDecodeError as e:
                    print(f"JSON decode error for row: {row['job_id']}. Error: {e}")
                    row[translation_code] = None

        return jsonify({"data": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
