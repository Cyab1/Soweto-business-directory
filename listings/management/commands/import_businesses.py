import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from listings.models import Business, Category

REQUIRED = {"external_id", "name", "category", "address"}


def to_float(value):
    try:
        return float(value) if value and value.strip() else None
    except ValueError:
        return None


class Command(BaseCommand):
    help = "Import businesses from a CSV as unclaimed listings."

    def add_arguments(self, parser):
        parser.add_argument("csv_path")
        parser.add_argument("--source", default="digismart_import")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **opts):
        source = opts["source"]
        created = updated = skipped = no_coords = 0

        try:
            f = open(opts["csv_path"], newline="", encoding="utf-8-sig")
        except OSError as e:
            raise CommandError(str(e))

        with f, transaction.atomic():
            reader = csv.DictReader(f)
            missing = REQUIRED - set(reader.fieldnames or [])
            if missing:
                raise CommandError(f"CSV is missing columns: {', '.join(sorted(missing))}")

            for line, row in enumerate(reader, start=2):
                get = lambda k: (row.get(k) or "").strip()
                ext_id, name = get("external_id"), get("name")
                if not ext_id or not name or not get("category"):
                    self.stderr.write(f"Line {line}: skipped (missing id, name or category)")
                    skipped += 1
                    continue

                category, _ = Category.objects.get_or_create(name=get("category"))
                lat, lng = to_float(get("latitude")), to_float(get("longitude"))
                if lat is None or lng is None:
                    lat = lng = None
                    no_coords += 1

                fields = {
                    "name": name,
                    "category": category,
                    "address": get("address"),
                    "contact_info": get("contact_info"),
                    "services": get("services"),
                    "whatsapp": get("whatsapp"),
                    "website_url": get("website_url"),
                    "instagram": get("instagram"),
                    "facebook": get("facebook"),
                    "price_range": get("price_range"),
                    "latitude": lat,
                    "longitude": lng,
                }

                existing = Business.objects.filter(source=source, external_id=ext_id).first()
                if existing is None:
                    Business.objects.create(
                        source=source, external_id=ext_id,
                        status=Business.Status.UNCLAIMED, owner=None, **fields,
                    )
                    created += 1
                elif existing.status == Business.Status.UNCLAIMED:
                    for k, v in fields.items():
                        setattr(existing, k, v)
                    existing.save()
                    updated += 1
                else:
                    skipped += 1  # claimed by an owner: never overwrite their edits

            if opts["dry_run"]:
                transaction.set_rollback(True)

        prefix = "[DRY RUN] " if opts["dry_run"] else ""
        self.stdout.write(self.style.SUCCESS(
            f"{prefix}created={created} updated={updated} skipped={skipped} "
            f"without_coordinates={no_coords}"
        ))