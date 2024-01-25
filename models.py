from sqlalchemy import Column, ForeignKey, Integer, String, func, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.types import DECIMAL as Decimal

Base = declarative_base()


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    quantity = Column(Integer)
    price_per_one = Column(Decimal)

    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    invoice = relationship("Invoice", back_populates="invoice_lines")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    discount = Column(Decimal)

    invoice_lines = relationship("InvoiceLine", back_populates="invoice")

    total_lines = column_property(select(func.count(InvoiceLine.id)).where(InvoiceLine.invoice_id == id).label("total_lines"))

    total_sum = column_property(
        select(func.sum(InvoiceLine.quantity * InvoiceLine.price_per_one))
        .where(InvoiceLine.invoice_id == id)
        .label("total_sum")
    )

    discount_sum = column_property(
        select(func.sum(InvoiceLine.quantity * InvoiceLine.price_per_one) * (1 - discount / 100))
        .where(InvoiceLine.invoice_id == id)
        .label("discount_sum")
    )
