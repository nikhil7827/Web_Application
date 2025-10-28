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


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_expense(id):
    expense = Expense.query.get_or_404(id)
    if request.method == 'POST':
        expense.description = request.form['description']
        expense.amount = float(request.form['amount'])
        expense.category = request.form['category']
        db.session.commit()
        flash("Expense updated successfully!", "info")
        return redirect(url_for('index'))
    return render_template('update_expense.html', expense=expense)

@app.route('/delete/<int:id>')
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted successfully!", "danger")
    return redirect(url_for('index'))

@app.route('/summary')
def summary():
    current_year = datetime.now().year
    month = request.args.get('month')
    query = Expense.query
    if month:
        query = query.filter(db.extract('month', Expense.date) == int(month))
    expenses = query.all()
    total = sum(e.amount for e in expenses)
    categories = {}
    for e in expenses:
        categories[e.category] = categories.get(e.category, 0) + e.amount

    warning = None
    MONTHLY_BUDGET = 1000
    if total > MONTHLY_BUDGET:
        warning = f"⚠️ Budget exceeded by ${total - MONTHLY_BUDGET:.2f}"

    return render_template('summary.html', expenses=expenses, total=total, categories=categories, warning=warning)

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


from flask import Flask, render_template
...
@app.route('/')
def index():
    expenses = Expense.query.all()
    total = sum(e.amount for e in expenses)
    return render_template('index.html', expenses=expenses, total=total)
