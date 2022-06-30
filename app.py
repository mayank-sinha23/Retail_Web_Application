import csv
import json
from flask import Flask, render_template, flash, request, redirect, session
from werkzeug.utils import secure_filename
import glob
import os

app = Flask('__name__')

app.secret_key = "123456"
app.config['UPLOAD_FOLDER'] = 'C:\\Users\\Mukul\\PycharmProjects\\Retail-Web-application'

ALLOWED_EXTENSIONS = 'csv'


def allowed_file(filename):
    """
    Function for the allowed file extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_latest_file():
    """
    Returns the recent created file from the location.
    """
    list_of_files = glob.glob('C:\\Users\\Mukul\\PycharmProjects\\Retail-Web-application\\*')
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_file():
    """
    Route to upload the file.
    The file is saved to the app_config UPLOAD_FOLDER path.
    :return:
    """
    if request.method == 'POST':

        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist('files[]')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File successfully uploaded')

        data = []
        filename = get_latest_file()

        with open(filename) as f:
            reader = csv.DictReader(f)
            [data.append(dict(row)) for row in reader]

        return render_template("home.html", data=data, list=list, len=len, str=str)


@app.route('/create', methods=['GET', 'POST'])
def create():
    """
    Route for create.
    To create new entry for the CSV file uploaded by the user.
    :return:
    """
    if request.method == 'GET':
        # Get the CSV fields.
        fields = json.loads(request.args.get('fields').replace("'", '"'))

        return render_template("data.html", fields=fields)

    elif request.method == 'POST':
        # Form to get the details of the newly added row.
        data = dict(request.form)

        latest_file = get_latest_file()

        with open(latest_file, 'a') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            writer.writerow(data)

        # Redirect to the view page to see the updated data.
        return redirect('/view')


@app.route('/update', methods=['GET', 'POST'])
def update():
    """
    Route to update the contents of the CSV.
    Update the contents and redirect to the view page.
    :return:
    """
    # HTTP GET method
    if request.method == 'GET':
        # updated data
        data = []

        latest_file = get_latest_file()

        # open CSV file
        with open(latest_file) as rf:
            # Use CSV dict reader
            reader = csv.DictReader(rf)
            [data.append(dict(row)) for row in reader]
            return render_template("update.html", fields=data[int(request.args.get('id'))])

    # HTTP POST method
    elif request.method == 'POST':
        # updated data
        data = []
        latest_file = get_latest_file()

        with open(latest_file) as rf:
            reader = csv.DictReader(rf)
            [data.append(dict(row)) for row in reader]

        row = {}

        for key, val in dict(request.form).items():
            if key != 'Id':
                row[key] = val

        # To update the CSV row.
        data[int(request.form.get('Id'))] = row

        latest_file = get_latest_file()

        # To write to the CSV file.
        with open(latest_file, 'w') as wf:
            # create CSV dictionary writer
            writer = csv.DictWriter(wf, fieldnames=data[0].keys())

            # write CSV column names
            writer.writeheader()
            writer.writerows(data)

        # Redirect to the page to see the updated data.
        flash('Records updated successfully')
        return redirect('/view')


@app.route('/view', methods=['GET'])
def view_file():
    """
    Route to view the contents of the CSV.
    :return:
    """
    if request.method == 'GET':

        data = []
        latest_file = get_latest_file()

        with open(latest_file) as f:
            reader = csv.DictReader(f)
            [data.append(dict(row)) for row in reader]
        return render_template("home.html", data=data, list=list, len=len, str=str)


@app.route('/delete')
def delete():
    """
    Route to delete the contents of the CSV.
    :return:
    """
    latest_file = get_latest_file()
    with open(latest_file) as rf:
        data = []
        temp_data = []

        reader = csv.DictReader(rf)

        [temp_data.append(dict(row)) for row in reader]

        [
            data.append(temp_data[row])
            for row in range(0, len(temp_data))
            if row != int(request.args.get('id'))
        ]
        latest_file = get_latest_file()
        with open(latest_file, 'w') as wf:
            writer = csv.DictWriter(wf, fieldnames=data[0].keys())

            writer.writeheader()
            writer.writerows(data)

    # Redirect to the page to see the updated data.
    flash("Records updated successfully")
    return redirect('/view')


if __name__ == '__main__':
    app.run(debug=True)