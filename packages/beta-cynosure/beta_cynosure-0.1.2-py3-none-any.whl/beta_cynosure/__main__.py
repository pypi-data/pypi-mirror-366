import argparse
from beta_cynosure.engine import run

def cli():
    parser = argparse.ArgumentParser(description="Extrai dados financeiros da CVM e gera CSVs (DFP, ITR, FRE)")
    parser.add_argument("period", help="Intervalo INICIO-FIM (ex: 2020-2024) ou apenas um ano (ex: 2024)")
    parser.add_argument("-p", "--prefix", nargs="+", help="Um ou mais prefixos de ticker (ex: -p PETR VALE)", default=[])

    args = parser.parse_args()

    try:
        if "-" in args.period:
            start_year, end_year = map(int, args.period.split("-"))
            if start_year > end_year:
                raise ValueError
            years = list(range(start_year, end_year + 1))
        else:
            year = int(args.period)
            years = [year]
    except Exception:
        print("Formato inválido. Use: b-cynosure 2023-2025 ou b-cynosure 2024 -p petr")
        return

    run(years, prefix=[p.lower() for p in args.prefix])


if __name__ == "__main__":
    cli()
