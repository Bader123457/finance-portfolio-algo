from __future__ import annotations
import argparse
from prism_client import (
    get_my_current_information,
    get_context,
    context_to_tuple,
    send_portfolio,
)
from portfolio import months_between, choose_allocation, allocate_positions

def main():
    parser = argparse.ArgumentParser(description="PRISM Portfolio Builder")
    parser.add_argument("--dry-run", action="store_true", help="Do not submit, just print")
    args = parser.parse_args()

    ok, info = get_my_current_information()
    if not ok:
        print("Error (info):", info)
    else:
        print("Team information:", info)

    ok, ctxt = get_context()
    if not ok:
        print("Error (context):", ctxt)
        return

    print("Context provided:", ctxt)
    parsed = context_to_tuple(ctxt)

    horizon = months_between(parsed.start_date, parsed.end_date)
    recipe = choose_allocation(parsed.budget, horizon, parsed.age)
    positions = allocate_positions(recipe["budget"], recipe["weights"], recipe["buckets"])

    print("Proposed positions:", positions)

    if args.dry_run:
        print("DRY RUN: not submitting.")
        return

    ok, resp = send_portfolio(positions)
    if not ok:
        print("Error (submit):", resp)
    else:
        print("Evaluation response:", resp)

if __name__ == "__main__":
    main()
