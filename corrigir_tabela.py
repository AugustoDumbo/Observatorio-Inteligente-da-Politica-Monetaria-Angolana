import sys
sys.path.insert(0, '.')
from scripts.utils.conexoes import ConexaoPostgres

pg = ConexaoPostgres()
conn = pg.conectar()
cur = conn.cursor()

# Corrigir o tamanho da coluna unidade
cur.execute('ALTER TABLE raw.agregados_monetarios ALTER COLUMN unidade TYPE VARCHAR(20);')
conn.commit()
print('✅ Coluna unidade alterada para VARCHAR(20)')

cur.close()
conn.close()
print('✅ Correção concluída!')
