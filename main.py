from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)
import os
import asyncio

# --- Configuración ---
TOKEN = '8064823801:AAH9bfrV68EtsLY39sHVZbVkhoTrwkjAJM4'
GRUPO_AUTORIZADO = 5098085  # Sustituye por el chat_id de tu grupo
#USUARIOS_AUTORIZADOS = [123456789]  # Sustituye con los IDs permitidos
CARPETA_STICKERS = 'stickers'
TIEMPO_AUTODESTRUCCION = 15  # segundos

# --- Comando /sticker: mostrar galería ---
async def mostrar_stickers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GRUPO_AUTORIZADO:
        await update.message.reply_text("Este bot solo funciona en el grupo autorizado.")
        return

    #if update.effective_user.id not in USUARIOS_AUTORIZADOS:
    #    await update.message.reply_text("No tienes permiso.")
    #    return

    archivos = [f for f in os.listdir(CARPETA_STICKERS) if f.endswith('.jpg')]
    for archivo in archivos:
        nombre = archivo.replace('.jpg', '')
        ruta = os.path.join(CARPETA_STICKERS, archivo)
        botones = [[InlineKeyboardButton("Enviar este", callback_data=nombre)]]
        markup = InlineKeyboardMarkup(botones)

        with open(ruta, 'rb') as f:
            await update.message.reply_photo(photo=f, caption=nombre, reply_markup=markup)

# --- Al pulsar un botón ---
async def enviar_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.message.chat.id != GRUPO_AUTORIZADO:
        await query.edit_message_text("Este bot solo funciona en el grupo autorizado.")
        return

    #if query.from_user.id not in USUARIOS_AUTORIZADOS:
    #    await query.edit_message_text("No tienes permiso.")
    #    return

    nombre = query.data
    ruta_webp = os.path.join(CARPETA_STICKERS, nombre + '.webp')

    if os.path.exists(ruta_webp):
        with open(ruta_webp, 'rb') as f:
            msg = await context.bot.send_document(
                chat_id=query.message.chat.id,
                document=f,
                filename=nombre + '.webp',
                protect_content=True
            )

        # Esperar y borrar el mensaje automáticamente
        await asyncio.sleep(TIEMPO_AUTODESTRUCCION)
        try:
            await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)
        except:
            pass
    else:
        await query.edit_message_text("Sticker no encontrado.")

# --- Lanzar el bot ---
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("sticker", mostrar_stickers))
app.add_handler(CallbackQueryHandler(enviar_sticker))

print("Bot en funcionamiento con autodestrucción...")
app.run_polling()
