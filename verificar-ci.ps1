# verificar-ci.ps1 -- Simula el runner de GitHub Actions en un venv limpio.
#
# Por que existe este script y no una lista de comandos:
#   1. No depende de 'Activate.ps1', que la politica de ejecucion de Windows
#      bloquea por defecto. Llama a los ejecutables del venv por ruta directa.
#   2. Se ejecuta de una sola vez. Pegar 5 lineas en PowerShell es como se
#      pierde la mitad del bloque sin darse cuenta.
#   3. Si falla, dice QUE fallo y POR QUE, en vez de dejar un codigo de error.
#
# Uso:   powershell -ExecutionPolicy Bypass -File .\verificar-ci.ps1
#
# NOTA: un venv reusado no verifica una instalacion. Este script SIEMPRE
# borra y recrea .venv-limpio. Esa es toda la gracia.

$ErrorActionPreference = "Continue"
Set-Location -Path $PSScriptRoot

$fallos = New-Object System.Collections.ArrayList

function Paso([string]$titulo) {
    Write-Host ""
    Write-Host "=== $titulo ===" -ForegroundColor Cyan
}
function Ok([string]$m)    { Write-Host "  [OK] $m" -ForegroundColor Green }
function Mal([string]$m)   { Write-Host "  [X]  $m" -ForegroundColor Red; [void]$fallos.Add($m) }
function Abortar([string]$m) {
    Write-Host ""
    Write-Host "  [X] $m" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# ---------------------------------------------------------------- 1. Python
Paso "1. Buscando un interprete de Python 3.12+"

$pyExe = $null
$pyArgs = @()

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3.12 -c "pass" 2>$null
    if ($LASTEXITCODE -eq 0) { $pyExe = "py"; $pyArgs = @("-3.12") }
    else {
        & py -3 -c "pass" 2>$null
        if ($LASTEXITCODE -eq 0) { $pyExe = "py"; $pyArgs = @("-3") }
    }
}
if (-not $pyExe -and (Get-Command python -ErrorAction SilentlyContinue)) {
    $pyExe = "python"; $pyArgs = @()
}
if (-not $pyExe) {
    Abortar @"
No encontre ni 'py' ni 'python' en el PATH de esta terminal.

Tu bitacora ya registra este mismo problema el 13-sep: el PATH que se pone con
'`$env:Path +=' NO sobrevive a un reinicio, porque solo vive en esa sesion.

Arreglo permanente (una sola vez, y reinicia la terminal despues):
  [Environment]::SetEnvironmentVariable(
      'Path',
      [Environment]::GetEnvironmentVariable('Path','User') + ';C:\ruta\a\Python312;C:\ruta\a\Python312\Scripts',
      'User')
"@
}

$version = & $pyExe @pyArgs -c "import sys; print('{}.{}'.format(*sys.version_info[:2]))"
Ok "$pyExe $pyArgs -> Python $version"

$partes = $version.Split(".")
if ([int]$partes[0] -lt 3 -or ([int]$partes[0] -eq 3 -and [int]$partes[1] -lt 12)) {
    Abortar "pyproject.toml exige Python >= 3.12 y el CI usa 3.12. Aqui hay $version."
}

# ------------------------------------------------------- 2. Venv desde cero
Paso "2. Creando .venv-limpio DESDE CERO"

if (Test-Path ".venv-limpio") {
    Remove-Item -Recurse -Force ".venv-limpio" -ErrorAction SilentlyContinue
}
if (Test-Path ".venv-limpio") {
    Abortar "No pude borrar .venv-limpio. Suele ser que tienes esa terminal con el venv activado, o VS Code con un interprete de ahi abierto. Cierralos y repite."
}

& $pyExe @pyArgs -m venv ".venv-limpio"

$vpy    = Join-Path $PWD ".venv-limpio\Scripts\python.exe"
$vbin   = Join-Path $PWD ".venv-limpio\Scripts"
if (-not (Test-Path $vpy)) {
    Abortar "El venv no se creo (no existe $vpy). Si el error menciona 'ensurepip', tu instalacion de Python viene sin el modulo venv completo."
}
Ok "venv creado"

# ------------------------------------- 3. LA COMPUERTA NUEVA: pip desde cero
Paso "3. pip install -r requirements-dev.txt  (esta es la compuerta nueva)"

& $vpy -m pip install --upgrade pip --quiet --disable-pip-version-check
& $vpy -m pip install -r requirements-dev.txt --disable-pip-version-check

if ($LASTEXITCODE -ne 0) {
    Abortar @"
El 'pip install' fallo. Esto es EXACTAMENTE lo que el CI habria hecho.

Si el mensaje dice 'ResolutionImpossible' y menciona pydantic, entonces
requirements.txt todavia tiene 'pydantic==2.11.9'. Debe decir 2.12.5, porque
google-genai 2.23.0 lo exige. Revisa el archivo.
"@
}
Ok "instalacion limpia sin conflictos de resolucion"

& $vpy -m pip show pydantic 2>$null | Select-String "^Version:" | ForEach-Object { Ok "pydantic $_" }

# ------------------------------------------------- 4. Las cuatro compuertas
Paso "4. Las cuatro compuertas, con los comandos exactos del workflow"

& "$vbin\ruff.exe" check .
if ($LASTEXITCODE -eq 0) { Ok "ruff check" } else { Mal "ruff check" }

& "$vbin\ruff.exe" format --check .
if ($LASTEXITCODE -eq 0) { Ok "ruff format --check" } else { Mal "ruff format --check" }

& "$vbin\mypy.exe"
if ($LASTEXITCODE -eq 0) { Ok "mypy" } else { Mal "mypy" }

& "$vbin\pytest.exe"
if ($LASTEXITCODE -eq 0) { Ok "pytest" } else { Mal "pytest" }

# ---------------------------- 5. Arranque sin clave: degradacion honesta
Paso "5. Arranque SIN GEMINI_API_KEY (una funcion opcional no es un requisito)"

$sonda = Join-Path $env:TEMP "brujula_sonda.py"
@'
import asyncio

from datetime import UTC, datetime
from fastapi.testclient import TestClient
from app.main import app
from app.composicion import servicio_conversacion
from app.config import Configuracion
from app.dominio.agenda import Agenda

c = TestClient(app)
assert c.get("/health").status_code == 200, "/health no respondio 200"
assert c.get("/api/agenda").status_code == 200, "/api/agenda no respondio 200"

# La clave se fuerza a vacia por constructor, no borrando variables de entorno:
# asi la prueba da el mismo resultado tengas o no GEMINI_API_KEY en tu .env.
svc = servicio_conversacion(Configuracion(gemini_api_key=""))
r = asyncio.run(svc.responder(
    "que tengo esta semana?",
    Agenda(pendientes=(), fuentes_consultadas=("calendario",), fuentes_fallidas=()),
    datetime.now(UTC),
))
assert r.degradada is True, "sin clave deberia degradar, no responder normal"
assert r.generada_por_ia is False, "sin clave no puede decir que la genero una IA"
print("  arranca, /health 200, /api/agenda 200, degrada con honestidad")
'@ | Set-Content -Path $sonda -Encoding ASCII

$pythonpathPrevio = $env:PYTHONPATH
$env:PYTHONPATH = $PWD.Path
& $vpy $sonda
$codigoSonda = $LASTEXITCODE
$env:PYTHONPATH = $pythonpathPrevio
Remove-Item -LiteralPath $sonda -Force -ErrorAction SilentlyContinue

if ($codigoSonda -eq 0) { Ok "degradacion honesta sin API key" } else { Mal "arranque/degradacion sin API key" }

# ---------------------------------------------------------------- Veredicto
Write-Host ""
if ($fallos.Count -eq 0) {
    Write-Host "================================================" -ForegroundColor Green
    Write-Host " TODO VERDE. El CI deberia pasar. Puedes commitear." -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    exit 0
} else {
    Write-Host "================================================" -ForegroundColor Red
    Write-Host " FALLARON $($fallos.Count):" -ForegroundColor Red
    $fallos | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
    Write-Host " NO commitees todavia. Sube la salida al chat." -ForegroundColor Red
    Write-Host "================================================" -ForegroundColor Red
    exit 1
}
