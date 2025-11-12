from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
from flask import jsonify, request

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


@app.route('/add_expense', methods=['POST'])
def add_expense():
    description = request.form['description']
    amount = float(request.form['amount'])
    category = request.form['category']
    new_expense = Expense(description=description, amount=amount, category=category, date=datetime.utcnow())
    db.session.add(new_expense)
    db.session.commit()
    flash('Expense added successfully!', 'success')
    return redirect(url_for('index'))

from datetime import datetime


@app.route('/update_expense/<int:id>', methods=['POST'])
def update_expense(id):
    expense = Expense.query.get_or_404(id)
    expense.description = request.form['description']
    expense.amount = float(request.form['amount'])
    expense.category = request.form['category']
    db.session.commit()

    return jsonify({
        'success': True,
        'id': expense.id,
        'description': expense.description,
        'amount': f"{expense.amount:.2f}",
        'category': expense.category
    })

@app.route('/delete_expense/<int:id>', methods=['DELETE'])
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return jsonify({'success': True, 'id': id})

from datetime import datetime

@app.route('/summary')
def summary():
    # Fetch all expenses from the database
    expenses = Expense.query.order_by(Expense.date.desc()).all()

    # Calculate totals
    total_income = sum(e.amount for e in expenses if e.category.lower() == 'income')
    total_expenses = sum(e.amount for e in expenses if e.category.lower() != 'income')
    balance = total_income - total_expenses

    # Group expenses by category (excluding income)
    categories = {}
    for e in expenses:
        if e.category.lower() != 'income':
            categories[e.category] = categories.get(e.category, 0) + e.amount

    # Prepare chart data
    chart_labels = list(categories.keys())
    chart_values = list(categories.values())

    return render_template(
        'summary.html',
        expenses=expenses,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        categories=categories,
        chart_labels=chart_labels,
        chart_values=chart_values
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
    expenses = Expense.query.order_by(Expense.date.desc()).all()

    total_income = sum(e.amount for e in expenses if e.category.lower() == 'income')
    total_expenses = sum(e.amount for e in expenses if e.category.lower() != 'income')
    balance = total_income - total_expenses

    # Expense breakdown by category
    categories = {}
    for e in expenses:
        if e.category.lower() != 'income':
            categories[e.category] = categories.get(e.category, 0) + e.amount

    return render_template(
        'index.html',
        expenses=expenses,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        categories=categories,
        chart_labels=list(categories.keys()),
        chart_values=list(categories.values())
    )

@app.route('/add_income', methods=['POST'])
def add_income():
    description = request.form['description']
    amount = float(request.form['amount'])
    new_income = Expense(description=description, amount=amount, category='Income', date=datetime.utcnow())
    db.session.add(new_income)
    db.session.commit()
    flash('Income added successfully!', 'success')
    return redirect(url_for('index'))

