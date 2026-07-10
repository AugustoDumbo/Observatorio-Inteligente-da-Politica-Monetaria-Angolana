import sys
sys.path.insert(0, '.')
from scripts.utils.conexoes import ConexaoPostgres
import pandas as pd

pg = ConexaoPostgres()
conn = pg.conectar()

tabelas = ['taxas_cambio', 'taxas_juro', 'agregados_monetarios']
print('📊 REGISTROS NO BANCO:')
print('=' * 40)
for tabela in tabelas:
    query = f'SELECT COUNT(*) FROM raw.{tabela};'
    count = pd.read_sql(query, conn).iloc[0,0]
    print(f'  ✅ raw.{tabela}: {count} registros')

print('\n💵 Últimas taxas de câmbio:')
print(pd.read_sql('SELECT timestamp, moeda, valor_compra FROM raw.taxas_cambio ORDER BY timestamp DESC LIMIT 6;', conn))

print('\n🏦 Últimas taxas de juro:')
print(pd.read_sql('SELECT * FROM raw.taxas_juro ORDER BY timestamp DESC LIMIT 3;', conn))

print('\n💰 Últimos agregados monetários:')
print(pd.read_sql('SELECT timestamp, m2, m3, reservas_internacionais FROM raw.agregados_monetarios ORDER BY timestamp DESC LIMIT 3;', conn))

conn.close()
print('\n✅ Verificação concluída!')
