from abc import ABC, abstractmethod
from datetime import datetime, date
import textwrap

class Cliente:
    def __init__(self, endereco: str):
        self.endereco: str = endereco
        self.contas: list[Conta] = []

    def realizar_transacao(self, conta: "Conta", transacao: "Transacao") -> None:
        transacao.registrar(conta)

    def adicionar_conta(self, conta: "Conta") -> None:
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, cpf: str, nome: str, 
                 data_nascimento: date, endereco: str):
        super().__init__(endereco)
        self.cpf: str = cpf
        self.nome: str = nome
        self.data_nascimento: date = data_nascimento

class Conta:
    def __init__(self, numero: int, cliente: "Cliente"):
        self._saldo: float = 0.0
        self._numero: int = numero
        self._agencia: str = "001"
        self._cliente: "Cliente" = cliente
        self._historico: Historico = Historico()

    @classmethod
    def nova_conta(cls, cliente: "Cliente", numero: int,) -> "Conta":
        return cls(numero, cliente)
    
    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor: float) -> bool:
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if valor > 0 and valor <= self.saldo:
            print("\nSaque realizado com sucesso")
            self._saldo =- valor
            return True
        elif excedeu_saldo:
            print("\nOperação falhou!! Você não tem saldo suficiente")
        else:
            print("\n Operação falhou! O valor informado é inválido")
        return False

    def depositar(self, valor: float) -> bool:
        if valor > 0:
            self._saldo += valor
            print("\nDéposito realizado com sucesso")
            return True
        else:
            print("\n Operação falhou! O valor informado é inválido")
        return False


class ContaCorrente(Conta):
    def __init__(self, numero, cliente: "Cliente",
                 limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite= limite
        self._limite_saques= limite_saques

    @property
    def limite(self):
        return self._limite
    
    @property
    def limite_saques(self):
        return self._limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.
             transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print("Operação falhou! o valor do saque excede seu limite")
        elif excedeu_saques:
            print("Operação falhou! você exceeu seu número dde saques")
        else:
            return super().sacar(valor)
        return False
    
    def __str__(self):
        return f"""\
        Agência:\t{self.agencia}
        C/C:\t\t{self.numero}
        Titular:\t{self.cliente.nome}
    """

class Historico:
    def __init__(self):
        self._transacoes = []
    
    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao) -> None:
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime
                ("%d-%m-%Y %H:%M:%S"),
            }
        )

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

class Deposito(Transacao):
    def __init__(self, valor: float):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta: "Conta") -> None:
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Saque(Transacao):
    def __init__(self, valor: float):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta: "Conta") -> None:
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in
    clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n Cliente não possui conta")
        return
    return cliente.contas[0]

def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n Cliente não encontrado!")
        return
    
    valor = float(input("Informe o valor a ser depositado: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n Cliente não encontrado!")
        return
    
    valor = float(input("Informe o valor a ser sacado: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nCliente não encontrado")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    print("\n ============== EXTRATO =============")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações"
    else:
        for transacao in transacoes:
            extrato += f"\n {transacao['tipo']}:\n\tR${transacao['valor']:.2f}"

    print(extrato)
    print(f"\n Saldo:\n\tR$ {conta.saldo:.2f}")
    print("===========================")

def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Cliente não encontrado")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n === Conta criada com sucesso! ===")

def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))

def criar_cliente(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        nome = input("Informe o nome completo: ")
        data_nascimento = input("Informe a data de nascmiento (dd-mm-aaaa): ")
        endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

        cliente = PessoaFisica(cpf=cpf, nome=nome, data_nascimento=data_nascimento, endereco=endereco)

        clientes.append(cliente)

        print("\n=== Cliente criado com sucesso")
        
    else:
        print("\nEste CPF já está em uso")

def menu():
    menu = """\n
    ================= MENU ======================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova Conta
    [lc]\tListar Contas
    [nu]\tNovo Usuário
    [q]\tSair
    -> """

    return input(textwrap.dedent(str(menu)))

def main():
    clientes = []
    contas = []
    #agencia = "001"
    #cliente = PessoaFisica(cpf="04", nome="Gabriel Pamponet", data_nascimento="02-06-2004", endereco="Cabula")
    #clientes.append(cliente)
    

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) +1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print(" Operação Invalida!! Por favor selecione novamente a operação desejada")

    
main()