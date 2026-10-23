from sqlalchemy import Column, Integer, String, Float
from datetime import datetime
from database import Base
class ExpenseDB(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    amount = Column(Float)
    category = Column(String)
    date = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d"))
class IncomeDB(Base):
    __tablename__ = "income"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String)
    amount = Column(Float)
class BudgetDB(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    limit_amount = Column(Float)