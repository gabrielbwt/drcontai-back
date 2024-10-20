import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

def get_recurring(transactions, distance=2.0, min_samples=3):

    transactions_df = pd.DataFrame(transactions)

    if transactions_df.empty:
        return {
            'num_groups_received': 0,
            'recurring_transactions_received': pd.DataFrame(),
            'num_groups_debited': 0,
            'recurring_transactions_debited': pd.DataFrame()
        }

    transactions_df['date'] = pd.to_datetime(transactions_df['date'])
    transactions_df['days_diff'] = (transactions_df['date'] - transactions_df['date'].min()).dt.days
    amounts = transactions_df[['amount']].values

    vectorizer = TfidfVectorizer()
    description_tfidf = vectorizer.fit_transform(transactions_df['description']).toarray()

    features = pd.concat([pd.DataFrame(description_tfidf), pd.DataFrame(amounts), transactions_df[['days_diff']]], axis=1)
    features.columns = features.columns.astype(str)

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    dbscan = DBSCAN(eps=distance, min_samples=min_samples)
    labels = dbscan.fit_predict(features_scaled)

    transactions_df['recurring_group'] = labels
    recurring_transactions = transactions_df[transactions_df['recurring_group'] != -1]

    recurring_received = recurring_transactions[recurring_transactions['amount'] > 0]
    recurring_debited = recurring_transactions[recurring_transactions['amount'] < 0]

    if not recurring_received.empty:
        grouped_recurring_received = recurring_received.groupby('recurring_group', group_keys=False).apply(
            lambda x: {
                'ids': x['id'].tolist(),
                'description': x['description'].mode()[0],
                'total_amount': x['amount'].sum()
            }
        ).reset_index(drop=True)
    else:
        grouped_recurring_received = pd.DataFrame()

    if not recurring_debited.empty:
        grouped_recurring_debited = recurring_debited.groupby('recurring_group', group_keys=False).apply(
            lambda x: {
                'ids': x['id'].tolist(),
                'description': x['description'].mode()[0],
                'total_amount': abs(x['amount'].sum())
            }
        ).reset_index(drop=True)
    else:
        grouped_recurring_debited = pd.DataFrame()

    return {
        'num_groups_received': recurring_received['recurring_group'].nunique(),
        'recurring_transactions_received': grouped_recurring_received,
        'num_groups_debited': recurring_debited['recurring_group'].nunique(),
        'recurring_transactions_debited': grouped_recurring_debited
    }
