import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)
n_registos = 10000


print("A gerar dados sintéticos com anomalias de governação...")


ids = [f"TRX-{i:06d}" if np.random.rand() > 0.02 else None for i in range(1, n_registos + 1)]


sistemas = np.random.choice(['CRM_VENDAS', 'PORTAL_WEB', 'ERP_FIN'], size=n_registos, p=[0.4, 0.4, 0.2])


categorias_base = ['Eletrônicos', 'Móveis', 'Vestuário', 'Informática', 'Acessórios']
categorias = [
    np.random.choice(categorias_base).lower() if np.random.rand() > 0.3 
    else np.random.choice(categorias_base).upper() 
    for _ in range(n_registos)
]


valores = np.round(np.random.exponential(scale=350, size=n_registos), 2)
valores[np.random.choice(n_registos, size=int(n_registos * 0.03), replace=False)] *= -1

data_base = datetime.now()
datas = [
    data_base - timedelta(days=int(d), minutes=int(m)) 
    for d, m in zip(np.random.uniform(0, 90, n_registos), np.random.uniform(0, 1440, n_registos))
]

df_raw = pd.DataFrame({
    'ID_TRANSACAO': ids,
    'DATA_REGISTRO': datas,
    'SISTEMA_ORIGEM': sistemas,
    'CATEGORIA_PRODUTO': categorias,
    'VALOR_BRUTO': valores
})


print("A aplicar regras de conformidade e a segregar quarentena...")

val_id = df_raw['ID_TRANSACAO'].notna()
val_valor = df_raw['VALOR_BRUTO'] > 0

mask_aprovados = val_id & val_valor
mask_rejeitados = ~mask_aprovados


df_trusted = df_raw[mask_aprovados].copy()
df_trusted['CATEGORIA_PRODUTO'] = df_trusted['CATEGORIA_PRODUTO'].str.strip().str.upper()
df_trusted['SISTEMA_ORIGEM'] = df_trusted['SISTEMA_ORIGEM'].str.strip().str.upper()


df_quarentena = df_raw[mask_rejeitados].copy()

def definir_motivo(row):
    motivos = []
    if pd.isna(row['ID_TRANSACAO']):
        motivos.append("ID_NULO")
    if row['VALOR_BRUTO'] <= 0:
        motivos.append("VALOR_NEGATIVO_OU_ZERO")
    return "; ".join(motivos)

df_quarentena['MOTIVO_REJEICAO'] = df_quarentena.apply(definir_motivo, axis=1)

df_log_anomalias = pd.DataFrame({
    'SISTEMA_ORIGEM': df_quarentena['SISTEMA_ORIGEM'].str.strip().str.upper(),
    'DATA_EVENTO': df_quarentena['DATA_REGISTRO'],
    'MOTIVO_REJEICAO': df_quarentena['MOTIVO_REJEICAO']
})

print(f"Total gerado: {n_registos}")
print(f"Registos válidos (Trusted): {len(df_trusted)}")
print(f"Registos rejeitados (Quarentena): {len(df_log_anomalias)}")


df_trusted.to_csv("fato_transacao_padronizada.csv", index=False, sep=",")
df_log_anomalias.to_csv("log_anomalias_dados.csv", index=False, sep=",")

print("\nArquivos CSV gerados com sucesso na pasta do projeto:")
print(" -> fato_transacao_padronizada.csv")
print(" -> log_anomalias_dados.csv")