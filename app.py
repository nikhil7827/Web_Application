from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/expensesdb'
app.config['SECRET_KEY'] = 'secret123'
db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()


@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        desc = request.form['description']
        amount = float(request.form['amount'])
        category = request.form['category']
        new_expense = Expense(description=desc, amount=amount, category=category)
        db.session.add(new_expense)
        db.session.commit()
        flash("Expense added successfully!", "success")
        return redirect(url_for('index'))
    return render_template('add_expense.html')


from datetime import datetime

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_expense(id):
    expense = Expense.query.get_or_404(id)
    if request.method == 'POST':
        expense.description = request.form['description']
        expense.amount = float(request.form['amount'])
        expense.category = request.form['category']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update_expense.html', expense=expense, datetime=datetime)


@app.route('/delete/<int:id>')
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted successfully!", "danger")
    return redirect(url_for('index'))

from datetime import datetime

@app.route('/summary')
def summary():
    month = request.args.get('month')
    query = Expense.query

    if month and month != "":
        query = query.filter(db.extract('month', Expense.date) == int(month))

    expenses = query.order_by(Expense.date.desc()).all()
    total = sum(e.amount for e in expenses)

    warning = None
    MONTHLY_BUDGET = 1000
    if total > MONTHLY_BUDGET:
        warning = f"Budget exceeded by ${total - MONTHLY_BUDGET:.2f}"

    months = [
        ("1", "January"), ("2", "February"), ("3", "March"), ("4", "April"),
        ("5", "May"), ("6", "June"), ("7", "July"), ("8", "August"),
        ("9", "September"), ("10", "October"), ("11", "November"), ("12", "December")
    ]

    return render_template(
        'summary.html',
        expenses=expenses,
        total=total,
        warning=warning,
        months=months,
        selected_month=month,
        datetime=datetime
    )
@app.route('/export')
def export_csv():
    expenses = Expense.query.all()
    data = [{
        "Date": e.date.strftime("%Y-%m-%d"),
        "Description": e.description,
        "Category": e.category,
        "Amount": e.amount
    } for e in expenses]
    df = pd.DataFrame(data)
    df.to_csv('expenses.csv', index=False)
    return send_file('expenses.csv', as_attachment=True)


from datetime import datetime

@app.route('/')
def index():
    expenses = Expense.query.all()
    total = sum(e.amount for e in expenses)
    return render_template('index.html', expenses=expenses, total=total, datetime=datetime)

