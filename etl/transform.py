"""Limpa os dados brutos e roda checagens de qualidade."""
import pandas as pd

RAW_DIR = "data/raw"
CLEAN_DIR = "data/clean"


def _quality_report(df: pd.DataFrame, nome: str, issues: list[str]) -> None:
    print(f"\n[data_quality] {nome}: {len(df)} linhas")
    for issue in issues:
        print(f"  - {issue}")


def limpar_vendas() -> pd.DataFrame:
    df = pd.read_csv(f"{RAW_DIR}/vendas.csv", parse_dates=["data"])
    issues = []

    n_antes = len(df)
    df = df.drop_duplicates()
    if len(df) != n_antes:
        issues.append(f"{n_antes - len(df)} duplicatas removidas")

    n_negativos = (df["receita"] < 0).sum()
    if n_negativos:
        issues.append(f"{n_negativos} linhas com receita negativa removidas")
        df = df[df["receita"] >= 0]

    n_nulos = df.isnull().any(axis=1).sum()
    if n_nulos:
        issues.append(f"{n_nulos} linhas com valores nulos removidas")
        df = df.dropna()

    _quality_report(df, "vendas", issues or ["nenhum problema encontrado"])
    return df


def limpar_despesas() -> pd.DataFrame:
    df = pd.read_csv(f"{RAW_DIR}/despesas.csv", parse_dates=["data"])
    issues = []

    n_negativos = (df["valor"] < 0).sum()
    if n_negativos:
        issues.append(f"{n_negativos} linhas com valor negativo removidas")
        df = df[df["valor"] >= 0]

    _quality_report(df, "despesas", issues or ["nenhum problema encontrado"])
    return df


def limpar_calendario() -> pd.DataFrame:
    df = pd.read_csv(f"{RAW_DIR}/calendario.csv", parse_dates=["data"])
    _quality_report(df, "calendario", ["nenhum problema encontrado"])
    return df


def main():
    import os

    os.makedirs(CLEAN_DIR, exist_ok=True)
    limpar_calendario().to_csv(f"{CLEAN_DIR}/calendario.csv", index=False)
    limpar_vendas().to_csv(f"{CLEAN_DIR}/vendas.csv", index=False)
    limpar_despesas().to_csv(f"{CLEAN_DIR}/despesas.csv", index=False)
    print(f"\nDados limpos salvos em {CLEAN_DIR}/")


if __name__ == "__main__":
    main()
