package votings

import (
	"log"
	"net/http"
	"io/ioutil"
	"encoding/json"
	"time"
)

type voting struct {
	Id string `json:"votering_id"`
	Yes string `json:"Ja"`
	No string `json:"Nej"`
	NotAvailable string `json:"Frånvarande"`
	Abstain string `json:"Avstår"`
}

type votingsList struct {
	Number string `json:"@antal"`
	Votering []voting `json:"votering"`
}

type votingsResponse struct {
	VotingsList votingsList `json:"voteringlista"`
}

// Get Votings
func Request(year string) []voting {
	url := "http://data.riksdagen.se/voteringlista/?"
	url += "rm=" + year + "%2F18&"
	url += "bet=&punkt=&valkrets=&rost=&iid=&"
	url += "sz=2000&"
	url += "utformat=json&"
	url += "gruppering=votering_id"

	log.Print("Requesting voting from : ", url)

	// Adds a 2 seconds timeout the request futher down
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
	res, getErr := voteClient.Do(req)
	if getErr != nil {
		log.Fatal(getErr)
	}

	log.Print("HTTP: ", res.Status)

	// Get response body
	body, readErr := ioutil.ReadAll(res.Body)
	if readErr != nil {
		log.Fatal(readErr)
	}

	votingsResponse1 := votingsResponse{}
	jsonErr := json.Unmarshal(body, &votingsResponse1)
	if jsonErr != nil {
		log.Fatal(jsonErr)
	}

	log.Print("Hits: ", votingsResponse1.VotingsList.Number)

	return votingsResponse1.VotingsList.Votering
}
