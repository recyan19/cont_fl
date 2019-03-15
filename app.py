from flask import Flask, render_template, flash, request, redirect, url_for
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, PasswordField
import os
import re
import pickle
from hashlib import sha256

# App Config
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = b'_5#y2L"F4Q8z\n\xec]/'


class ContactForm(Form):
    first_name = TextField(
        'First name:',
        validators=[validators.required()]
    )
    surname = TextField(
        'Surname:',
        #validators=[validators.Length(max=35)]
    )
    company = TextField(
        'Company:',
        #validators=[validators.Length(max=35)]
    )
    address = TextField(
        'Address:',
        #validators=[validators.Length(max=35)]
    )
    telephone = TextField(
        'Phone:',
        #validators=[validators.Length(min=10, max=15)]
    )
    email = TextField(
        'Email:',
        #validators=[validators.Length(min=3, max=35)]
    )


class BookForm(Form):
    file = TextField(
        'Filename:',
        validators=[validators.required()]
    )
    password = PasswordField(
        'Password:',
        validators = [validators.required()]
    )


class BookAuthForm(Form):
    password = PasswordField(
        'Password:',
        validators=[validators.required()]
    )


class ContactUpdateForm(Form):
    first_name = TextField(
        'First name:',
    )
    surname = TextField(
        'Surname:',
    )
    company = TextField(
        'Company:',
    )
    address = TextField(
        'Address:',
    )
    telephone = TextField(
        'Phone:',
    )
    email = TextField(
        'Email:',
    )


class SearchContactForm(Form):
    search_field = TextField(
        'Search',
        validators = [validators.required()]
    )


class Contact:
    def __init__(self, first_name, surname, company, address, telephone, email):
        self.first_name = first_name
        self.surname = surname
        self.company = company
        self.address = address
        self.telephone = telephone
        self.email = email

    def __str__(self):
        return "Firstname: {0} Surname: {1}\nCompany: {2}\nAddress: {3}\nTelephone: {4}\nEmail: {5}\n".format(
            self.first_name, self.surname, self.company, self.address, self.telephone, self.email
        )
    # def __repr__(self):
    #     return "Firstname: {0} Surname: {1}\nCompany: {2}\nAddress: {3}\nTelephone: {4}\nEmail: {5}\n".format(
    #         self.first_name, self.surname, self.company, self.address, self.telephone, self.email
    #     )

class Contacts:
    def __init__(self):
        self.id = 0
        self.contact_dict = {}
        self.password = ''

    def add(self, contact):
        self.contact_dict[self.id] = contact
        self.id += 1

    def get(self, id_):
        if id_ in self.contact_dict:
            return self.contact_dict[id_]
        else:
            return 'Contact not found!'

    def save_book(self, file):
        #if not os.path.exists(file):
         #   self.password = sha256(getpass.getpass("Create a password: ").encode('utf_8')).hexdigest()
        with open(file, 'wb') as f:
            pickle.dump(self, f)

    def delete_contact(self, idx):
        if idx in self.contact_dict:
            self.contact_dict.pop(idx,0)
        return

    def search(self, reg):
        res = dict()
        for idx, contact in self.contact_dict.items():
            if any(re.search(reg, str(x)) for x in contact.__dict__.values()):
                res[idx] = contact
        return res



cur_book = None
book_name = None
user = [False, None]

@app.route('/')
def index():
    global user
    user[0],user[1] = False, None
    books = [b for b in os.listdir() if b.endswith('.bin')]
    print('heloo')
    return render_template('index.html', books=books)

@app.route('/book/<string:name>/', methods=['GET', 'POST'])
def book_detail(name):
    global cur_book
    global book_name
    if not user:
        return redirect(url_for('auther',name=name))
    if user[1] != name:
        return redirect(url_for('auther',name=name))
    form = SearchContactForm(request.form)
    with open(name, 'rb') as f:
        cur_book = pickle.load(f)

    ctx = cur_book.contact_dict
    book_name = name

    if request.method =='POST':
        search_field = request.form['search_field']

    if form.validate():
        return redirect(url_for('search_contacts', ctx=search_field, name=name))

    return render_template('book_detail.html', contacts=ctx, book=book_name, form=form)

@app.route("/book/<string:name>/add_contact/", methods=['GET', 'POST'])
def add_contact(name):
    global cur_book
    form = ContactForm(request.form)
    if request.method == 'POST':
        first_name = request.form['first_name']
        surname = request.form['surname']
        company = request.form['company']
        address = request.form['address']
        telephone = request.form['telephone']
        email = request.form['email']

    
    if form.validate():
        new_contact = Contact(first_name, surname, company, address, telephone, email)
        cur_book.add(new_contact)
        cur_book.save_book(name)
        return redirect(url_for('book_detail', name=name))
    
    return render_template('add_form.html', form=form)

@app.route('/create_book/', methods=['GET', 'POST'])
def create_book():
    form = BookForm(request.form)
    if request.method == 'POST':
        file = request.form['file']
        password = request.form['password']
    err = False
    if form.validate():
        if not os.path.exists(file):
            new_book = Contacts()
            new_book.password = sha256(password.encode()).hexdigest()
            new_book.save_book(file)
            return redirect(url_for('index'))
        err = "This name is already taken! Choose another one."


    return render_template('add_book.html', errors=err, form=form)

@app.route('/book/<string:name>/<int:idx>/', methods=['GET', 'POST'])
def update_contact(name, idx):
    global cur_book
    form = ContactUpdateForm(request.form)
    if request.method == 'POST':
        first_name = request.form['first_name']
        surname = request.form['surname']
        company = request.form['company']
        address = request.form['address']
        telephone = request.form['telephone']
        email = request.form['email']

        if form.validate():
            contact = cur_book.contact_dict[idx] 
            x = ['first_name','surname','company','address','telephone','email']
            for val, attr in zip([first_name,surname,company,address,telephone,email],x):
                if val:
                    contact.__dict__[attr] = val
                    cur_book.save_book(name)
            return redirect(url_for('book_detail', name=name))

    return render_template('update_contact.html', form=form, idx=idx)


@app.route('/book/<string:name>/delete/<int:idx>/', methods=['GET', 'POST'])
def delete_contact(name, idx):
    global cur_book
    cur_book.delete_contact(idx)
    cur_book.save_book(name)
    return redirect(url_for('book_detail', name=name))


@app.route('/book/<string:name>/search/<string:ctx>/')
def search_contacts(name, ctx):
    global book_name
    results = cur_book.search(ctx)
    return render_template('search_results.html', results=results, name=book_name)

@app.route('/<string:name>/authenticate/', methods=['GET', 'POST'])
def auther(name):
    global cur_book
    with open(name, 'rb') as obj:
        cur_book = pickle.load(obj)
    form = BookAuthForm(request.form)
    if request.method == 'POST':
        password = request.form['password']
    if form.validate():
        if sha256(password.encode()).hexdigest() == cur_book.password:
            global user
            user[0] = True
            user[1] = name
            return redirect(url_for('book_detail', name=name))
    return render_template('auth.html', form=form)