import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, RedirectResponse

from services import InvoiceService, get_invoice_service

app = FastAPI()

possible_ordering = ["id", "lines_count", "total_sum"]


@app.get("/")
async def root():
    return RedirectResponse("/invoices")


@app.get("/invoices")
async def list_invoices(
    invoice_service: InvoiceService = Depends(get_invoice_service),
    page: int = Query(ge=1, default=1),
    order: str = Query(default=None),
    total_sum_gte: float = Query(ge=0, default=None),
    total_sum_lte: float = Query(ge=0, default=None),
):
    if order and order not in possible_ordering:
        raise HTTPException(status_code=400, detail=f"order must take one of the values {possible_ordering}")

    invoice_list = await invoice_service.list(ordering=order, total_sum_gte=total_sum_gte, total_sum_lte=total_sum_lte)

    if not invoice_list:
        return JSONResponse(content="No invoices matching your request could be found :(")

    page_size = 100
    offset_min = (page - 1) * page_size
    offset_max = page * page_size
    invoice_list = invoice_list[offset_min:offset_max]

    result = {
        "invoices": invoice_list,
        "invoices_count": len(invoice_list),
        "invoices_total": float(sum([invoice["total"] for invoice in invoice_list])),
    }
    return JSONResponse(content=result)
