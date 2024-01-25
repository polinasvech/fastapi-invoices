from collections import namedtuple

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc
from sqlalchemy.engine import Engine
from sqlalchemy.orm import joinedload

from db import BaseService, get_engine
from models import Invoice as InvoiceModel


class InvoiceService(BaseService):
    async def list(
        self,
        ordering: str = None,
        total_sum_gte: float = None,
        total_sum_lte: float = None,
    ) -> list:
        """
        Возвращает список инвойсов со строками, удовлетворяющих условиям

        :param ordering: поле для сортировки (по убыванию)
        :param total_sum_gte: минимальная total сумма
        :param total_sum_lte: максимальная total сумма
        :return: список инвойсов
        """
        invoices = []
        Invoice = namedtuple("Invoice", ["title", "subtotal", "total", "lines"])
        InvoiceLine = namedtuple("InvoiceLine", ["title", "quantity", "price_per_one", "subtotal_line", "total_line"])

        with self.get_session() as session:
            with session.begin():
                query = session.query(InvoiceModel).options(joinedload(InvoiceModel.invoice_lines))

                # если нужно, добавляем сортировку
                if ordering == "id":
                    query = query.order_by(desc(InvoiceModel.id))
                elif ordering == "lines_count":
                    query = query.order_by(desc(InvoiceModel.total_lines))
                elif ordering == "total_sum":
                    query = query.order_by(desc(InvoiceModel.total_sum))

                # если нужно, фильтруем данные по total_sum
                if total_sum_gte:
                    query = query.filter(InvoiceModel.discount_sum >= total_sum_gte)
                if total_sum_lte:
                    query = query.filter(InvoiceModel.discount_sum <= total_sum_lte)

                invoice_info = query.all()

            for obj in invoice_info:
                # подготовка InvoiceLine
                inlines = []
                for line in obj.invoice_lines:
                    inline = InvoiceLine(
                        line.title,
                        line.quantity,
                        line.price_per_one,
                        line.quantity * line.price_per_one,
                        (line.quantity * line.price_per_one) * (1 - obj.discount / 100),
                    )
                    inlines.append(inline)

                # подготовка Invoice
                invoice = Invoice(
                    obj.title,
                    obj.total_sum,
                    obj.total_sum * (1 - obj.discount / 100),
                    [jsonable_encoder(line._asdict()) for line in inlines],
                )
                invoices.append(invoice)

            return [jsonable_encoder(invoice._asdict()) for invoice in invoices]


def get_invoice_service(
    db_connection: Engine = Depends(get_engine),
) -> InvoiceService:
    return InvoiceService(db_connection)
