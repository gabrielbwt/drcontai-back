from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from typing import List

class CategoryDTO(BaseModel):
    id: str
    description: str
    descriptionTranslated: str
    parentId: Optional[str] = Field(None)
    parentDescription: Optional[str] = Field(None)

    model_config = ConfigDict(from_attributes=True)

class ConnectDTO(BaseModel):
    token: str

    model_config = ConfigDict(from_attributes=True)

class TransactionsDTO(BaseModel):
    id: str
    description: str
    amount: float
    date: str
    category: str
    account: str

    model_config = ConfigDict(from_attributes=True)

class TransactionDTO(BaseModel):
    id: str
    description: str
    currencyCode: str 
    amount: float 
    date: str 
    balance: float 
    category: str
    categoryId: str
    accountId: str 
    status: str 
    type: str

class TransactionSummaryDTO(BaseModel):
    category: str
    received: float
    debited: float

class RecurringTransactionDTO(BaseModel):
    ids: List[str]
    description: str
    total_amount: float

class RecurringTransactionsDTO(BaseModel):
    num_groups_received: int
    recurring_transactions_received: List[RecurringTransactionDTO]
    num_groups_debited: int
    recurring_transactions_debited: List[RecurringTransactionDTO]

class MonthlyTransactionDTO(BaseModel):
    month: str
    received: float
    debited: float

class InformationsResponseDTO(BaseModel):
    transactions_summary: List[TransactionSummaryDTO]
    recurring_transactions: RecurringTransactionsDTO
    monthly_transactions: List[MonthlyTransactionDTO]

class CategoryInfoDTO(BaseModel):
    transaction_id: str
    category_id: str

    model_config = ConfigDict(from_attributes=True)