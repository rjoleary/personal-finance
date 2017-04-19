package main

import "time"

type account struct {
	Id       uint64
	Name     string
	Currency string
}

type category struct {
	Id   uint64
	Name string
}

type transaction struct {
	Id          uint64
	Created     time.Time
	Date        *time.Time
	Amount      *float64 // TODO
	Description *string
	Payee       *string
	Account     uint64
	Category    *uint64
}
