from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

con = sqlite3.connect("Database.sqlite")
cur = con.cursor()
