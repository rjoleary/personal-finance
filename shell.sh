#!/bin/sh
sqlite3 -cmd 'PRAGMA foreign_keys = ON;' -column -header finance.db
