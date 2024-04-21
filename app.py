# Flask app to validate geocoding process

from flask import Flask, render_template, request
import csv
import random
import configparser

app = Flask(__name__)

# Using configparser to obtain Google API Key for map embedding
config = configparser.ConfigParser()
config.read('config.ini')
api_key = config.get('geocoding', 'GOOGLE_API_KEY')

# Function to read data.csv file containing rows to be validated
def read_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]
    return data

# Function to write and save changes after editting in-app
def write_csv(filename, data):
    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

# Render function to generate visuals and load html and css files
@app.route('/')
def index():
    data = read_csv('data.csv')

    filtered_data = [row for row in data if not row.get('Validation')]

    if filtered_data:
        random_index = random.randint(0, len(filtered_data) - 1)
        random_row = filtered_data[random_index]
        row_index = data.index(random_row)
        message = str(len(filtered_data)) + " entries remaining"
    else:
        random_row = None
        row_index = None
        message = "All entries done! Congratulations!"

    return render_template('index.html', row=random_row, row_index=row_index, message=message, api_key=api_key)

# Submit function for when the user presses any of the buttons
@app.route('/submit', methods=['POST'])
def submit():

    response = request.form['response']
    row_id = int(request.form['row_id'])
    notes = request.form['notes']

    data = read_csv('data.csv')

    data[row_id]['Validation'] = response
    data[row_id]['Notes'] = notes

    write_csv('data.csv', data)

    return index()

if __name__ == '__main__':
    app.run(debug=True)
