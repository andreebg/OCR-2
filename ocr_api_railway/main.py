from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError
import pytesseract
import io
import re
import datetime

# Asegura la ruta explícita del binario de Tesseract en contenedor
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

app = FastAPI(title="OCR Invoice Extractor", version="1.0")

def extract_data(text: str) -> dict:
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    full_text = " ".join(lines)

    def find(pattern: str, default: str = "") -> str:
        match = re.search(pattern, full_text, re.IGNORECASE)
        return match.group(1).strip() if match else default

    ruc_cliente     = find(r"RUC(?: CLIENTE)?:?\s*(\d+)")
    cliente         = find(r"CLIENTE:?\s*(.*?)\s*(?:RUC|DIRECCIÓN|$)")
    beneficiario    = find(r"Beneficiario:?\s*(.*?)\s*(?:RUC|$)")
    ruc_beneficiario= find(r"RUC(?: BENEFICIARIO)?:?\s*(\d+)")
    nro_doc         = find(r"(?:N°|Nro|Número) de documento:?\s*([A-Z0-9-]+)")
    fecha           = find(r"(\d{2}/\d{2}/\d{4})")
    forma_pago      = find(r"(?:Forma de pago|Condición de pago):?\s*(\w+)")
    placa           = find(r"PLACA:?\s*(\w+)")
    concepto        = find(r"(DIESEL PREMIUM.*?|SONDEO.*?|PLÁSTICO.*?|MONTAJE.*?)\s")
    cantidad        = find(r"(\d{1,4}[.,]?\d{0,3})\s+(" + concepto + ")")
    precio_unit     = find(r"VALOR UNIT(?:ARIO)?[:\s]*(\d+[.,]\d+)")
    subtotal        = find(r"(?:SUBTOTAL|SUB TOTAL)[:\s]*(\d+[.,]\d+)")
    igv             = find(r"(?:IGV|IVA)[^\d]*(\d+[.,]\d+)")
    total           = find(r"TOTAL[:\s]*(\d+[.,]\d+]?)")

    # Formatea fecha
    try:
        dt = datetime.datetime.strptime(fecha, "%d/%m/%Y")
        fecha_fmt = dt.strftime("%Y-%m-%d")
    except Exception:
        fecha_fmt = fecha

    # Nombre sugerido para archivo
    nombre_archivo = f"FC-{cliente[:5].replace(' ', '').upper()}-{beneficiario[:10].replace(' ', '').upper()}-{fecha_fmt}.pdf"

    return {
        "cliente": cliente,
        "ruc_cliente": ruc_cliente,
        "beneficiario": beneficiario,
        "ruc_beneficiario": ruc_beneficiario,
        "nro_documento": nro_doc,
        "fecha": fecha_fmt,
        "forma_pago": forma_pago,
        "placa": placa,
        "item": concepto,
        "cantidad": cantidad,
        "precio_unitario": precio_unit,
        "subtotal": subtotal,
        "igv_iva": igv,
        "total": total,
        "nombre_archivo_sugerido": nombre_archivo
    }

@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith("image/"):
            return JSONResponse(status_code=400, content={"error": "El archivo debe ser una imagen válida."})

        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        text = pytesseract.image_to_string(image, lang='eng')  # Puedes cambiar a 'spa' si OCR en español
        data = extract_data(text)
        return JSONResponse(content=data)

    except UnidentifiedImageError:
        return JSONResponse(status_code=400, content={"error": "La imagen no es válida o no puede abrirse."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error interno: {str(e)}"})
