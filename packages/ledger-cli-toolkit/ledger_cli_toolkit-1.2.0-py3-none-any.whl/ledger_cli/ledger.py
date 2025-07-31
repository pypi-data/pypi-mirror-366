import re
import json
from typing import List, Dict, Union
from datetime import datetime


class LedgerParser:
    def __init__(
        self, file_path: str, file_accounts_path: str = None, parents_accounts=None
    ):
        self.file_path = file_path
        self.file_accounts_path = file_accounts_path
        self.parents_accounts = (
            {
                "Assets": "Assets",
                "Liabilities": "Liabilities",
                "Equity": "Equity",
                "Income": "Income",
                "Expenses": "Expenses",
            }
            if parents_accounts is None
            else parents_accounts
        )

    def __str__(self):
        return f"LedgerParser(file_path='{self.file_path}')"

    def parse(self) -> List[Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]]:
        """
        Parses the ledger file to extract a list of transactions.
        """
        transactions = []
        last_amount = None
        last_unit = None

        with open(self.file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        current_transaction = None

        for line in lines:
            line = line.strip()

            if not line:
                # Save the current transaction and reset
                if current_transaction:
                    transactions.append(current_transaction)
                    current_transaction = None
                continue

            if not line or line.startswith(";"):
                # Línea vacía o comentario tipo ledger o markdown
                continue

            date_match = re.match(
                r"^(\d{4}[-/]\d{2}[-/]\d{2})(?: (\d{2}:\d{2}:\d{2}))?( \*?)?(.*)$", line
            )
            if date_match:
                # Parse transaction header
                date, time, verified, description = date_match.groups()
                current_transaction = {
                    "date": date,
                    "time": time if time else None,
                    "verified": bool(verified and verified.strip() == "*"),
                    "description": description.strip(),
                    "accounts": [],
                }

            elif current_transaction:
                # Parse account line
                # account_match = re.match(
                #     r"^([A-Za-z0-9:]+)\s+([A-Z]{3})\s+(-?\d{1,3}(?:,\d{3})*(?:\.\d+)?)$",
                #     line,
                # )

                unit = None
                amount = None

                # Primer patrón (moneda + cantidad o cantidad + moneda)
                account_match = re.match(
                    r"""^([A-Za-z0-9: ]+)\s+
                        (?:
                            ([A-Z]{3})\s+     # Grupo 2: moneda primero
                            (-?\d{1,3}(?:,\d{3})*(?:\.\d+)?)     # Grupo 3: cantidad
                            |
                            (-?\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s+  # Grupo 4: cantidad primero
                            ([A-Z]{3})       # Grupo 5: moneda
                        )$""",
                    line,
                    re.VERBOSE,
                )

                if not account_match:
                    account_match = re.match(
                        r"^([A-Za-z0-9: ]+)\s+([A-Z]{3})\s+(-?\d+(?:\.\d+)?)$", line
                    )

                if not account_match:
                    account_match = re.match(
                        r"^([A-Za-z0-9: ]+)\s+([A-Z]{3}|\$)?\s*(-?\$?\d{1,3}(?:,\d{3})*(?:\.\d+)?)$",
                        line,
                    )

                if not account_match:
                    account_match = re.match(
                        r"^([A-Za-z0-9: ]+)\s+([A-Z]{3}|\$)?\s*(-?\d{1,3}(?:,\d{3})*(?:\.\d+)?)$",
                        line,
                    )

                if not account_match:
                    account_match = re.match(r"^([A-Za-z0-9: ]+)$", line)

                group_count = account_match.lastindex or 0
                account_name = account_match.group(1).strip()

                if (
                    group_count >= 3
                    and account_match.group(2)
                    and account_match.group(3)
                ):  # moneda primero
                    unit = account_match.group(2)
                    amount = account_match.group(3)
                elif (
                    group_count >= 5
                    and account_match.group(4)
                    and account_match.group(5)
                ):  # cantidad primero
                    amount = account_match.group(4)
                    unit = account_match.group(5)

                else:
                    # Intenta con otros patrones más simples
                    simple_match = re.match(
                        r"^([A-Za-z0-9: ]+)\s+([A-Z]{3}|\$)?\s*(-?\$?\d{1,3}(?:,\d{3})*(?:\.\d+)?)$",
                        line,
                    )
                    if simple_match:
                        account_name = simple_match.group(1).strip()
                        unit = simple_match.group(2)
                        amount = simple_match.group(3)
                    else:
                        # Solo nombre de cuenta
                        simple_name = re.match(r"^([A-Za-z0-9: ]+)$", line)
                        if simple_name:
                            account_name = simple_name.group(1).strip()
                            amount = (
                                -abs(last_amount) if last_amount is not None else 0.0
                            )
                            unit = last_unit

                if account_name:
                    amount = (
                        float(str(amount).replace(",", "").replace("$", ""))
                        if amount is not None
                        else 0.0
                    )
                    unit = unit.replace(" ", "") if unit else "N/A"
                    account_name = account_name.replace(" ", "")
                    subAccounts = account_name.split(":")

                    last_amount = amount
                    last_unit = unit

                    current_transaction["accounts"].append(
                        {
                            "account": account_name,
                            "subAccounts": subAccounts,
                            "unit": unit,
                            "amount": amount,
                        }
                    )

                # if account_match:
                #     account_name = account_match.group(1).strip()
                #     unit = (
                #         account_match.group(2)
                #         if len(account_match.groups()) > 1
                #         else last_unit
                #     )
                #     # amount = (
                #     #     account_match.group(3)
                #     #     if len(account_match.groups()) > 2
                #     #     else f"-{last_amount}"
                #     # )

                #     if len(account_match.groups()) > 2:
                #         amount = account_match.group(3)
                #     else:
                #         amount = -abs(last_amount)

                #     # Clean data
                #     amount = (
                #         float(str(amount).replace(",", "").replace("$", ""))
                #         if amount
                #         else 0.0
                #     )

                #     unit = unit.replace(" ", "") if unit else "N/A"
                #     account_name = account_name.replace(" ", "")
                #     subAccounts = account_name.split(":")

                #     last_amount = amount
                #     last_unit = unit

                #     current_transaction["accounts"].append(
                #         {
                #             "account": account_name,
                #             "subAccounts": subAccounts,
                #             "unit": unit,
                #             "amount": amount,
                #         }
                #     )

        # Add the last transaction if any
        if current_transaction:
            transactions.append(current_transaction)

        return transactions

    def parse_accounts(self) -> List[str]:
        """
        Parses the file to extract a list of accounting accounts.
        """
        accounts = []

        with open(self.file_accounts_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()
            account_match = re.match(r"^account\s+([A-Za-z0-9:]+)$", line)
            if account_match:
                account_name = account_match.group(1)
                account_name = account_name.replace(" ", "")
                accounts.append(account_name)

        return accounts

    def parse_accounts_advance(self) -> List[Dict[str, str]]:
        """
        Parses the file to extract a list of accounting accounts with additional metadata.

        Example input:
        account Activos:Banco
          description "Cuenta bancaria principal para operaciones diarias"
          category "Activo Corriente"
          type "Activo"
          currency "MXN"
          created "2023-01-15"
          notes "Cuenta para depósitos y pagos automáticos"

        Returns a list of dicts like:
        [
            {
                "account": "Activos:Banco",
                "description": "Cuenta bancaria principal para operaciones diarias",
                "category": "Activo Corriente",
                "type": "Activo",
                "currency": "MXN",
                "created": "2023-01-15",
                "notes": "Cuenta para depósitos y pagos automáticos"
            },
            ...
        ]
        """
        accounts = []
        current_account = None
        current_data = {}

        with open(self.file_accounts_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                # Detecta inicio de nueva cuenta
                account_match = re.match(r"^account\s+([A-Za-z0-9:]+)$", line)
                if account_match:
                    # Si ya había una cuenta anterior, la guarda
                    if current_account is not None:
                        accounts.append(current_data)

                    # Nueva cuenta
                    current_account = account_match.group(1).replace(" ", "")
                    current_data = {"account": current_account}
                    continue

                # Si está dentro de una cuenta, parsea pares clave-valor
                if current_account is not None and line:
                    # Busca patrón clave "valor entre comillas"
                    key_value_match = re.match(r'^([a-zA-Z0-9_]+)\s+"(.+)"$', line)
                    if key_value_match:
                        key = key_value_match.group(1).lower()
                        value = key_value_match.group(2)
                        current_data[key] = value
                    else:
                        # También puede haber líneas sin comillas, opcional
                        key_value_match = re.match(r"^([a-zA-Z0-9_]+)\s+(.+)$", line)
                        if key_value_match:
                            key = key_value_match.group(1).lower()
                            value = key_value_match.group(2)
                            current_data[key] = value

        # Añade la última cuenta si existe
        if current_account is not None:
            accounts.append(current_data)

        return accounts

    def parse_metadata(self) -> Dict[str, Union[str, List[str], Dict[str, str]]]:
        metadata = {}
        current_key = None
        current_subkey = None
        buffer = []

        with open(self.file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line.startswith(";;; [") and line.endswith("]"):
                    # Guarda lo anterior si hay algo
                    if current_key and buffer:
                        content = "\n".join(buffer).strip()
                        if current_subkey:
                            if current_key not in metadata:
                                metadata[current_key] = {}
                            metadata[current_key][current_subkey] = content
                        else:
                            metadata[current_key] = content
                        buffer = []

                    # Inicia nuevo bloque
                    tag = line[5:-1]
                    if ":" in tag:
                        current_key, current_subkey = tag.split(":", 1)
                    else:
                        current_key = tag
                        current_subkey = None

                elif line.startswith(";;;"):
                    buffer.append(line[4:])  # Quitamos el prefijo ";;; "

            # Guardar el último bloque si existe
            if current_key and buffer:
                content = "\n".join(buffer).strip()
                if current_subkey:
                    if current_key not in metadata:
                        metadata[current_key] = {}
                    metadata[current_key][current_subkey] = content
                else:
                    metadata[current_key] = content

        return metadata

    def details_account(self, account: str):
        sub_accounts = account.split(":")
        return {"parent": sub_accounts[0], "sub_accounts": sub_accounts[1:]}

    def parse_accounts_with_details(self):
        accounts = self.parse_accounts()
        return [
            {"account": account, "details": self.details_account(account)}
            for account in accounts
        ]

    def transactions_to_json(self) -> str:
        transactions = self.parse()
        return json.dumps(transactions, indent=4, ensure_ascii=False)

    def to_json(
        self, data: List[Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]]
    ) -> str:
        return json.dumps(data, indent=4, ensure_ascii=False)

    def accounts_to_json(self) -> str:
        transactions = self.parse_accounts_with_details()
        return json.dumps(transactions, indent=4, ensure_ascii=False)

    def get_registers_between_dates(self, start_date: str, end_date: str) -> str:
        transactions = self.parse()
        start = datetime.strptime(start_date, "%Y/%m/%d")
        end = datetime.strptime(end_date, "%Y/%m/%d")

        filtered_transactions = [
            transaction
            for transaction in transactions
            if start <= datetime.strptime(transaction["date"], "%Y/%m/%d") <= end
        ]

        return json.dumps(filtered_transactions, indent=4, ensure_ascii=False)

    def get_registers_by_month(self, year: int, month: int) -> str:
        transactions = self.parse()
        filtered_transactions = [
            transaction
            for transaction in transactions
            if datetime.strptime(transaction["date"], "%Y/%m/%d").year == year
            and datetime.strptime(transaction["date"], "%Y/%m/%d").month == month
        ]

        return json.dumps(filtered_transactions, indent=4, ensure_ascii=False)

    def calculate_balances(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
        reference: List[str] = None,
    ) -> Dict[str, Dict[str, float]]:
        balances = {}

        for transaction in transactions_json:
            for account in transaction["accounts"]:
                account_name = account["account"]
                unit = account["unit"]
                amount = account["amount"]

                if account_name not in balances:
                    balances[account_name] = {}

                if unit not in balances[account_name]:
                    balances[account_name][unit] = 0.0

                balances[account_name][unit] += amount

        # Si se proporciona la lista de referencia, ordenamos los balances
        if reference:
            # Ordenamos las cuentas basándonos en la lista de referencia
            sorted_balances = {}
            for ref_account in reference:
                if ref_account in balances:
                    sorted_balances[ref_account] = balances.pop(ref_account)

            # Agregamos las cuentas que no están en la lista de referencia al final
            for account_name, balance in balances.items():
                sorted_balances[account_name] = balance

            return sorted_balances

        return balances

    def calculate_balance_for_account(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
        target_account: str,
    ) -> Dict[str, float]:
        account_balance = {}

        for transaction in transactions_json:
            for account in transaction["accounts"]:
                account_name = account["account"]
                unit = account["unit"]
                amount = account["amount"]

                if account_name.startswith(target_account):
                    if unit not in account_balance:
                        account_balance[unit] = 0.0

                    account_balance[unit] += amount

        return account_balance

    def calculate_balances_by_parents_accounts(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        assets = {}
        liabilities = {}
        equity = {}
        income = {}
        expenses = {}

        for transaction in transactions_json:
            for account in transaction["accounts"]:
                account_name = account["account"]
                unit = account["unit"]
                amount = account["amount"]

                if account_name.startswith(self.parents_accounts["Assets"]):
                    if unit not in assets:
                        assets[unit] = 0.0
                    assets[unit] += amount
                elif account_name.startswith(self.parents_accounts["Liabilities"]):
                    if unit not in liabilities:
                        liabilities[unit] = 0.0
                    liabilities[unit] += amount
                elif account_name.startswith(self.parents_accounts["Equity"]):
                    if unit not in equity:
                        equity[unit] = 0.0
                    equity[unit] += amount
                elif account_name.startswith(self.parents_accounts["Income"]):
                    if unit not in income:
                        income[unit] = 0.0
                    income[unit] += amount
                elif account_name.startswith(self.parents_accounts["Expenses"]):
                    if unit not in expenses:
                        expenses[unit] = 0.0
                    expenses[unit] += amount

        # Asignamos "N/A" solo si el objeto está vacío
        if not assets:
            assets["N/A"] = 0.0
        if not liabilities:
            liabilities["N/A"] = 0.0
        if not equity:
            equity["N/A"] = 0.0
        if not income:
            income["N/A"] = 0.0
        if not expenses:
            expenses["N/A"] = 0.0

        return {
            "Assets": assets,
            "Liabilities": liabilities,
            "Equity": equity,
            "Income": income,
            "Expenses": expenses,
        }

    def calculate_balances_by_details_accounts(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
    ) -> Dict[str, Dict[str, Union[Dict[str, float], List[str]]]]:
        # Diccionario para almacenar los saldos
        balances = {}

        for transaction in transactions_json:
            for account in transaction["accounts"]:
                account_name = account["account"]
                amount = account["amount"]
                unit = account["unit"]
                details = self.details_account(account_name)
                parent_account = details["parent"]

                # Inicializar el nivel raíz si no existe
                if parent_account not in balances:
                    balances[parent_account] = {
                        "balances": {},
                        "sub_accounts": {},
                    }

                # Mantén un puntero al nivel actual en la jerarquía
                current_level = balances[parent_account]

                # Recorre cada subcuenta para agregar niveles de profundidad
                for sub_account in details["sub_accounts"]:
                    # Si el subnivel no existe, inicialízalo
                    if sub_account not in current_level["sub_accounts"]:
                        current_level["sub_accounts"][sub_account] = {
                            "balances": {},
                            "sub_accounts": {},
                        }

                    # Mueve el puntero al siguiente nivel
                    current_level = current_level["sub_accounts"][sub_account]

                    # Inicializa el saldo de la unidad si no existe
                    if unit not in current_level["balances"]:
                        current_level["balances"][unit] = 0.0

                    # Agrega el monto a la unidad en este nivel
                    current_level["balances"][unit] += amount

                # También actualiza los saldos del nivel padre
                if unit not in balances[parent_account]["balances"]:
                    balances[parent_account]["balances"][unit] = 0.0

                balances[parent_account]["balances"][unit] += amount

        return balances

    def calculate_status_results(self, balances: Dict[str, Dict[str, float]]):
        # Diccionarios para almacenar los totales por cada moneda
        total_income_by_currency = {}
        total_expenses_by_currency = {}
        utility_by_currency = {}

        income_details = []
        expenses_details = []

        for account, currencies in balances.items():
            for currency, amount in currencies.items():
                if account.startswith(self.parents_accounts["Income"]):
                    amount = abs(amount)
                    # Sumar ingresos por cada moneda
                    if currency not in total_income_by_currency:
                        total_income_by_currency[currency] = 0
                    total_income_by_currency[currency] += amount
                    income_details.append(
                        {account: {"currency": currency, "amount": amount}}
                    )
                elif account.startswith(self.parents_accounts["Expenses"]):
                    amount = -amount
                    # Sumar gastos por cada moneda
                    if currency not in total_expenses_by_currency:
                        total_expenses_by_currency[currency] = 0
                    total_expenses_by_currency[currency] += amount
                    expenses_details.append(
                        {account: {"currency": currency, "amount": amount}}
                    )

        # Calcular utilidad por cada moneda
        for currency in total_income_by_currency:
            income = total_income_by_currency.get(currency, 0)
            expenses = total_expenses_by_currency.get(currency, 0)
            utility_by_currency[currency] = income + expenses

        return {
            "total_income_by_currency": total_income_by_currency,
            "total_expenses_by_currency": total_expenses_by_currency,
            "utility_by_currency": utility_by_currency,
            "income_details": income_details,
            "expenses_details": expenses_details,
        }

    def _create_transaction(
        self,
        date: str,
        description: str,
        accounts: List[Dict[str, Union[str, float]]],
        verify: bool = False,
    ) -> str:
        transaction = f"{date}{' * ' if verify else ' '}{description}\n"
        for account in accounts:
            account_line = (
                f"    {account['account']}    {account['unit']} {account['amount']:.2f}"
            )
            transaction += account_line + "\n"
        return transaction

    def add_transaction(
        self, date: str, description: str, accounts: List[Dict[str, Union[str, float]]]
    ):
        """
        Adds a new transaction to the ledger file.

        :param date: Date of the transaction in 'YYYY/MM/DD' format.
        :param description: Description of the transaction.
        :param accounts: List of account dictionaries with 'account', 'unit', and 'amount'.
        """
        with open(self.file_path, "a", encoding="utf-8") as file:
            file.write("\n")
            transaction_string = self._create_transaction(date, description, accounts)
            file.write(transaction_string)
            file.write("\n")

    # FUNCIONES AUXILIARES

    def get_date_range(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
    ):
        # Extraer todas las fechas únicas de las transacciones
        dates = {
            transaction["date"]
            for transaction in transactions_json
            if "date" in transaction
        }

        # Función para convertir las fechas a objetos datetime
        def parse_date(date_str: str):
            # Detectar el formato de fecha y convertirlo a datetime
            if "/" in date_str:
                return datetime.strptime(date_str, "%Y/%m/%d")
            elif "-" in date_str:
                return datetime.strptime(date_str, "%Y-%m-%d")
            else:
                raise ValueError(f"Fecha con formato no soportado: {date_str}")

        # Convertir las fechas a objetos datetime para calcular los límites
        date_objects = [parse_date(date) for date in dates]

        # Determinar la fecha mínima y máxima
        min_date = min(date_objects)
        max_date = max(date_objects)

        # Retornar las fechas en formato string
        return min_date.strftime("%Y/%m/%d"), max_date.strftime("%Y/%m/%d")


# Ejemplo de uso
if __name__ == "__main__":
    parser = LedgerParser("test.ledger")
    transactions_json = parser.parse()
    print(parser.get_registers_between_dates("2025/01/02", "2025/01/04"))
    print(parser.get_registers_by_month(2025, 1))
    balances = parser.calculate_balances(transactions_json)
    print(json.dumps(balances, indent=4, ensure_ascii=False))
    specific_balance = parser.calculate_balance_for_account(transactions_json, "Assets")
    print(json.dumps(specific_balance, indent=4, ensure_ascii=False))
