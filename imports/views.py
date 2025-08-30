import csv, io, json
from datetime import datetime
from typing import List, Dict, Tuple

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .forms import UploadCSVForm
from players.models import Player

DATE_INPUTS = ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y")  # dozvoljeni formati

def parse_date(s: str):
    if not s:
        return None
    for fmt in DATE_INPUTS:
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Neispravan datum: {s!r}")

def validate_row(row: Dict[str, str]) -> Tuple[Dict, List[str]]:
    """Vrati (normalizirani_podaci, lista_grešaka)."""
    errors = []
    data = {
        "first_name": (row.get("first_name") or "").strip(),
        "last_name": (row.get("last_name") or "").strip(),
        "position": (row.get("position") or "").strip(),
        "dob": None,
    }
    # datum
    dob_raw = (row.get("dob") or "").strip()
    if dob_raw:
        try:
            data["dob"] = parse_date(dob_raw).isoformat()
        except ValueError as e:
            errors.append(str(e))

    if not data["first_name"]:
        errors.append("first_name je obvezno")
    if not data["last_name"]:
        errors.append("last_name je obvezno")

    return data, errors

def read_csv(file) -> Tuple[List[Dict], List[Dict]]:
    """
    Vrati (valjani_redovi, redovi_s_greškama).
    Svaki element: {"rownum": int, "data": {...}} ili {"rownum": int, "errors": [...]}
    """
    # dekodiraj u tekst
    text = io.TextIOWrapper(file, encoding="utf-8", errors="replace")
    reader = csv.DictReader(text)
    ok, bad = [], []
    required = {"first_name", "last_name", "dob", "position"}
    missing = required - set([h.strip() for h in reader.fieldnames or []])
    if missing:
        raise ValueError(f"Nedostaju kolone: {', '.join(sorted(missing))}")

    for i, row in enumerate(reader, start=2):  # pretpostavimo zaglavlje je red 1
        data, errors = validate_row(row)
        if errors:
            bad.append({"rownum": i, "errors": errors})
        else:
            ok.append({"rownum": i, "data": data})
    return ok, bad

@require_http_methods(["GET", "POST"])
def player_import_upload(request: HttpRequest) -> HttpResponse:
    """
    Korak 1: upload + dry-run.
    GET -> prikaži formu.
    POST -> parsiraj CSV, prikaži pregled (što će se upisati) + greške.
    """
    if request.method == "GET":
        form = UploadCSVForm()
        return render(request, "imports/players_upload.html", {"form": form})

    form = UploadCSVForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, "imports/players_upload.html", {"form": form})

    try:
        ok, bad = read_csv(request.FILES["file"])
    except Exception as e:
        messages.error(request, f"Greška pri čitanju CSV-a: {e}")
        return render(request, "imports/players_upload.html", {"form": form})

    # JSON payload za commit
    payload = json.dumps({"ok": ok}, ensure_ascii=False)

    return render(
        request,
        "imports/players_preview.html",
        {
            "ok": ok,
            "bad": bad,
            "form": UploadCSVForm(initial={"dry_run": False, "payload": payload}),
        },
    )

@require_http_methods(["POST"])
def player_import_commit(request: HttpRequest) -> HttpResponse:
    """
    Korak 2: commit – kreiraj Player zapise za sve valjane redove iz payload-a.
    """
    form = UploadCSVForm(request.POST)
    if not form.is_valid() or not form.cleaned_data.get("payload"):
        messages.error(request, "Nedostaje payload.")
        return redirect("imports:players_upload")

    data = json.loads(form.cleaned_data["payload"])
    ok_rows = data.get("ok", [])
    created = 0
    for item in ok_rows:
        rec = item["data"]
        # idempotencija: preskoči ako već postoji isti first/last/dob
        qs = Player.objects.filter(
            first_name=rec["first_name"],
            last_name=rec["last_name"],
        )
        if rec.get("dob"):
            qs = qs.filter(dob=rec["dob"])
        if qs.exists():
            continue
        Player.objects.create(
            first_name=rec["first_name"],
            last_name=rec["last_name"],
            dob=rec.get("dob") or None,
            position=rec.get("position") or "",
        )
        created += 1

    messages.success(request, f"Uvezeno zapisa: {created}")
    return redirect("players:list")
