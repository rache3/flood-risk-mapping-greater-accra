"""
upload_r2.py — Upload Pipeline Outputs to Cloudflare R2
=========================================================
Replaces upload_gcs.py. R2 is S3-compatible, so this uses boto3
with a custom endpoint rather than the Google Cloud Storage SDK.

Uploads:
    output/flood_risk_map.cog.tif  → rasters/flood_risk_map.cog.tif
    output/flood_risk_map.tif      → rasters/flood_risk_map.tif
    docs/gadm41_GHA_accra.json     → vectors/gadm41_GHA_accra.json

Requires in .env:
    R2_ACCOUNT_ID
    R2_ACCESS_KEY_ID
    R2_SECRET_ACCESS_KEY
    R2_BUCKET
    R2_ENDPOINT

Usage:
    python scripts/upload_r2.py
"""

import os
import logging

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
R2_ACCESS_KEY_ID     = os.getenv("R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY", "")
R2_BUCKET            = os.getenv("R2_BUCKET", "accra-flood-risk")
R2_ENDPOINT          = os.getenv("R2_ENDPOINT", "")
R2_PUBLIC_URL         = os.getenv("R2_PUBLIC_URL", "")

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
DOCS_DIR   = os.getenv("DOCS_DIR", "docs")

UPLOADS = [
    (os.path.join(OUTPUT_DIR, "flood_risk_map.cog.tif"), "rasters/flood_risk_map.cog.tif"),
    (os.path.join(OUTPUT_DIR, "flood_risk_map.tif"),      "rasters/flood_risk_map.tif"),
    (os.path.join(DOCS_DIR,   "gadm41_GHA_accra.json"),   "vectors/gadm41_GHA_accra.json"),
]


def get_client():
    """Create a boto3 S3 client configured for Cloudflare R2."""
    import boto3
    from botocore.config import Config

    if not R2_ACCESS_KEY_ID or not R2_SECRET_ACCESS_KEY:
        log.error("R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY not set in .env")
        raise SystemExit(1)

    if not R2_ENDPOINT:
        log.error("R2_ENDPOINT not set in .env")
        raise SystemExit(1)

    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def upload_file(client, local_path: str, remote_key: str) -> bool:
    """Upload a single file to R2. Returns True on success."""
    if not os.path.exists(local_path):
        log.warning("File not found, skipping: %s", local_path)
        return False

    size_mb = os.path.getsize(local_path) / 1024 / 1024
    log.info("Uploading %s (%.1f MB) → r2://%s/%s", local_path, size_mb, R2_BUCKET, remote_key)

    content_type = "application/json" if remote_key.endswith(".json") else "image/tiff"

    try:
        client.upload_file(
            local_path,
            R2_BUCKET,
            remote_key,
            ExtraArgs={"ContentType": content_type},
        )
        log.info("Upload complete ✓  %s", remote_key)
        return True
    except Exception as e:
        log.error("Upload failed for %s: %s", remote_key, e)
        return False


def main():
    log.info("=== R2 Upload Pipeline ===")
    log.info("Bucket: %s", R2_BUCKET)
    log.info("Endpoint: %s", R2_ENDPOINT)

    client = get_client()

    results = []
    for local_path, remote_key in UPLOADS:
        ok = upload_file(client, local_path, remote_key)
        results.append((remote_key, ok))

    log.info("")
    log.info("═" * 55)
    log.info("  UPLOAD SUMMARY")
    log.info("═" * 55)
    for key, ok in results:
        symbol = "✓" if ok else "✗"
        log.info("  %s  %s", symbol, key)
    log.info("═" * 55)

    if all(ok for _, ok in results):
        log.info("All uploads complete ✓")
    else:
        log.warning("Some uploads failed — check logs above")

    if R2_PUBLIC_URL:
        log.info("")
        log.info("Public COG URL     : %s/rasters/flood_risk_map.cog.tif", R2_PUBLIC_URL)
        log.info("Public GeoJSON URL : %s/vectors/gadm41_GHA_accra.json", R2_PUBLIC_URL)

    log.info("Live map : https://floodwatch.geobuildersafrica.com")


if __name__ == "__main__":
    main()