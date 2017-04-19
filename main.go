package main

import (
	"database/sql"
	"flag"
	"fmt"
	"io/ioutil"
	"log"

	_ "github.com/mattn/go-sqlite3"
)

var importers = []importer{}

type importer interface {
	name() string
	identify(data []byte) bool
	parse(data []byte) ([]transaction, error)
}

func main() {
	flag.Parse()
	if flag.NArg() < 1 {
		log.Fatal("Usage: finance FILE...")
	}

	// Open database
	db, err := sql.Open("sqlite3", "file:finance.db?_foreign_keys=1")
	if err != nil {
		log.Fatal(err)
	}
	tx, err := db.Begin()
	if err != nil {
		log.Fatal(err)
	}

	if flag.Arg(0) == "list" {
		rows, err := db.Query("SELECT acc_name, acc_currency FROM account")
		if err != nil {
			log.Fatal(err)
		}
		defer rows.Close()
		for rows.Next() {
			var name, currency string
			err = rows.Scan(&name, &currency)
			if err != nil {
				log.Fatal(err)
			}
			fmt.Println(name, currency)
		}
		err = rows.Err()
		if err != nil {
			log.Fatal(err)
		}
		return
	}

	if flag.Arg(0) == "account" {
		_, err := db.Exec("INSERT INTO account(acc_name, acc_currency) VALUES (?, ?)", flag.Arg(1), flag.Arg(2))
		if err != nil {
			log.Fatal(err)
		}
		tx.Commit()
		return
	}

	stmt, err := tx.Prepare(`
INSERT INTO transact(trn_date, trn_amount, trn_description, acc_id) VALUES (?, ?, ?, 1)
`)
	if err != nil {
		log.Fatal(err)
	}
	defer stmt.Close()

	for _, filename := range flag.Args() {
		data, err := ioutil.ReadFile(filename)
		if err != nil {
			log.Printf("unable to read %q: %v", filename, err)
			continue
		}

		// Identify the importer
		var imp importer
		for _, imp = range importers {
			if imp.identify(data) {
				break
			}
		}
		if imp == nil {
			log.Printf("could not identify format of %q", filename)
			continue
		}

		// Parse
		trans, err := imp.parse(data)
		if err != nil {
			log.Printf("failed to parse %q as %q: %v", filename, imp.name(), err)
			continue
		}

		// Insert to db
		//j, _ := json.MarshalIndent(trans, "", "  ")
		//log.Print(string(j))
		for _, t := range trans {
			if _, err = stmt.Exec(t.Date, t.Amount, t.Description); err != nil {
				log.Fatal(err)
			}
		}
		log.Printf("imported %q as %q", filename, imp.name())
	}
	tx.Commit()
}
