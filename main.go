package main

import (
	"database/sql"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"time"

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

	// Open database.
	db, err := sql.Open("sqlite3", "file:finance.db?_foreign_keys=1")
	if err != nil {
		log.Fatal(err)
	}
	tx, err := db.Begin()
	if err != nil {
		log.Fatal(err)
	}

	cmd, ok := map[string]func(){
		"help": func() {
			fmt.Println("list_accounts")
			fmt.Println("list_trans ACCOUNT_NUMBER")
			fmt.Println("create_account NAME")
			fmt.Println("import FILE ACCOUNT_NUMBER")
		},

		"list_accounts": func() {
			rows, err := db.Query("SELECT acc_id, acc_name, acc_currency FROM account")
			if err != nil {
				log.Fatal(err)
			}
			defer rows.Close()
			for rows.Next() {
				var id int
				var name, currency string
				err = rows.Scan(&id, &name, &currency)
				if err != nil {
					log.Fatal(err)
				}
				fmt.Printf("%d %s (%s)\n", id, name, currency)
			}
			err = rows.Err()
			if err != nil {
				log.Fatal(err)
			}
		},

		"list_trans": func() {
			rows, err := db.Query("SELECT trn_date, trn_amount, trn_description FROM transact NATURAL JOIN account WHERE acc_id == ?", flag.Args()[1])
			if err != nil {
				log.Fatal(err)
			}
			defer rows.Close()
			for rows.Next() {
				var date *time.Time
				var amount *float64
				var description *string
				err = rows.Scan(&date, &amount, &description)
				if err != nil {
					log.Fatal(err)
				}
				fmt.Printf("(%v) ", date)
				if amount != nil {
					fmt.Printf("%.2f\t", *amount)
				}
				if description != nil {
					fmt.Printf("%s", *description)
				}
				fmt.Println()
			}
			err = rows.Err()
			if err != nil {
				log.Fatal(err)
			}
		},

		"create_account": func() {
			_, err := db.Exec("INSERT INTO account(acc_name, acc_currency) VALUES (?, ?)", flag.Args()[1], flag.Args()[2])
			if err != nil {
				log.Fatal(err)
			}
			tx.Commit()
			return

		},

		"import": func() {
			stmt, err := tx.Prepare(`
		INSERT INTO transact(trn_date, trn_amount, trn_description, acc_id) VALUES (?, ?, ?, ?)
		`)
			if err != nil {
				log.Fatal(err)
			}
			defer stmt.Close()

			filename := flag.Args()[1]
			data, err := ioutil.ReadFile(filename)
			if err != nil {
				log.Fatalf("unable to read %q: %v", filename, err)
			}

			// Identify the importer
			var imp importer
			for _, imp = range importers {
				if imp.identify(data) {
					break
				}
			}
			if imp == nil {
				log.Fatalf("could not identify format of %q", filename)
			}

			// Parse
			trans, err := imp.parse(data)
			if err != nil {
				log.Fatalf("failed to parse %q as %q: %v", filename, imp.name(), err)
			}

			// Insert to db
			//j, _ := json.MarshalIndent(trans, "", "  ")
			//log.Print(string(j))
			for _, t := range trans {
				if _, err = stmt.Exec(t.Date, t.Amount, t.Description, flag.Args()[2]); err != nil {
					log.Fatal(err)
				}
			}
			log.Printf("imported %q as %q", filename, imp.name())
			tx.Commit()
		},
	}[flag.Arg(0)]
	if !ok {
		log.Fatal("command not found")
	}
	cmd()
}
