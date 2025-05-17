from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)
import os
import asyncio

import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- Configuración ---
TOKEN = os.getenv("BOT_TOKEN")

GRUPO_AUTORIZADO = -4066203778  # Sustituye por el chat_id de tu grupo
#USUARIOS_AUTORIZADOS = [123456789]  # Sustituye con los IDs permitidos
CARPETA_STICKERS = 'stickers'
TIEMPO_AUTODESTRUCCION = 3600  # segundos
CIUDAD = "Madrid"

# --- Comando /sticker: mostrar galería ---
async def mostrar_stickers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GRUPO_AUTORIZADO:
        await update.message.reply_text("Este bot solo funciona en el grupo autorizado.")
        return

    #if update.effective_user.id not in USUARIOS_AUTORIZADOS:
    #    await update.message.reply_text("No tienes permiso.")
    #    return

    archivos = [f for f in os.listdir(CARPETA_STICKERS) if f.endswith('.webp')]
    for archivo in archivos:
        nombre = archivo.replace('.webp', '')
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

async def obtener_clima():
    url = f"https://wttr.in/{CIUDAD.replace(' ', '+')}?format=j1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return "No se pudo obtener el clima 😞"
            data = await resp.json()

            hoy = data["weather"][0]
            max_temp = hoy["maxtempC"]
            min_temp = hoy["mintempC"]
            descripcion = hoy["hourly"][7]["weatherDesc"][0]["value"]  # Aprox. 7:00
            temp = hoy["hourly"][7]["tempC"]
            sensacion = hoy["hourly"][7]["FeelsLikeC"]

            return (
                f"Tiempo en Campus Repsol a las 7:00:\n"
                f"{descripcion}, {temp}°C (sensación: {sensacion}°C)\n"
                f"Máxima: {max_temp}°C | Mínima: {min_temp}°C"
            )

async def enviar_clima_diario(context: ContextTypes.DEFAULT_TYPE):
    mensaje = await obtener_clima()
    await context.bot.send_message(chat_id=GRUPO_AUTORIZADO, text=mensaje)

# Comando /tiempo
async def comando_tiempo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = await obtener_clima()
    await update.message.reply_text(mensaje)



# --- Lanzar el bot ---
app = ApplicationBuilder().token(TOKEN).build()

# Scheduler para ejecutar la tarea diaria
scheduler = AsyncIOScheduler()
scheduler.add_job(enviar_clima_diario, trigger='cron', hour=11, minute=0, args=[app.bot])
scheduler.start()

app.add_handler(CommandHandler("sticker", mostrar_stickers))
app.add_handler(CallbackQueryHandler(enviar_sticker))
app.add_handler(CommandHandler("tiempo", comando_tiempo))
app.run_polling()


