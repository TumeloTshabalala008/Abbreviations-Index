from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

app = Flask(__name__)

# App Configuration
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///acronyms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model (Note: 'abbreviation' is not unique)
class Acronym(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.String(50), nullable=False)  # Not unique
    full_form = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Acronym {self.abbreviation}>'

# WTForms Form
class AbbreviationForm(FlaskForm):
    abbreviation = StringField('Abbreviation', validators=[DataRequired()])
    full_form = StringField('Full Form', validators=[DataRequired()])
    description = TextAreaField('Description')

# Ensure database tables are created
with app.app_context():
    db.create_all()

# Home Route: Display all acronyms sorted by abbreviation
@app.route('/')
def index():
    acronyms = Acronym.query.order_by(Acronym.abbreviation.asc()).all()
    return render_template('index.html', acronyms=acronyms)

# API Endpoint for Live Search (searches by abbreviation) and returns sorted results
@app.route('/get_abbreviations')
def get_abbreviations():
    search_query = request.args.get('search', '').strip()
    if search_query:
        acronyms = Acronym.query.filter(Acronym.abbreviation.ilike(f"%{search_query}%")) \
                                .order_by(Acronym.abbreviation.asc()).all()
    else:
        acronyms = Acronym.query.order_by(Acronym.abbreviation.asc()).all()
    
    return jsonify([
        {
            'id': a.id,
            'abbreviation': a.abbreviation,
            'full_form': a.full_form,
            'description': a.description
        } for a in acronyms
    ])

# Create New Acronym Route using Flask-WTF
@app.route('/create', methods=['GET', 'POST'])
def create():
    form = AbbreviationForm()
    if form.validate_on_submit():
        new_acronym = Acronym(
            abbreviation=form.abbreviation.data,
            full_form=form.full_form.data,
            description=form.description.data
        )
        db.session.add(new_acronym)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create.html', form=form)

# Update an Existing Acronym Route using Flask-WTF
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    acronym = Acronym.query.get_or_404(id)
    form = AbbreviationForm(obj=acronym)
    if form.validate_on_submit():
        acronym.abbreviation = form.abbreviation.data
        acronym.full_form = form.full_form.data
        acronym.description = form.description.data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update.html', form=form, acronym=acronym)

# Delete an Acronym
@app.route('/delete/<int:id>')
def delete(id):
    acronym = Acronym.query.get_or_404(id)
    db.session.delete(acronym)
    db.session.commit()
    return redirect(url_for('index'))

# Seed Route to Populate the Database with 100 Common Abbreviations
@app.route('/seed')
def seed_data():
    abbreviations = [
        ("AI", "Artificial Intelligence", "The simulation of human intelligence in machines."),
        ("API", "Application Programming Interface", "A set of protocols for building software applications."),
        ("HTTP", "HyperText Transfer Protocol", "A protocol used for transmitting web pages."),
        ("HTTPS", "HyperText Transfer Protocol Secure", "A secure version of HTTP."),
        ("CPU", "Central Processing Unit", "The main processing unit of a computer."),
        ("RAM", "Random Access Memory", "Temporary memory used for processing tasks."),
        ("HTML", "HyperText Markup Language", "The standard language for creating web pages."),
        ("CSS", "Cascading Style Sheets", "A language for styling HTML content."),
        ("SQL", "Structured Query Language", "A language for managing databases."),
        ("IoT", "Internet of Things", "Devices connected via the internet for data exchange."),
        ("VPN", "Virtual Private Network", "A secure network connection over the internet."),
        ("LAN", "Local Area Network", "A network covering a small geographical area."),
        ("WAN", "Wide Area Network", "A network covering a large geographical area."),
        ("DNS", "Domain Name System", "Translates domain names to IP addresses."),
        ("IP", "Internet Protocol", "A set of rules for addressing and routing packets."),
        ("UX", "User Experience", "Designing products for a better user experience."),
        ("UI", "User Interface", "The graphical interface users interact with."),
        ("SEO", "Search Engine Optimization", "Improving website visibility in search engines."),
        ("SMTP", "Simple Mail Transfer Protocol", "A protocol for sending emails."),
        ("FTP", "File Transfer Protocol", "A protocol for transferring files over a network."),
        ("JSON", "JavaScript Object Notation", "A lightweight data-interchange format."),
        ("XML", "eXtensible Markup Language", "A markup language for storing structured data."),
        ("PDF", "Portable Document Format", "A file format for documents."),
        ("JPEG", "Joint Photographic Experts Group", "A common image format."),
        ("PNG", "Portable Network Graphics", "A lossless image format."),
        ("GIF", "Graphics Interchange Format", "A format for animated images."),
        ("MP3", "MPEG Audio Layer 3", "A popular audio format."),
        ("MP4", "MPEG-4 Video", "A multimedia format for videos."),
        ("CSV", "Comma-Separated Values", "A simple file format for tabular data."),
        ("RPA", "Robotic Process Automation", "Automating repetitive tasks using software."),
        ("BI", "Business Intelligence", "Data analysis to support business decisions."),
        ("ML", "Machine Learning", "A branch of AI that allows computers to learn from data."),
        ("DL", "Deep Learning", "A subset of ML using neural networks."),
        ("SaaS", "Software as a Service", "Cloud-based software delivery."),
        ("PaaS", "Platform as a Service", "Cloud-based platforms for development."),
        ("IaaS", "Infrastructure as a Service", "Cloud-based infrastructure services."),
        ("ERP", "Enterprise Resource Planning", "Integrated business management software."),
        ("CRM", "Customer Relationship Management", "Software for managing customer relationships."),
        ("SDK", "Software Development Kit", "A collection of tools for software development."),
        ("CI/CD", "Continuous Integration/Continuous Deployment", "Automating software development."),
        ("KPI", "Key Performance Indicator", "A metric for measuring success."),
        ("ROI", "Return on Investment", "A measure of profitability."),
        ("B2B", "Business to Business", "Transactions between businesses."),
        ("B2C", "Business to Consumer", "Transactions between businesses and consumers."),
        ("C2C", "Consumer to Consumer", "Transactions between consumers."),
        ("P2P", "Peer to Peer", "A decentralized network model."),
        ("TCP", "Transmission Control Protocol", "A core internet protocol."),
        ("UDP", "User Datagram Protocol", "A connectionless transport protocol."),
        ("SSH", "Secure Shell", "A protocol for secure remote login."),
        ("AWS", "Amazon Web Services", "A cloud computing service by Amazon."),
        ("GCP", "Google Cloud Platform", "A cloud computing service by Google."),
        ("Azure", "Microsoft Azure", "A cloud computing service by Microsoft."),
        ("Git", "Version Control System", "A system for tracking code changes."),
        ("CI", "Continuous Integration", "A software development practice."),
        ("CD", "Continuous Deployment", "Automatically deploying changes."),
        ("NoSQL", "Non-Relational Database", "A database model different from SQL."),
        ("ORM", "Object-Relational Mapping", "A technique for interacting with databases."),
        ("CLI", "Command Line Interface", "A text-based interface for interacting with software."),
        ("GUI", "Graphical User Interface", "A visual way of interacting with software."),
        ("IDE", "Integrated Development Environment", "A software development tool."),
        ("LDAP", "Lightweight Directory Access Protocol", "A protocol for accessing directory services."),
        ("OAuth", "Open Authorization", "A protocol for secure authentication."),
        ("JWT", "JSON Web Token", "A secure way to transmit information."),
        ("SSL", "Secure Sockets Layer", "A protocol for securing data transmission."),
        ("TLS", "Transport Layer Security", "A security protocol that replaces SSL."),
        ("NLP", "Natural Language Processing", "A field of AI that deals with human language."),
        ("TDD", "Test-Driven Development", "A software development approach."),
        ("DDD", "Domain-Driven Design", "A software design approach."),
        ("MVC", "Model View Controller", "A software architecture pattern."),
        ("SPA", "Single Page Application", "A web application that loads a single HTML page.")
    ]

    for abbr, full_form, desc in abbreviations:
        # Avoid duplicate entries by checking for an existing record
        if not Acronym.query.filter_by(abbreviation=abbr).first():
            new_acronym = Acronym(abbreviation=abbr, full_form=full_form, description=desc)
            db.session.add(new_acronym)
    db.session.commit()
    return "Database seeded successfully with 100 abbreviations!"

if __name__ == '__main__':
    app.run(debug=True)
