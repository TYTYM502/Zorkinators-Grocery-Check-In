import json
import mimetypes
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

from DataCenter import Inventory


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATE_DIR = BASE_DIR / "templates"


class GroceryWebApp:
    def __init__(self):
        self.inventory = Inventory()
        self.session_items = []
        self.next_session_id = 1

    def _require_date(self, raw_value: str) -> datetime:
        return datetime.strptime(raw_value, "%Y-%m-%d")

    def snapshot(self, query: str = "", category: str = "", storage: str = "", status: str = "all") -> dict:
        stats = self.inventory.get_statistics()
        return {
            "stats": stats,
            "inventory_groups": self.inventory.get_inventory_groups(query, category, storage, status),
            "session_items": [self._serialize_session_item(item) for item in self.session_items],
            "categories": [self.inventory.serialize_category(cat) for cat in self.inventory.categories.values()],
            "category_names": self.inventory.get_category_names(),
            "storage_names": self.inventory.get_storage_names(),
            "records": self.inventory.get_all_records(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def scan_barcode(self, barcode: str) -> dict:
        barcode = barcode.strip()
        if not barcode:
            raise ValueError("Barcode is required.")

        template = self.inventory.get_item_template_by_barcode(barcode)
        if template:
            purchase_date = datetime.now()
            session_item = self._build_session_item(
                barcode=barcode,
                name=template.name,
                category=template.category,
                storage_location=template.storage_location,
                purchase_date=purchase_date,
                exp_date=self.inventory.get_recommended_exp_date(template.category, purchase_date),
            )
            self.session_items.append(session_item)
            return {
                "mode": "existing",
                "message": f"Added {template.name} to the current session draft.",
                "item": self._serialize_session_item(session_item),
            }

        return {
            "mode": "new",
            "message": "Barcode not found. Enter item details to save it.",
            "defaults": {
                "barcode": barcode,
                "purchase_date": datetime.now().strftime("%Y-%m-%d"),
                "exp_date": self.inventory.get_recommended_exp_date("", datetime.now()).strftime("%Y-%m-%d"),
            },
        }

    def create_item(self, payload: dict) -> dict:
        barcode = payload.get("barcode", "").strip()
        name = payload.get("name", "").strip()
        category = payload.get("category", "").strip()
        storage = payload.get("storage_location", "").strip()

        if not all([barcode, name, category, storage]):
            raise ValueError("Barcode, name, category, and storage location are required.")

        purchase_date = self._require_date(payload["purchase_date"])
        exp_date = self._require_date(payload["exp_date"])

        session_item = self._build_session_item(barcode, name, category, storage, purchase_date, exp_date)
        self.session_items.append(session_item)
        return {
            "message": f"Saved {name} to the current session draft.",
            "item": self._serialize_session_item(session_item),
        }

    def update_session_item(self, session_id: int, payload: dict) -> dict:
        item = next((existing for existing in self.session_items if existing["session_id"] == session_id), None)
        if item is None:
            raise KeyError(f"Session item {session_id} not found.")

        item["name"] = payload["name"].strip()
        item["category"] = payload["category"].strip()
        item["storage_location"] = payload["storage_location"].strip()
        item["exp_date"] = self._require_date(payload["exp_date"])
        item["purchase_date"] = self._require_date(payload["purchase_date"])
        return {
            "message": f"Updated {item['name']} in the session draft.",
            "item": self._serialize_session_item(item),
        }

    def approve_session(self) -> dict:
        count = len(self.session_items)
        for item in self.session_items:
            self.inventory.add_item(
                item["barcode"],
                item["name"],
                item["category"],
                item["storage_location"],
                item["exp_date"],
                item["purchase_date"],
            )
        self.session_items.clear()
        return {"message": f"Approved {count} item(s) and added them to inventory."}

    def update_inventory_item(self, item_id: int, payload: dict) -> dict:
        updated = self.inventory.update_item(
            item_id=item_id,
            name=payload["name"].strip(),
            category=payload["category"].strip(),
            storage_location=payload["storage_location"].strip(),
            exp_date=self._require_date(payload["exp_date"]),
            purchase_date=self._require_date(payload["purchase_date"]),
        )
        return {
            "message": f"Updated {updated.name}.",
            "item": self.inventory.serialize_item(updated),
        }

    def create_record(self, payload: dict) -> dict:
        if not all([
            payload.get("barcode", "").strip(),
            payload.get("name", "").strip(),
            payload.get("category", "").strip(),
            payload.get("storage_location", "").strip(),
        ]):
            raise ValueError("Barcode, name, category, and storage location are required.")
        record = self.inventory.create_record(
            barcode=payload["barcode"].strip(),
            name=payload["name"].strip(),
            category=payload["category"].strip(),
            storage_location=payload["storage_location"].strip(),
            exp_date=self._require_date(payload["exp_date"]),
            purchase_date=self._require_date(payload["purchase_date"]),
            archived=bool(payload.get("archived")),
        )
        return {
            "message": f"Saved record {record.item_id} for {record.name}.",
            "item": self.inventory.serialize_item(record),
        }

    def update_record(self, item_id: int, payload: dict) -> dict:
        updated = self.inventory.update_item(
            item_id=item_id,
            name=payload["name"].strip(),
            category=payload["category"].strip(),
            storage_location=payload["storage_location"].strip(),
            exp_date=self._require_date(payload["exp_date"]),
            purchase_date=self._require_date(payload["purchase_date"]),
            archived=bool(payload.get("archived")),
        )
        return {
            "message": f"Updated record {updated.item_id}.",
            "item": self.inventory.serialize_item(updated),
        }

    def archive_inventory_item(self, item_id: int) -> dict:
        self.inventory.archive_item(item_id)
        return {"message": "Archived the selected item."}

    def archive_inventory_group(self, barcode: str) -> dict:
        archived_count = self.inventory.archive_items_by_barcode(barcode.strip())
        if archived_count == 0:
            raise LookupError(f"Barcode {barcode} was not found in active inventory.")
        return {"message": f"Archived {archived_count} active item(s) for barcode {barcode}."}

    def checkout_barcode(self, barcode: str) -> dict:
        barcode = barcode.strip()
        if not barcode:
            raise ValueError("Barcode is required.")

        items = self.inventory.get_items_by_barcode(barcode)
        if not items:
            raise LookupError(f"Barcode {barcode} was not found.")

        items.sort(key=lambda existing: existing.purchase_date)
        removed = items[0]
        self.inventory.archive_item(removed.item_id)
        return {"message": f"Checked out 1x {removed.name}."}

    def save_category(self, payload: dict) -> dict:
        name = payload.get("name", "").strip()
        storage = payload.get("storage_location", "").strip()
        if not all([name, storage]):
            raise ValueError("Category name and storage location are required.")

        category = self.inventory.upsert_category(
            name=name,
            storage_location=storage,
            recommended_exp_days=int(payload["recommended_exp_days"]),
            warning_threshold_percent=int(payload["warning_threshold_percent"]),
        )
        return {
            "message": f"Saved category {category.name}.",
            "category": self.inventory.serialize_category(category),
        }

    def _build_session_item(
        self,
        barcode: str,
        name: str,
        category: str,
        storage_location: str,
        purchase_date: datetime,
        exp_date: datetime,
    ) -> dict:
        session_item = {
            "session_id": self.next_session_id,
            "barcode": barcode.strip(),
            "name": name.strip(),
            "category": category.strip(),
            "storage_location": storage_location.strip(),
            "purchase_date": purchase_date,
            "exp_date": exp_date,
        }
        self.next_session_id += 1
        return session_item

    def _serialize_session_item(self, item: dict) -> dict:
        inventory_item = SimpleNamespace(
            item_id=item["session_id"],
            barcode=item["barcode"],
            name=item["name"],
            category=item["category"],
            storage_location=item["storage_location"],
            purchase_date=item["purchase_date"],
            exp_date=item["exp_date"],
            archived=False,
        )
        return {
            "session_id": item["session_id"],
            "barcode": item["barcode"],
            "name": item["name"],
            "category": item["category"],
            "storage_location": item["storage_location"],
            "exp_date": item["exp_date"].strftime("%Y-%m-%d"),
            "purchase_date": item["purchase_date"].strftime("%Y-%m-%d"),
            "status": self.inventory.get_item_status(inventory_item),
            "archived": False,
        }


APP = GroceryWebApp()


class GroceryRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self._serve_file(TEMPLATE_DIR / "index.html", "text/html; charset=utf-8")
            return

        if parsed.path.startswith("/static/"):
            target = STATIC_DIR / parsed.path.removeprefix("/static/")
            self._serve_file(target)
            return

        if parsed.path == "/api/bootstrap":
            params = parse_qs(parsed.query)
            payload = APP.snapshot(
                query=params.get("query", [""])[0],
                category=params.get("category", [""])[0],
                storage=params.get("storage", [""])[0],
                status=params.get("status", ["all"])[0],
            )
            self._json(payload)
            return

        if parsed.path.startswith("/api/recommendation"):
            params = parse_qs(parsed.query)
            category = params.get("category", [""])[0]
            purchase_date = params.get("purchase_date", [""])[0] or datetime.now().strftime("%Y-%m-%d")
            recommended = APP.inventory.get_recommended_exp_date(
                category,
                datetime.strptime(purchase_date, "%Y-%m-%d"),
            )
            self._json({"exp_date": recommended.strftime("%Y-%m-%d")})
            return

        self._json({"error": "Not found."}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self):
        parsed = urlparse(self.path)
        body = self._read_json()

        try:
            if parsed.path == "/api/session/scan":
                self._json(APP.scan_barcode(body.get("barcode", "")))
                return

            if parsed.path == "/api/session/items":
                self._json(APP.create_item(body), status=HTTPStatus.CREATED)
                return

            if parsed.path == "/api/session/approve":
                self._json(APP.approve_session())
                return

            if parsed.path == "/api/checkout":
                self._json(APP.checkout_barcode(body.get("barcode", "")))
                return

            if parsed.path == "/api/categories":
                self._json(APP.save_category(body), status=HTTPStatus.CREATED)
                return

            if parsed.path == "/api/records":
                self._json(APP.create_record(body), status=HTTPStatus.CREATED)
                return

            if parsed.path == "/api/inventory/archive-group":
                self._json(APP.archive_inventory_group(body.get("barcode", "")))
                return
        except (ValueError, KeyError, LookupError) as exc:
            status = HTTPStatus.BAD_REQUEST if not isinstance(exc, LookupError) else HTTPStatus.NOT_FOUND
            self._json({"error": str(exc)}, status=status)
            return

        self._json({"error": "Not found."}, status=HTTPStatus.NOT_FOUND)

    def do_PUT(self):
        parsed = urlparse(self.path)
        body = self._read_json()
        parts = [part for part in parsed.path.split("/") if part]

        try:
            if len(parts) == 4 and parts[:3] == ["api", "session", "items"]:
                self._json(APP.update_session_item(int(parts[3]), body))
                return

            if len(parts) == 3 and parts[:2] == ["api", "items"]:
                self._json(APP.update_inventory_item(int(parts[2]), body))
                return

            if len(parts) == 3 and parts[:2] == ["api", "records"]:
                self._json(APP.update_record(int(parts[2]), body))
                return

            if len(parts) == 3 and parts[:2] == ["api", "categories"]:
                body["name"] = body.get("name") or parts[2]
                self._json(APP.save_category(body))
                return
        except (ValueError, KeyError, LookupError) as exc:
            status = HTTPStatus.BAD_REQUEST if not isinstance(exc, LookupError) else HTTPStatus.NOT_FOUND
            self._json({"error": str(exc)}, status=status)
            return

        self._json({"error": "Not found."}, status=HTTPStatus.NOT_FOUND)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        parts = [part for part in parsed.path.split("/") if part]

        try:
            if len(parts) == 3 and parts[:2] == ["api", "items"]:
                self._json(APP.archive_inventory_item(int(parts[2])))
                return
        except (ValueError, KeyError, LookupError) as exc:
            self._json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        self._json({"error": "Not found."}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format, *args):
        return

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_file(self, path: Path, content_type: str | None = None):
        if not path.exists() or not path.is_file():
            self._json({"error": "Not found."}, status=HTTPStatus.NOT_FOUND)
            return

        data = path.read_bytes()
        guessed_type = content_type or mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", guessed_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run():
    server = ThreadingHTTPServer(("127.0.0.1", 8000), GroceryRequestHandler)
    print("Serving Grocery Check-In at http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        APP.inventory.close()
        server.server_close()


if __name__ == "__main__":
    run()