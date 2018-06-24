package main

import (
	"fmt"
	"html/template"
	"log"
	"net/http"
	"strings"
	"io/ioutil"
	"encoding/json"
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

type voteringslista struct {
	Number int `json:"number"`
}

// Hämta Votering
func requestVotering(year string) string {
	// url := "http://data.riksdagen.se/voteringlista/?"
	// url += "rm=" + year + "%2F18&"
	// url += "bet=&punkt=&valkrets=&rost=&iid=&"
	// url += "sz=2000&"
	// url += "utformat=xml&"
	// url += "gruppering=votering_id"

	textBytes, _ := ioutil.ReadFile("assets/fakevotering.txt")
	fmt.Println(string(textBytes))
	voteringslista1 := voteringslista{}

	err := json.Unmarshal(textBytes, &voteringslista1)
	if err != nil {
		fmt.Println(err)
		return ""
	}

	return string(voteringslista1.Number)
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

	fmt.Println(requestVotering("2017"))

	http.HandleFunc("/", startpage) // setting router rule
	err := http.ListenAndServe(":9090", nil) // setting listening port

	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}
