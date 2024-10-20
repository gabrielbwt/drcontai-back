from app.services.base_service import BaseService
from app.utils.settings import Settings
from fastapi import HTTPException, status
from app.dal.pluggy import PluggyDal
from datetime import datetime
from app.dto.pluggy import CategoryInfoDTO
from app.utils.recurrence_analysis import get_recurring
import pandas as pd
import requests
import time
import httpx

class PluggyService(BaseService):
        
    def __init__(self, settings: Settings, pluggy_dal: PluggyDal):
        self.base_url = 'https://api.pluggy.ai'
        self.client_id = settings.pluggy_client_id
        self.client_secret = settings.pluggy_client_secret
        self.dal = pluggy_dal

    def get_api_key(self):
        current_time = time.time()

        pluggy_api_key = self.dal.get_pluggy_api_key()

        if pluggy_api_key is not None:
            api_key = pluggy_api_key.api_key
            api_key_expiration = pluggy_api_key.api_key_expiration

            if api_key is not None and datetime.fromtimestamp(current_time) < api_key_expiration:
                return api_key

        payload = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        try:
            response = requests.post(f"{self.base_url}/auth", json=payload, headers=headers)

            if response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao obter a chave de acesso da API Pluggy")

            response_json = response.json()

            api_key = response_json["apiKey"]
            api_key_expiration = datetime.fromtimestamp(current_time + 60 * 60 * 2)
            
            self.dal.update_pluggy_api_key(api_key, api_key_expiration)

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro inesperado ao obter a chave de acesso da API Pluggy: {str(e)}")

        return api_key

    async def get_connect_token(self):
        current_time = time.time()

        pluggy_config_connect_token = self.dal.get_pluggy_connect_token()

        if pluggy_config_connect_token is not None:
            connect_token = pluggy_config_connect_token.connect_token
            connect_token_expiration = pluggy_config_connect_token.connect_token_expiration

            if datetime.fromtimestamp(current_time) < connect_token_expiration:
                return {"token": connect_token}

        api_key = self.get_api_key()

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-API-KEY": api_key
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/connect_token", headers=headers)

            if response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao obter o token de conexão da API Pluggy")

            response_json = response.json()

            connect_token = response_json["accessToken"]
            connect_token_expiration = datetime.fromtimestamp(current_time + 60 * 60 * 0.5) # 30 minutos

            self.dal.update_pluggy_connect_token(connect_token, connect_token_expiration)

        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro inesperado ao obter o token de conexão da API Pluggy")

        return {"token": connect_token}
        
    def get_accounts(self, item_id: str):

        api_key = self.get_api_key()

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key,
        }

        try:

            response = requests.get(f"{self.base_url}/accounts?itemId={item_id}", headers=headers)

            if response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao obter as contas da API Pluggy")

            response_json = response.json()
            return response_json["results"]
        
        except Exception:

            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro inesperado ao obter as contas da API Pluggy")

    async def get_transactions(self, item_id: str, from_date: datetime = '2023-11-01', to_date: datetime = '2024-10-19'):

        accounts = self.get_accounts(item_id)

        api_key = self.get_api_key()

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key,
        }

        all_transactions = []

        try:
            async with httpx.AsyncClient() as client:
                for account in accounts:
                    account_id = account['id']
                    page = 1

                    while True:

                        response = await client.get(
                            f"{self.base_url}/transactions",
                            headers=headers,
                            params={
                                "accountId": account_id,
                                "page": page,
                                "pageSize": 500,
                                "from": from_date,
                                "to": to_date
                            }
                        )

                        if response.status_code != 200:
                            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao obter transações")

                        data = response.json()
                        transactions = data.get("results", [])

                        all_transactions.extend(transactions)

                        if page >= data.get("totalPages", 1):
                            break

                        page += 1

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro inesperado: {str(e)}")

        all_transactions_filtred = await self.get_filtred_transactions(all_transactions)

        return all_transactions_filtred
 
    async def get_categories(self):

        api_key = self.get_api_key()

        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key,
        }

        try:
            async with httpx.AsyncClient() as client:
                
                response = await client.get(f"{self.base_url}/categories", headers=headers)

            if response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao obter as categorias da API Pluggy")
    
            return response.json()["results"]
        
        except Exception:

            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro inesperado ao obter as categorias da API Pluggy")
        
    async def get_filtred_transactions(self, transactions: list):
        
        categories = await self.get_categories()
        
        if categories is None or len(categories) == 0:
            raise ValueError("Nenhuma categoria encontrada")

        category_map = {category['id']: category['descriptionTranslated'] for category in categories}

        informations = ["id", "description", "currencyCode", "amount", "date", "categoryId", "balance", "accountId", "type", "status"]

        filtered_transactions = []

        for transaction in transactions:

            if not all(key in transaction for key in informations):
                raise KeyError(f"Transação com chave faltando: {transaction}")

            filtered_transaction = {info: transaction[info] for info in informations}

            category_id = transaction.get('categoryId')
            filtered_transaction['category'] = category_map.get(category_id, "Descrição não encontrada")
            filtered_transaction['categoryId'] = category_id

            filtered_transactions.append(filtered_transaction)

        return filtered_transactions

    def filter_transactions_by_category(self, transactions: list):
        result = {}

        for transaction in transactions:
            category = transaction['category']

            if category not in result:
                result[category] = {
                    'received': [],
                    'debited': []
                }

            if transaction['amount'] > 0:
                result[category]['received'].append(transaction)
            elif transaction['amount'] < 0:
                result[category]['debited'].append(transaction)

        return result
    
    def summarize_transactions_by_category(self, transactions_by_category):
        summary = []

        for category, data in transactions_by_category.items():
            received_total = 0
            debited_total = 0
            
            if 'received' in data and isinstance(data['received'], list):
                received_total = sum(t['amount'] for t in data['received'] if 'amount' in t)
            
            if 'debited' in data and isinstance(data['debited'], list):
                debited_total = sum(t['amount'] for t in data['debited'] if 'amount' in t)

            summary.append({
                'category': category,
                'received': received_total,
                'debited': abs(debited_total)
            })

        return summary

    def monthly_revenue_expense(self, transactions, start_month, end_month):

        start_month = pd.to_datetime(start_month)
        end_month = pd.to_datetime(end_month)

        transactions_df = pd.DataFrame(transactions)

        if transactions_df.empty:
            return [{'month': month.strftime('%m/%Y'), 'received': 0, 'debited': 0} 
                    for month in pd.date_range(start=start_month, end=end_month, freq='MS')]

        transactions_df['date'] = pd.to_datetime(transactions_df['date']).dt.tz_localize(None)

        transactions_df = transactions_df[
            (transactions_df['date'] >= start_month) & 
            (transactions_df['date'] <= end_month)
        ]

        months = pd.date_range(start=start_month, end=end_month, freq='MS')

        results = []

        for month in months:
            month_str = month.strftime('%m/%Y')
            
            monthly_transactions = transactions_df[
                (transactions_df['date'] >= month) &
                (transactions_df['date'] < month + pd.DateOffset(months=1))
            ]

            if monthly_transactions.empty:
                received = 0
                debited = 0
            else:
                received = monthly_transactions[monthly_transactions['amount'] > 0]['amount'].sum()
                debited = monthly_transactions[monthly_transactions['amount'] < 0]['amount'].sum()

            results.append({
                'month': month_str,
                'received': received,
                'debited': abs(debited)
            })

        return results

    async def get_informations(self, item_id: str, from_date: datetime, to_date: datetime):

        transactions = await self.get_transactions(item_id, from_date, to_date)

        transactions_filtred_by_category = self.filter_transactions_by_category(transactions)

        transactions_summary = self.summarize_transactions_by_category(transactions_filtred_by_category)

        recurring_transactions = get_recurring(transactions)

        monthly_transactions = self.monthly_revenue_expense(transactions, from_date, to_date)
    
        return {
            'transactions_summary': transactions_summary,
            'recurring_transactions': recurring_transactions,
            'monthly_transactions': monthly_transactions
        }
    
    async def update_category(self, category_info: CategoryInfoDTO):

        api_key = self.get_api_key()

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-API-KEY": api_key
        }

        try:

            payload = { "categoryId": category_info.category_id }

            response = requests.patch(f"{self.base_url}/transactions/{category_info.transaction_id}", json=payload, headers=headers)

            if response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao atualizar a categoria da transação")

            return 
        
        except Exception:

            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro inesperado ao atualizar a categoria da transação")