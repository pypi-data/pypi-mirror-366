"""
# tools for getting TLS certs

## usage:

```py
from a5.web import tls
bundle = tls.new_cert_bundle(domain, email, hosted_zone_id, staging=True)
with open("tls.json", "w") as f:
    f.write(tls.serialize_bundle(bundle))
```

```py
from a5.web import tls
with open("tls.json") as f:
    bundle = tls.deserialize_bundle(f.read())
nbundle = tls.renew_cert_bundle(bundle)
```
"""

import json
import logging
from pathlib import Path

import pico_acme
from pico_acme import route53

logger = logging.getLogger(__name__)


def new_cert_bundle(domain, account_email, route53_hosted_zone_id, staging=False):
    logger.info(f"Registering account")
    acme_client = pico_acme.register_account(account_email, agree_tos=True, staging=staging)
    logger.info(f"Creating key and CSR")
    key_pem_bin = pico_acme.make_key()
    csr_pem = pico_acme.make_csr(key_pem_bin, [domain])
    upsert, clean = route53.route53_upsert_cleanup(route53_hosted_zone_id)
    logger.info(f"Performing DNS01 challenge")
    fullchain_pem = pico_acme.perform_dns01(acme_client, domain, csr_pem, upsert, clean)
    logger.info(f"Success")
    return (
        domain,
        route53_hosted_zone_id,
        pico_acme.serialize_account(acme_client),
        key_pem_bin.decode("ascii"),
        fullchain_pem,
        staging,
    )


def renew_cert_bundle(bundle):
    domain, route53_hosted_zone_id, account_ser, key_pem, fullchain_pem, staging = bundle
    logger.info(f"Loading account")
    acme_client = pico_acme.deserialize_account(account_ser, staging=staging)
    logger.info(f"Loading key and creating CSR")
    csr_pem = pico_acme.make_csr(key_pem.encode("ascii"), [domain])
    upsert, clean = route53.route53_upsert_cleanup(route53_hosted_zone_id)
    logger.info(f"Performing DNS01 challenge for renewal")
    fullchain_pem = pico_acme.perform_dns01(acme_client, domain, csr_pem, upsert, clean)
    logger.info(f"Success")
    return (
        domain,
        route53_hosted_zone_id,
        pico_acme.serialize_account(acme_client),
        key_pem,
        fullchain_pem,
        staging,
    )


def maybe_renew_bundle(bundle):
    domain, route53_hosted_zone_id, account_ser, key_pem, fullchain_pem, staging = bundle
    if pico_acme.should_renew(fullchain_pem):
        bundle = renew_cert_bundle(bundle)
    return bundle


def serialize_bundle(bundle):
    return json.dumps(bundle)


def deserialize_bundle(data):
    return json.loads(data)


def get_key_and_cert(bundle):
    domain, route53_hosted_zone_id, account_ser, key_pem, fullchain_pem, staging = bundle
    return key_pem, fullchain_pem


def setup_tls_certs(storage_folder, domain, account_email, route53_hosted_zone_id, staging=False):
    """
    Sets up TLS. Gets new certs/renews as required. Returns paths to key and cert
    """
    storage = Path(storage_folder)
    storage.mkdir(parents=True, exist_ok=True)
    bundle_path = storage / "bundle.json"
    key_path = storage / "key.pem"
    fullchain_path = storage / "cert.pem"
    if bundle_path.exists() and key_path.exists() and fullchain_path.exists():
        # everything exists, just check if we need to renew
        bundle = deserialize_bundle(bundle_path.read_text())
        bundle = maybe_renew_bundle(bundle)
    else:
        bundle = new_cert_bundle(domain, account_email, route53_hosted_zone_id, staging=staging)
    bundle_path.write_text(serialize_bundle(bundle))
    key, chain = get_key_and_cert(bundle)
    key_path.write_text(key)
    fullchain_path.write_text(chain)
    return key_path, fullchain_path
