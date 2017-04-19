package main

import (
	"bytes"
	"encoding/csv"
	"errors"
	"reflect"
	"strconv"
	"time"
)

func init() {
	importers = append(importers, boa_importer{})
}

type boa_importer struct{}

func (i boa_importer) name() string {
	return "Bank of America CSV"
}

func (i boa_importer) identify(data []byte) bool {
	return bytes.HasPrefix(data, []byte("Description,,Summary Amt."))
}

func (i boa_importer) parse(data []byte) ([]transaction, error) {
	// Remove the header before the CSV.
	parts := bytes.Split(data, []byte("\r\n\r\n"))
	if len(parts) != 2 {
		return nil, errors.New("parsing failed")
	}
	csvData := parts[1]

	records, err := csv.NewReader(bytes.NewReader(csvData)).ReadAll()
	if err != nil {
		return nil, err
	}
	expectedHeader := []string{"Date", "Description", "Amount", "Running Bal."}
	if len(records) < 1 || !reflect.DeepEqual(records[0], expectedHeader) {
		return nil, errors.New("invalid header")
	}

	// Convert records to transactions.
	trans := []transaction{}
	for _, r := range records[1:] {
		var date *time.Time
		if r[0] != "" {
			v, err := time.Parse("01/02/2006", r[0])
			if err != nil {
				return nil, err
			}
			date = &v
		}

		var desc *string
		if r[1] != "" {
			desc = &r[1]
		}

		var amount *float64
		if r[2] != "" {
			v, err := strconv.ParseFloat(r[2], 64)
			if err != nil {
				return nil, err
			}
			amount = &v
		}

		trans = append(trans, transaction{
			Date:        date,
			Description: desc,
			Amount:      amount,
		})
	}

	return trans, nil
}
