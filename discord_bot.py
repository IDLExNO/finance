#!/usr/bin/env python3
"""Discord front-end for the finance engine. Listens for messages in one channel
(or your DMs, if DISCORD_CHANNEL_ID is unset) and treats them as transactions:
    200 - food
    Salary increased to 105000
    dashboard
    forecast
Every message updates data/state.json exactly like cli.py does -- run this
instead of typing commands yourself. See DISCORD_SETUP.md for how to create
the bot application/token and run this continuously on your machine.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import discord

from engine.io_utils import load_profile, load_assumptions, load_state, save_state
from engine.transactions import parse_transaction
from engine.apply import apply_transaction
from engine.model import simulate, yearly_snapshots, house_readiness
from engine.fmt import inr

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
if not TOKEN:
    sys.exit("Set DISCORD_BOT_TOKEN in your environment before running this bot. See DISCORD_SETUP.md.")
CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"]) if os.environ.get("DISCORD_CHANNEL_ID") else None

profile = load_profile()
assumptions = load_assumptions()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


def dashboard_text(state):
    snap = simulate(state, profile, assumptions, 1, salary_scenario="base")[0]
    r = house_readiness(simulate(state, profile, assumptions, 180, salary_scenario="base"),
                         profile, assumptions, "base", "base")
    b = snap["buckets"]
    return (
        f"Take-home: {inr(snap['take_home'])} | Expenses: {inr(snap['expenses_total'])} | Surplus: {inr(snap['surplus'])}\n"
        f"Emergency: {inr(b['emergency'])}/{inr(snap['emergency_target'])} | Bike: {inr(b['bike'])} | "
        f"House: {inr(b['house'])} | Long-term: {inr(b['long_term_wealth'])} | EPF: {inr(snap['epf_balance'])}\n"
        f"Net worth: {inr(snap['net_worth'])} | Debt: {inr(snap['debt_outstanding'])}\n"
        f"House-ready (base scenario): {r['date'] if r else 'beyond 15y horizon'}"
    )


def forecast_text(state):
    snaps = simulate(state, profile, assumptions, 123, salary_scenario="base")
    lines = [f"{s['date'][:7]}: net worth {inr(s['net_worth'])}, house fund {inr(s['buckets']['house'])}"
             for s in yearly_snapshots(snaps)]
    return "\n".join(lines)


def transaction_reply(impact, action, text):
    reply = (
        f"Updated ({action['type']}): {text}\n"
        f"Surplus: {inr(impact['surplus_before'])} -> {inr(impact['surplus_after'])}\n"
        f"Net worth (10y): {inr(impact['net_worth_10y_before'])} -> {inr(impact['net_worth_10y_after'])}\n"
        f"House-ready: {impact['house_date_before']} -> {impact['house_date_after']}"
    )
    if "opportunity_cost_5y" in impact:
        reply += f"\nOpportunity cost if invested instead: {inr(impact['opportunity_cost_5y'])} (5y), {inr(impact['opportunity_cost_10y'])} (10y)"
    if impact.get("note"):
        reply += f"\n{impact['note']}"
    return reply


@client.event
async def on_ready():
    print(f"Logged in as {client.user}. Listening on "
          f"{'channel ' + str(CHANNEL_ID) if CHANNEL_ID else 'DMs only'}.")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if CHANNEL_ID is not None:
        if message.channel.id != CHANNEL_ID:
            return
    elif message.guild is not None:
        return  # no channel configured -> only respond to DMs, never post in servers unscoped

    text = message.content.strip()
    if not text:
        return
    low = text.lower()

    state = load_state()
    if low in ("dashboard", "how am i doing", "how am i doing?"):
        await message.reply(dashboard_text(state))
        return
    if low == "forecast":
        await message.reply(forecast_text(state))
        return

    action = parse_transaction(text)
    if action["type"] == "unknown" or action.get("amount") is None:
        return  # not a recognized transaction -- stay quiet rather than spam the channel

    new_state, impact = apply_transaction(state, profile, assumptions, action)
    save_state(new_state)
    await message.reply(transaction_reply(impact, action, text))


client.run(TOKEN)
