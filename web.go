package main

import (
	"fmt"
	"html/template"
	"log"
	"net/http"
	"strings"
	"github.com/reicher/RiktigPolitik/votings"
)

func doStartupDebug(r *http.Request) {

	r.ParseForm() //Parse url parameters passed, then parse the response packet for the POST body (request body)

	// // attention: If you do not call ParseForm method, the following data can not be obtained form
	fmt.Println("r.form: ", r.Form) // print information on server side.

	fmt.Println("r.URL.path: ", r.URL.Path)
	fmt.Println("r.URL.scheme: ", r.URL.Scheme)
	fmt.Println("r.Form[url_long]: ", r.Form["url_long"])
	for k, v := range r.Form {
		fmt.Println("key:", k)
		fmt.Println("val:", strings.Join(v, ""))
	}
}


func about(w http.ResponseWriter, r *http.Request) {
}

func news(w http.ResponseWriter, r *http.Request) {
}

func startpage(w http.ResponseWriter, r *http.Request) {

	//doStartupDebug(r)

	t, err := template.ParseFiles("templates/startpage.gtpl")
	if err != nil {
		fmt.Println(err)
	} else {
		t.Execute(w, nil)
	}
}

func main() {
	fmt.Println("localhost:9090")

	// Note that the polical year start in fall.
	// 2017 is really fall 2017 - fall 2018x
	votings.Request("2017")

	// fmt.Printf(votingSession[3].Id)

	http.HandleFunc("/", startpage) // setting router rule
	http.HandleFunc("/news", news)
	http.HandleFunc("/about", about)
	err := http.ListenAndServe(":9090", nil) // setting listening port

	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}
