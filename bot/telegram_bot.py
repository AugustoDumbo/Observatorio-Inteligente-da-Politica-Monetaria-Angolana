#!/usr/bin/env python3
"""
🤖 Bot Telegram - Observatório Monetário Angolano
Envia alertas, previsões e responde a comandos
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import os
from datetime import datetime, timedelta
import asyncio
import json

# Telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

# Acessar dados
from scripts.utils.conexoes import ConexaoPostgres
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== CONFIGURAÇÃO =====
TOKEN = os.getenv('TELEGRAM_TOKEN', 'SEU_TOKEN_AQUI')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')  # Opcional: ID do grupo

class ObservatorioBot:
    def __init__(self):
        self.pg = ConexaoPostgres()
        
    def obter_resumo(self):
        """Obtém resumo económico atual"""
        conn = self.pg.conectar()
        
        try:
            # Último câmbio USD
            cambio = pd.read_sql("""
                SELECT valor_compra FROM raw.taxas_cambio
                WHERE moeda = 'USD'
                ORDER BY timestamp DESC LIMIT 1
            """, conn)
            usd = cambio.iloc[0,0] if not cambio.empty else 0
            
            # Última taxa BNA
            juros = pd.read_sql("""
                SELECT taxa_bna FROM raw.taxas_juro
                ORDER BY timestamp DESC LIMIT 1
            """, conn)
            taxa = juros.iloc[0,0] if not juros.empty else 0
            
            # Último IPC
            ipc_df = pd.read_sql("""
                SELECT ipc_geral FROM raw.ipc
                ORDER BY timestamp DESC LIMIT 1
            """, conn)
            ipc = ipc_df.iloc[0,0] if not ipc_df.empty else 0
            
            # Brent
            brent_df = pd.read_sql("""
                SELECT brent_crude FROM raw.precos_internacionais
                ORDER BY timestamp DESC LIMIT 1
            """, conn)
            brent = brent_df.iloc[0,0] if not brent_df.empty else 0
            
            # Reservas
            reservas_df = pd.read_sql("""
                SELECT reservas_internacionais FROM raw.agregados_monetarios
                ORDER BY timestamp DESC LIMIT 1
            """, conn)
            reservas = reservas_df.iloc[0,0] if not reservas_df.empty else 0
            
            return {
                'usd_aoa': usd,
                'taxa_bna': taxa,
                'ipc': ipc,
                'brent': brent,
                'reservas': reservas
            }
        finally:
            conn.close()
    
    def obter_previsoes(self):
        """Obtém previsões de inflação"""
        try:
            import torch
            import joblib
            from scripts.ml.modelo_lstm_pytorch import LSTMModel, ModeloLSTMPyTorch
            
            modelo_path = Path('models/lstm_model.pth')
            scaler_path = Path('models/scaler_lstm.pkl')
            
            if modelo_path.exists() and scaler_path.exists():
                modelo = ModeloLSTMPyTorch()
                modelo.scaler = joblib.load(scaler_path)
                modelo.modelo = LSTMModel(7)
                modelo.modelo.load_state_dict(torch.load(modelo_path, map_location='cpu'))
                modelo.modelo.eval()
                
                return modelo.prever(3)
        except Exception as e:
            logger.error(f"Erro previsões: {e}")
        return None
    
    def obter_alertas(self):
        """Obtém últimos alertas"""
        alertas_path = Path('data/alertas.json')
        if alertas_path.exists():
            with open(alertas_path) as f:
                return json.load(f)
        return None

# ===== HANDLERS DE COMANDOS =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    keyboard = [
        [InlineKeyboardButton("📊 Resumo", callback_data='resumo'),
         InlineKeyboardButton("💵 Câmbio", callback_data='cambio')],
        [InlineKeyboardButton("📈 Inflação", callback_data='inflacao'),
         InlineKeyboardButton("🔮 Previsões", callback_data='previsao')],
        [InlineKeyboardButton("⚠️ Alertas", callback_data='alertas'),
         InlineKeyboardButton("❓ Ajuda", callback_data='ajuda')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    mensagem = (
        "🇦🇴 *Observatório Monetário Angolano*\n\n"
        "Bem-vindo ao sistema de monitoramento económico baseado em IA!\n\n"
        "Escolha uma opção ou use os comandos:\n"
        "/resumo - Resumo económico\n"
        "/cambio - Taxa de câmbio\n"
        "/inflacao - Dados de inflação\n"
        "/previsao - Previsões ML\n"
        "/alertas - Alertas do sistema"
    )
    
    await update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /resumo"""
    bot = ObservatorioBot()
    dados = bot.obter_resumo()
    
    mensagem = (
        "📊 *RESUMO ECONÓMICO*\n"
        f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        f"💵 *USD/AOA:* {dados['usd_aoa']:,.2f}\n"
        f"🏦 *Taxa BNA:* {dados['taxa_bna']:.1f}%\n"
        f"📈 *Inflação:* {dados['ipc']:.1f}%\n"
        f"🛢️ *Brent:* ${dados['brent']:.2f}\n"
        f"💰 *Reservas:* ${dados['reservas']:,.0f}M\n\n"
        "🔗 _Dados em tempo real_"
    )
    
    await update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)

async def cambio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /cambio"""
    bot = ObservatorioBot()
    conn = bot.pg.conectar()
    
    try:
        df = pd.read_sql("""
            SELECT timestamp, moeda, valor_compra 
            FROM raw.taxas_cambio
            ORDER BY timestamp DESC LIMIT 10
        """, conn)
        
        mensagem = "💵 *TAXAS DE CÂMBIO*\n\n"
        
        for moeda in ['USD', 'EUR']:
            dados_moeda = df[df['moeda'] == moeda]
            if not dados_moeda.empty:
                ultimo = dados_moeda.iloc[0]
                mensagem += f"*{moeda}/AOA:* {ultimo['valor_compra']:,.2f}\n"
        
        mensagem += "\n🔗 _Fonte: BNA_"
        await update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)
    finally:
        conn.close()

async def inflacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /inflacao"""
    bot = ObservatorioBot()
    conn = bot.pg.conectar()
    
    try:
        df = pd.read_sql("""
            SELECT timestamp, ipc_geral, ipc_alimentacao, ipc_transportes
            FROM raw.ipc
            ORDER BY timestamp DESC LIMIT 6
        """, conn)
        
        mensagem = "📈 *INFLAÇÃO (IPC)*\n\n"
        
        for _, row in df.iterrows():
            data = row['timestamp'].strftime('%b/%Y') if hasattr(row['timestamp'], 'strftime') else str(row['timestamp'])[:7]
            mensagem += (
                f"*{data}*\n"
                f"  Geral: {row['ipc_geral']:.1f}%\n"
                f"  Alimentação: {row['ipc_alimentacao']:.1f}%\n"
                f"  Transportes: {row['ipc_transportes']:.1f}%\n\n"
            )
        
        mensagem += "🔗 _Fonte: INE_"
        await update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)
    finally:
        conn.close()

async def previsao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /previsao"""
    bot = ObservatorioBot()
    previsoes = bot.obter_previsoes()
    
    if previsoes is not None and not previsoes.empty:
        mensagem = "🔮 *PREVISÕES DE INFLAÇÃO (LSTM)*\n\n"
        
        for _, row in previsoes.iterrows():
            emoji = "📈" if row['ipc_previsto'] > previsoes['ipc_previsto'].iloc[0] else "📉"
            mensagem += f"{emoji} *{row['mes']}:* {row['ipc_previsto']:.1f}%\n"
        
        mensagem += "\n🤖 _Modelo: LSTM Deep Learning_"
    else:
        mensagem = "❌ Previsões não disponíveis. Execute o treino do modelo primeiro."
    
    await update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)

async def alertas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /alertas"""
    bot = ObservatorioBot()
    dados = bot.obter_alertas()
    
    if dados and dados['total_alertas'] > 0:
        mensagem = f"⚠️ *ALERTAS ATIVOS: {dados['total_alertas']}*\n\n"
        
        for alerta in dados['alertas']:
            mensagem += f"{alerta['nivel']} *{alerta['tipo']}*\n"
            mensagem += f"  {alerta['mensagem']}\n\n"
    else:
        mensagem = "✅ *Nenhum alerta ativo*\nSistema operando normalmente."
    
    await update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para botões inline"""
    query = update.callback_query
    await query.answer()
    
    # Redirecionar para função correspondente
    command_map = {
        'resumo': resumo,
        'cambio': cambio,
        'inflacao': inflacao,
        'previsao': previsao,
        'alertas': alertas,
    }
    
    if query.data in command_map:
        # Criar um update falso com message
        await command_map[query.data](update, context)

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ajuda"""
    mensagem = (
        "❓ *COMANDOS DISPONÍVEIS*\n\n"
        "/start - Iniciar bot\n"
        "/resumo - Resumo económico\n"
        "/cambio - Taxas de câmbio\n"
        "/inflacao - Dados de inflação\n"
        "/previsao - Previsões ML\n"
        "/alertas - Alertas do sistema\n"
        "/ajuda - Esta mensagem\n\n"
        "🇦🇴 *Observatório Monetário Angolano*"
    )
    await update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)

# ===== ENVIO AUTOMÁTICO DE ALERTAS =====

async def enviar_alerta_programado(context: ContextTypes.DEFAULT_TYPE):
    """Envia alertas automaticamente a cada 6 horas"""
    bot = ObservatorioBot()
    
    # Verificar alertas
    dados = bot.obter_alertas()
    
    if dados and dados['total_alertas'] > 0:
        criticos = sum(1 for a in dados['alertas'] if 'ALTO' in a.get('nivel', ''))
        
        if criticos > 0:
            mensagem = f"⚠️ *ALERTA AUTOMÁTICO*\n{criticos} alertas críticos detectados!\n\nUse /alertas para detalhes."
            
            # Enviar para o chat configurado
            chat_id = context.job.chat_id if hasattr(context.job, 'chat_id') else None
            if chat_id:
                await context.bot.send_message(chat_id, mensagem, parse_mode=ParseMode.MARKDOWN)

# ===== CONFIGURAÇÃO PRINCIPAL =====

def main():
    """Inicializa o bot"""
    if TOKEN == 'SEU_TOKEN_AQUI':
        logger.error("❌ Configure o TELEGRAM_TOKEN no arquivo .env")
        return
    
    logger.info("🤖 Iniciando Bot Telegram...")
    
    # Criar aplicação
    app = Application.builder().token(TOKEN).build()
    
    # Registrar handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('resumo', resumo))
    app.add_handler(CommandHandler('cambio', cambio))
    app.add_handler(CommandHandler('inflacao', inflacao))
    app.add_handler(CommandHandler('previsao', previsao))
    app.add_handler(CommandHandler('alertas', alertas))
    app.add_handler(CommandHandler('ajuda', ajuda))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Envio automático a cada 6 horas
    if CHAT_ID:
        app.job_queue.run_repeating(
            enviar_alerta_programado,
            interval=21600,  # 6 horas
            first=10,
            chat_id=CHAT_ID
        )
        logger.info(f"✅ Alertas automáticos configurados para chat {CHAT_ID}")
    
    logger.info("✅ Bot iniciado! Pressione Ctrl+C para parar")
    
    # Iniciar polling
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
