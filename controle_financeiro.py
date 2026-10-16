import json
from pathlib import Path
from datetime import date
from decimal import Decimal, InvalidOperation


ARQUIVO = Path(__file__).with_name("dados.json")


def carregar_dados():
    """Carrega as movimentacoes financeiras do arquivo JSON."""
    if not ARQUIVO.exists():
        return []

    try:
        with ARQUIVO.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        if not isinstance(dados, list):
            raise ValueError("O arquivo deve conter uma lista.")

        for item in dados:
            if not isinstance(item, dict):
                raise ValueError("Movimentacao invalida.")

            if item.get("tipo") not in ("receita", "despesa"):
                raise ValueError("Tipo de movimentacao invalido.")

            if not isinstance(item.get("descricao"), str):
                raise ValueError("Descricao invalida.")

            if not item["descricao"].strip():
                raise ValueError("Descricao vazia.")

            if not isinstance(item.get("categoria"), str):
                raise ValueError("Categoria invalida.")

            if not item["categoria"].strip():
                raise ValueError("Categoria vazia.")

            valor = Decimal(item["valor"])

            if not valor.is_finite() or valor <= 0:
                raise ValueError("Valor financeiro invalido.")

            date.fromisoformat(item["data"])

        return dados

    except (
        OSError,
        json.JSONDecodeError,
        ValueError,
        TypeError,
        KeyError,
        InvalidOperation
    ) as erro:
        raise RuntimeError(
            f"Nao foi possivel carregar os dados: {erro}"
        ) from erro


def salvar_dados(movimentacoes):
    """Salva as movimentacoes no arquivo JSON."""
    temporario = ARQUIVO.with_name("dados.tmp")

    try:
        with temporario.open("w", encoding="utf-8") as arquivo:
            json.dump(
                movimentacoes,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

        temporario.replace(ARQUIVO)
        return True

    except OSError as erro:
        print(f"Erro ao salvar os dados: {erro}")

        try:
            temporario.unlink(missing_ok=True)
        except OSError:
            pass

        return False


def formatar_moeda(valor):
    """Formata um valor no padrao monetario brasileiro."""
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X")
    texto = texto.replace(".", ",")
    texto = texto.replace("X", ".")

    return f"R$ {texto}"


def ler_valor():
    """Solicita um valor monetario positivo."""
    while True:
        entrada = input("Valor (ex.: 150,50): ").strip()
        entrada = entrada.replace(",", ".")

        try:
            valor = Decimal(entrada)

            if not valor.is_finite() or valor <= 0:
                print("Digite um valor maior que zero.")
                continue

            if valor.as_tuple().exponent < -2:
                print("Digite no maximo duas casas decimais.")
                continue

            return valor.quantize(Decimal("0.01"))

        except InvalidOperation:
            print("Valor invalido. Tente novamente.")


def cadastrar_movimentacao(movimentacoes, tipo):
    """Cadastra uma receita ou despesa."""
    print(f"\n--- Cadastrar {tipo.capitalize()} ---")

    descricao = input("Descricao: ").strip()

    if not descricao:
        print("A descricao nao pode ficar vazia.")
        return

    categoria = input("Categoria: ").strip()

    if not categoria:
        print("A categoria nao pode ficar vazia.")
        return

    valor = ler_valor()

    movimentacao = {
        "tipo": tipo,
        "descricao": descricao,
        "categoria": categoria,
        "valor": str(valor),
        "data": date.today().isoformat()
    }

    movimentacoes.append(movimentacao)

    if salvar_dados(movimentacoes):
        print(f"{tipo.capitalize()} cadastrada com sucesso!")
    else:
        movimentacoes.pop()
        print("Nao foi possivel cadastrar a movimentacao.")


def listar_movimentacoes(movimentacoes):
    """Exibe todas as movimentacoes registradas."""
    print("\n--- Movimentacoes Financeiras ---")

    if not movimentacoes:
        print("Nenhuma movimentacao cadastrada.")
        return

    for indice, item in enumerate(movimentacoes, start=1):
        valor = Decimal(item["valor"])
        data_formatada = date.fromisoformat(
            item["data"]
        ).strftime("%d/%m/%Y")

        print(f"\n{indice}. {item['descricao']}")
        print(f"   Tipo: {item['tipo'].capitalize()}")
        print(f"   Categoria: {item['categoria']}")
        print(f"   Valor: {formatar_moeda(valor)}")
        print(f"   Data: {data_formatada}")


def calcular_totais(movimentacoes):
    """Calcula os totais de receitas e despesas."""
    receitas = sum(
        (
            Decimal(item["valor"])
            for item in movimentacoes
            if item["tipo"] == "receita"
        ),
        Decimal("0.00")
    )

    despesas = sum(
        (
            Decimal(item["valor"])
            for item in movimentacoes
            if item["tipo"] == "despesa"
        ),
        Decimal("0.00")
    )

    return receitas, despesas


def consultar_saldo(movimentacoes):
    """Apresenta o saldo financeiro atual."""
    receitas, despesas = calcular_totais(movimentacoes)
    saldo = receitas - despesas

    print("\n--- Saldo Financeiro ---")
    print(f"Total de receitas: {formatar_moeda(receitas)}")
    print(f"Total de despesas: {formatar_moeda(despesas)}")
    print(f"Saldo atual:       {formatar_moeda(saldo)}")


def gerar_relatorio(movimentacoes):
    """Gera um resumo financeiro e agrupa despesas por categoria."""
    receitas, despesas = calcular_totais(movimentacoes)

    print("\n--- Relatorio Financeiro ---")
    print(f"Receitas: {formatar_moeda(receitas)}")
    print(f"Despesas: {formatar_moeda(despesas)}")
    print(f"Saldo:    {formatar_moeda(receitas - despesas)}")

    categorias = {}

    for item in movimentacoes:
        if item["tipo"] == "despesa":
            categoria = item["categoria"]
            valor = Decimal(item["valor"])

            categorias[categoria] = (
                categorias.get(categoria, Decimal("0.00"))
                + valor
            )

    print("\nDespesas por categoria:")

    if not categorias:
        print("Nenhuma despesa cadastrada.")
        return

    for categoria, valor in sorted(
        categorias.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        print(f"{categoria}: {formatar_moeda(valor)}")


def menu():
    """Executa o menu principal do sistema."""
    try:
        movimentacoes = carregar_dados()
    except RuntimeError as erro:
        print(erro)
        print("Verifique o arquivo dados.json antes de continuar.")
        return

    while True:
        print("\n" + "=" * 42)
        print("      CONTROLE FINANCEIRO PESSOAL")
        print("               VERSAO 1.4")
        print("=" * 42)
        print("1 - Cadastrar receita")
        print("2 - Cadastrar despesa")
        print("3 - Listar movimentacoes")
        print("4 - Consultar saldo")
        print("5 - Gerar relatorio financeiro")
        print("0 - Sair")
        print("=" * 42)

        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            cadastrar_movimentacao(movimentacoes, "receita")

        elif opcao == "2":
            cadastrar_movimentacao(movimentacoes, "despesa")

        elif opcao == "3":
            listar_movimentacoes(movimentacoes)

        elif opcao == "4":
            consultar_saldo(movimentacoes)

        elif opcao == "5":
            gerar_relatorio(movimentacoes)

        elif opcao == "0":
            print("Sistema encerrado. Ate mais!")
            break

        else:
            print("Opcao invalida. Tente novamente.")


if __name__ == "__main__":
    menu()