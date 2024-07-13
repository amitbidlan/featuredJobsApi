from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

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
        job_type = request.args.get('job_type')
        translation_code = request.args.get('translation_code')

        if not translation_code:
            return jsonify({"error": "translation_code is a required parameter"}), 400

        valid_translation_columns = [
            "jp_translation", "en_translation", "hi_translation", "es_translation",
            "fr_translation", "de_translation", "ch_translation", "ne_translation",
            "my_translation", "vi_translation"
        ]

        if translation_code not in valid_translation_columns:
            return jsonify({"error": "Invalid translation_code"}), 400
        
        if translation_code == 'en_translation':
            my_columns = [
                "job_id", "job_type", "brand_code", "prefecture", "end_point", 
                "listing_date", "expiry_date", "company_name_en", "job_detail_caption_en", 
                "job_detail_text_en", "company_address_en", "latitude", "longitude", 
                "image_url", "phone_number", "job_type_en", "salary_en", "working_hours_en"
            ]
        elif translation_code == 'jp_translation':
            my_columns = [
                "job_id", "job_type", "brand_code", "prefecture", "end_point", 
                "listing_date", "expiry_date", "company_name_jp", "job_detail_caption_jp", 
                "job_detail_text_jp", "company_address_jp", "latitude", "longitude", 
                "image_url", "phone_number", "job_type_jp", "salary_jp", "working_hours_jp"
            ]
        
        columns_str = ', '.join(my_columns)

        connection = create_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor(dictionary=True)  # Use dictionary=True to get column names

        # Build the query based on provided parameters
        query = f"""
            SELECT {columns_str}
            FROM aichi_featured_jobs
            WHERE 1=1
        """
        params = []

        if brand_code:
            query += " AND brand_code = %s"
            params.append(brand_code)

        if job_type:
            query += " AND job_type = %s"
            params.append(job_type)

        cursor.execute(query, tuple(params))
        result = cursor.fetchall()

        cursor.close()
        connection.close()

        # Modify column names in the result based on translation code
        modified_result = []
        for row in result:
            if translation_code == 'jp_translation':
                modified_row = {k.replace('_jp', ''): v for k, v in row.items()}
            elif translation_code == 'en_translation':
                modified_row = {k.replace('_en', ''): v for k, v in row.items()}
            modified_result.append(modified_row)

        return jsonify({"data": modified_result})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
