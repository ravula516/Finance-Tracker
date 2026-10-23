import ollama
from fastapi import FastAPI,HTTPException,Query
from database import engine, SessionLocal, Base
from models import ExpenseDB, IncomeDB, BudgetDB
from schemas import expense
from sqlalchemy import func
from fastapi.middleware.cors import CORSMiddleware
app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
expenses=[]
@app.get("/")
def home():
    return {"message":"welcome to Finance Tracker!"}
@app.get("/expenses")
def show(skip: int = Query(default=0, ge=0), limit: int = Query(default=10, le=100)):
    db = SessionLocal()
    records = db.query(ExpenseDB).order_by(ExpenseDB.date.desc()).offset(skip).limit(limit).all()
    result = [
        {
            "id": item.id,
            "title": item.title,
            "amount": item.amount,
            "category": item.category,
            "date": item.date
        }
        for item in records
    ]
    db.close()
    return result
@app.post("/expense")
def add_expense(expense:expense):
    db = SessionLocal()
    new_expense = ExpenseDB(
        title=expense.title,
        amount=expense.amount,
        category=expense.category
    )

    db.add(new_expense)
    db.commit()
    db.close()
    return {"message":"expense added successfully"}
@app.delete("/expenses/delete/{index}")
def delete_expense(index:int):
    db = SessionLocal()
    item = db.query(ExpenseDB).filter(
        ExpenseDB.id == index
    ).first()
    if item is None:
        db.close()
        raise HTTPException(status_code=404,detail="Expense not found")
    db.delete(item)
    db.commit()
    db.close()
    return {"message": "Expense deleted successfully"}
@app.get("/expenses/category/{category}")
def list(category:str):
    db = SessionLocal()
    records = db.query(ExpenseDB).filter(
        ExpenseDB.category.ilike(category)
    ).all()
    result = [
        {
            "id": item.id,
            "title": item.title,
            "amount": item.amount,
            "category": item.category
        }
        for item in records
    ]
    db.close()
    return result
@app.get("/expenses/summary")
def summary():
    db = SessionLocal()
    records = db.query(ExpenseDB).all()

    total = sum(item.amount for item in records)
    count = len(records)

    db.close()

    return {
        "total_expenses": count,
        "total_spent": total
    }
@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, updated: expense):
    db = SessionLocal()
    item = db.query(ExpenseDB).filter(
        ExpenseDB.id == expense_id
    ).first()
    if item is None:
        db.close()
        raise HTTPException(status_code=404,detail="Expense not found")
    item.title = updated.title
    item.amount = updated.amount
    item.category = updated.category

    db.commit()
    db.close()

    return {"message": "Expense updated successfully"}
@app.post("/income")
def add_income(source: str, amount: float):
    db = SessionLocal()
    new_income = IncomeDB(
        source=source,
        amount=amount
    )
    db.add(new_income)
    db.commit()
    db.close()
    return {"message": "Income added successfully"}
@app.get("/income")
def show_income(skip: int = Query(default=0, ge=0), limit: int = Query(default=10, le=100)):
    db = SessionLocal()
    records = db.query(IncomeDB).order_by(IncomeDB.amount.desc()).offset(skip).limit(limit).all()
    result = [
        {
            "id": item.id,
            "source": item.source,
            "amount": item.amount
        }
        for item in records
    ]
    db.close()
    return result
@app.get("/income/summary")
def income_summary():
    db = SessionLocal()
    records = db.query(IncomeDB).all()

    total = sum(item.amount for item in records)

    db.close()

    return {"total_income": total}

@app.put("/income/{income_id}")
def update_income(income_id: int, source: str, amount: float):
    db = SessionLocal()

    item = db.query(IncomeDB).filter(
        IncomeDB.id == income_id
    ).first()

    if item is None:
        db.close()
        raise HTTPException(status_code=404, detail="Income not found")

    item.source = source
    item.amount = amount

    db.commit()
    db.close()

    return {"message": "Income updated successfully"}


@app.delete("/income/{income_id}")
def delete_income(income_id: int):
    db = SessionLocal()

    item = db.query(IncomeDB).filter(
        IncomeDB.id == income_id
    ).first()

    if item is None:
        db.close()
        raise HTTPException(status_code=404, detail="Income not found")

    db.delete(item)
    db.commit()
    db.close()

    return {"message": "Income deleted successfully"}
@app.get("/balance")
def get_balance():
    db = SessionLocal()

    incomes = db.query(IncomeDB).all()
    expenses = db.query(ExpenseDB).all()

    total_income = sum(item.amount for item in incomes)
    total_expenses = sum(item.amount for item in expenses)

    db.close()

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": total_income - total_expenses
    }
@app.post("/budgets")
def add_budget(category: str, limit_amount: float):
    db = SessionLocal()
    new_budget = BudgetDB(
        category=category,
        limit_amount=limit_amount
    )
    db.add(new_budget)
    db.commit()
    db.close()
    return {"message": "Budget added successfully"}
@app.get("/budgets")
def show_budgets(skip: int = Query(default=0, ge=0), limit: int = Query(default=10, le=100)):
    db = SessionLocal()
    records = db.query(BudgetDB).order_by(BudgetDB.category.asc()).offset(skip).limit(limit).all()
    result = [
        {
            "id": item.id,
            "category": item.category,
            "limit_amount": item.limit_amount
        }
        for item in records
    ]
    db.close()
    return result
@app.get("/budgets/status")
def budget_status():
    db = SessionLocal()
    budgets = db.query(BudgetDB).all()
    result = []
    for budget in budgets:
        records = db.query(ExpenseDB).filter(
            ExpenseDB.category.ilike(budget.category)
        ).all()
        spent = sum(item.amount for item in records)
        result.append({
            "category": budget.category,
            "budget_limit": budget.limit_amount,
            "spent": spent,
            "remaining": budget.limit_amount - spent
        })
    db.close()
    return result

@app.put("/budgets/{budget_id}")
def update_budget(budget_id: int, category: str, limit_amount: float):
    db = SessionLocal()

    item = db.query(BudgetDB).filter(
        BudgetDB.id == budget_id
    ).first()

    if item is None:
        db.close()
        raise HTTPException(status_code=404, detail="Budget not found")

    item.category = category
    item.limit_amount = limit_amount

    db.commit()
    db.close()

    return {"message": "Budget updated successfully"}


@app.delete("/budgets/{budget_id}")
def delete_budget(budget_id: int):
    db = SessionLocal()

    item = db.query(BudgetDB).filter(
        BudgetDB.id == budget_id
    ).first()

    if item is None:
        db.close()
        raise HTTPException(status_code=404, detail="Budget not found")

    db.delete(item)
    db.commit()
    db.close()

    return {"message": "Budget deleted successfully"}

@app.get("/expenses/month/{year}/{month}")
def monthly_expenses(year: int, month: int):
    if month < 1 or month > 12:
        return {"error": "Month must be between 1 and 12"}
    db = SessionLocal()
    records = db.query(ExpenseDB).filter(
        ExpenseDB.date.startswith(f"{year}-{month:02d}")
    ).all()
    result = [
        {
            "id": item.id,
            "title": item.title,
            "amount": item.amount,
            "category": item.category,
            "date": item.date
        }
        for item in records
    ]
    db.close()
    return result
@app.get("/expenses/monthly-summary/{year}/{month}")
def monthly_summary(year: int, month: int):
    if month < 1 or month > 12:
        return {"error": "Month must be between 1 and 12"}

    db = SessionLocal()
    records = db.query(ExpenseDB).filter(
        ExpenseDB.date.startswith(f"{year}-{month:02d}")
    ).all()

    total = sum(item.amount for item in records)
    db.close()

    return {
        "year": year,
        "month": month,
        "total_expenses": total
    }
@app.get("/expenses/search/{keyword}")
def search_expenses(keyword: str):
    db = SessionLocal()

    records = db.query(ExpenseDB).filter(
        ExpenseDB.title == keyword
    ).all()

    result = [
        {
            "id": item.id,
            "title": item.title,
            "amount": item.amount,
            "category": item.category,
            "date": item.date
        }
        for item in records
    ]

    db.close()
    return result
@app.get("/income/search/{source}")
def search_income(source: str):
    db = SessionLocal()

    records = db.query(IncomeDB).filter(
        IncomeDB.source == source
    ).all()

    result = [
        {
            "id": item.id,
            "source": item.source,
            "amount": item.amount
        }
        for item in records
    ]

    db.close()
    return result
@app.get("/budgets/search/{category}")
def search_budgets(category: str):
    db = SessionLocal()

    records = db.query(BudgetDB).filter(
        BudgetDB.category == category
    ).all()

    result = [
        {
            "id": item.id,
            "category": item.category,
            "limit_amount": item.limit_amount
        }
        for item in records
    ]

    db.close()
    return result
@app.get("/expenses/range")
def expenses_by_amount(min_amount: float, max_amount: float):
    db = SessionLocal()

    records = db.query(ExpenseDB).filter(
        ExpenseDB.amount >= min_amount,
        ExpenseDB.amount <= max_amount
    ).all()

    result = [
        {
            "id": item.id,
            "title": item.title,
            "amount": item.amount,
            "category": item.category,
            "date": item.date
        }
        for item in records
    ]

    db.close()
    return result
@app.get("/expenses/date/{expense_date}")
def expenses_by_date(expense_date: str):
    db = SessionLocal()

    records = db.query(ExpenseDB).filter(
        ExpenseDB.date == expense_date
    ).all()

    result = [
        {
            "id": item.id,
            "title": item.title,
            "amount": item.amount,
            "category": item.category,
            "date": item.date
        }
        for item in records
    ]

    db.close()
    return result
@app.get("/dashboard")
def dashboard():
    db = SessionLocal()

    total_income = db.query(IncomeDB).with_entities(
        func.sum(IncomeDB.amount)
    ).scalar() or 0

    total_expenses = db.query(ExpenseDB).with_entities(
        func.sum(ExpenseDB.amount)
    ).scalar() or 0

    expense_count = db.query(ExpenseDB).count()
    total_budget = db.query(BudgetDB).with_entities(
    func.sum(BudgetDB.limit_amount)).scalar() or 0
    income_count = db.query(IncomeDB).count()
    db.close()

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": total_income - total_expenses,
        "expense_count": expense_count,
        "total_budget": total_budget,
        "income_count": income_count,
    }
Base.metadata.create_all(bind=engine)
@app.get("/ai/financial-advice")
def financial_advice():
    db = SessionLocal()

    try:
        incomes = db.query(IncomeDB).all()
        expenses = db.query(ExpenseDB).all()
        budgets = db.query(BudgetDB).all()

        total_income = sum(item.amount for item in incomes)
        total_expenses = sum(item.amount for item in expenses)

        expense_breakdown = {}
        for item in expenses:
            category = item.category
            expense_breakdown[category] = (
                expense_breakdown.get(category, 0) + item.amount
            )

        budget_details = [
            {
                "category": budget.category,
                "limit": budget.limit_amount,
                "spent": expense_breakdown.get(budget.category, 0)
            }
            for budget in budgets
        ]

        financial_data = {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "balance": total_income - total_expenses,
            "expense_breakdown": expense_breakdown,
            "budgets": budget_details
        }

        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a personal financial advisor. Analyze the "
                        "provided financial data carefully. Explain the "
                        "highest spending categories, category-wise spending "
                        "percentages, budget overruns, and practical ways to "
                        "reduce expenses. Estimate possible savings where "
                        "the data supports it. Use clear headings, specific "
                        "amounts, and actionable recommendations. Do not "
                        "invent financial facts that are not in the data."
                    )
                },
                {
                    "role": "user",
                    "content": str(financial_data)
                }
            ]
        )

        return {
            "financial_data": financial_data,
            "ai_advice": response["message"]["content"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI financial analysis failed: {str(e)}"
        )

    finally:
        db.close()