package main

import (
	"fmt"
	"html/template"
	"log"
	"net/http"
	"strings"
	"io/ioutil"
	"encoding/json"
	"time"
)

type voteringsLista struct {
	Antal string `json:"@antal"`
}

type voteringsSvar struct {
	Lista voteringsLista `json:"voteringlista"`
}

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

// Hämta Votering
func requestVotering(year string) string {
	url := "http://data.riksdagen.se/voteringlista/?"
	url += "rm=" + year + "%2F18&"
	url += "bet=&punkt=&valkrets=&rost=&iid=&"
	url += "sz=2000&"
	url += "utformat=json&"
	url += "gruppering=votering_id"

	fmt.Println("Requesting votering from :\n" + url)

	//textBytes, _ := ioutil.ReadFile("assets/fakevotering.txt")

	//
	voteClient := http.Client{
		Timeout: time.Second * 2, // Maximum of 2 secs
	}

	// Send request
	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		log.Fatal(err)
	}

	// Be nice and say who you are
	req.Header.Set("User-Agent", "Riktig-politik")

	// Send the request with the help of voteClient
	// Will wait for 2 seconds
	res, getErr := voteClient.Do(req)
	if getErr != nil {
		log.Fatal(getErr)
	}

	fmt.Printf("HTTP: %s\n", res.Status)

	// Get response body
	body, readErr := ioutil.ReadAll(res.Body)
	if readErr != nil {
		log.Fatal(readErr)
	}

	voteringsSvar1 := voteringsSvar{}
	jsonErr := json.Unmarshal(body, &voteringsSvar1)
	if jsonErr != nil {
		log.Fatal(jsonErr)
	}

	fmt.Printf("Antal: " + voteringsSvar1.Lista.Antal)

	return "\nKLAR!"
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
