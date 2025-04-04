from flask import Flask, request, jsonify, send_file, render_template
import mysql.connector
import pandas as pd
from fpdf import FPDF
import os

app = Flask(__name__)

# Database Configuration
db_config = {
    "host": "localhost",
    "user": "root", 
    "password": "nith@123",  
    "database": "machine_parameters"
}

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/store_data', methods=['POST'])
def store_data():
    try:
        # Get JSON data from frontend
        data = request.json
        material = data['material']
        spindle_speed = int(data['spindleSpeed'])
        feed_rate = int(data['feedRate'])
        depth_of_cut = float(data['depthOfCut'])
        coolant_flow = float(data['coolantFlow'])
        surface_roughness = float(data['surfaceRoughness'])
        material_removal_rate = float(data['materialRemovalRate'])

        # Insert into MySQL
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """INSERT INTO parameters (material, spindle_speed, feed_rate, depth_of_cut, coolant_flow, surface_roughness, material_removal_rate)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        values = (material, spindle_speed, feed_rate, depth_of_cut, coolant_flow, surface_roughness, material_removal_rate)
        cursor.execute(sql, values)
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Data stored successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def fetch_data():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT material, spindle_speed, feed_rate, depth_of_cut, coolant_flow, surface_roughness, material_removal_rate FROM parameters")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

# Function to generate PDF
def generate_pdf():
    data = fetch_data()
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Machine Parameters Report", ln=True, align='C')
    pdf.ln(10)
    
    # Table Headers
    pdf.set_font("Arial", style='B', size=12)
    columns = ["Material", "Spindle Speed", "Feed Rate", "Depth of Cut", "Coolant Flow", "SR", "MRR"]
    col_widths = [30, 30, 30, 30, 30, 20, 20]

    for i in range(len(columns)):
        pdf.cell(col_widths[i], 10, columns[i], border=1, align='C')
    pdf.ln()
    
    # Table Rows
    pdf.set_font("Arial", size=12)
    for row in data:
        for i in range(len(row)):
            pdf.cell(col_widths[i], 10, str(row[i]), border=1, align='C')
        pdf.ln()
    
    pdf_path = "machine_parameters.pdf"
    pdf.output(pdf_path)
    return pdf_path

@app.route('/download_pdf')
def download_pdf():
    pdf_path = generate_pdf()
    return send_file(pdf_path, as_attachment=True)



if __name__ == '__main__':
    app.run(debug=True)
