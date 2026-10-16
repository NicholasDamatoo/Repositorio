import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from datetime import date

ARQUIVO_DADOS = Path(__file__).with_name("dados.json")


def carregar_dados():
    """Carrega as movimentações salvas."""
    if not ARQUIVO_DADOS.exists():
        return []

    try:
        with ARQUIVO_DADOS.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        if not isinstance(dados, list):
            raise ValueError("Formato de dados inválido.")

        return dados

    except (json.JSONDecodeError, ValueError) as erro:
        print(f"Erro ao ler os dados: {erro}")
        print("Os registros não foram carregados.")
        return None

    except OSError as erro:
        print(f"Erro ao acessar o arquivo: {erro}")
        return None


def salvar_dados(movimentacoes):
    """Salva as movimentações em um arquivo JSON."""
    try:
        with ARQUIVO_DADOS.open("w", encoding="utf-8") as arquivo:
            json.dump(
                movimentacoes,
                arquivo,
                ensure_ascii=False,
                indent=4
            )
        return True

    except OSError as erro:
        print(f"Erro ao salvar os dados: {erro}")
        return False


def ler_valor():
    """Lê um valor monetário positivo."""
    while True:
        entrada = input("Valor (ex.: 125,50): ").strip()
        entrada = entrada.replace(",", ".")

        try:
            valor = Decimal(entrada)

            if not valor.is_finite() or valor <= 0:
                print("Digite um valor positivo e válido.")
                continue

            return valor.quantize(Decimal("0.01"))

        except InvalidOperation:
            print("Valor inválido. Tente novamente.")


def cadastrar_movimentacao(movimentacoes, tipo):
    """Registra uma receita ou despesa."""
    descricao = input("Descrição: ").strip()

    if not descricao:
        print("A descrição não pode ficar vazia.")
        return

    categoria = input("Categoria: ").strip()

    if not categoria:
        print("A categoria não pode ficar vazia.")
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
        print(f"{tipo.capitalize()} registrada com sucesso!")
    else:
        movimentacoes.pop()
        print("Não foi possível registrar a movimentação.")


def formatar_moeda(valor):
    """Formata um valor como moeda brasileira."""
    valor_formatado = f"{valor:,.2f}"
    valor_formatado = (
        valor_formatado
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
    return f"R$ {valor_formatado}"


def listar_movimentacoes(movimentacoes):
    """Exibe todas as receitas e despesas."""
    if not movimentacoes:
        print("\nNenhuma movimentação cadastrada.")
        return

    print("\n--- MOVIMENTAÇÕES ---")

    for indice, item in enumerate(movimentacoes, start=1):
        valor = Decimal(item["valor"])

        print(f"\n{indice}. {item['descricao']}")
        print(f"   Tipo: {item['tipo'].capitalize()}")
        print(f"   Categoria: {item['categoria']}")
        print(f"   Valor: {formatar_moeda(valor)}")
        print(f"   Data: {item['data']}")


def calcular_totais(movimentacoes):
    """Calcula o total de receitas e despesas."""
    receitas = sum(
        (Decimal(item["valor"]) for item in movimentacoes
         if item["tipo"] == "receita"),
        Decimal("0.00")
    )

    despesas = sum(
        (Decimal(item["valor"]) for item in movimentacoes
         if item["tipo"] == "despesa"),
        Decimal("0.00")
    )

    return receitas, despesas


def consultar_saldo(movimentacoes):
    """Exibe o saldo financeiro atual."""
    receitas, despesas = calcular_totais(movimentacoes)
    saldo = receitas - despesas

    print("\n--- SALDO FINANCEIRO ---")
    print(f"Receitas: {formatar_moeda(receitas)}")
    print(f"Despesas: {formatar_moeda(despesas)}")
    print(f"Saldo:    {formatar_moeda(saldo)}")


def gerar_relatorio(movimentacoes):
    """Exibe um resumo financeiro por categoria."""
    receitas, despesas = calcular_totais(movimentacoes)

    print("\n--- RELATÓRIO FINANCEIRO ---")
    print(f"Total de receitas: {formatar_moeda(receitas)}")
    print(f"Total de despesas: {formatar_moeda(despesas)}")
    print(f"Saldo final: {formatar_moeda(receitas - despesas)}")

    gastos_categoria = {}

    for item in movimentacoes:
        if item["tipo"] == "despesa":
            categoria = item["categoria"]
            valor = Decimal(item["valor"])

            gastos_categoria[categoria] = (
                gastos_categoria.get(categoria, Decimal("0.00"))
                + valor
            )

    print("\nDespesas por categoria:")

    if not gastos_categoria:
        print("Nenhuma despesa registrada.")
    else:
        for categoria, valor in sorted(
            gastos_categoria.items(),
            key=lambda item: item[1],
            reverse=True
        ):
            print(f"- {categoria}: {formatar_moeda(valor)}")


def menu():
    movimentacoes = carregar_dados()

    if movimentacoes is None:
        print("Corrija ou restaure o arquivo dados.json antes de continuar.")
        return

    while True:
        print("\n" + "=" * 38)
        print("   CONTROLE FINANCEIRO PESSOAL")
        print("=" * 38)
        print("1 - Cadastrar receita")
        print("2 - Cadastrar despesa")
        print("3 - Listar movimentações")
        print("4 - Consultar saldo")
        print("5 - Gerar relatório")
        print("0 - Sair")
        print("=" * 38)

        opcao = input("Escolha uma opção: ").strip()

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
            print("Sistema encerrado. Até mais!")
            break

        else:
            print("Opção inválida. Escolha uma opção do menu.")


if __name__ == "__main__":
    menu()
