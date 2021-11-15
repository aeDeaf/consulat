package main

import (
	"consul-kommy/permutations"
	"encoding/json"
	"github.com/hashicorp/consul/api"
	"log"
	"math"
	"net/http"
	"os"
)

type Task struct {
	Matrix    [][]int
	Start_city int
}

type result struct {
	Min_dist int `json:"min_dist"`
	Min_route []int `json:"min_route"`
}

var task Task

func setTask(w http.ResponseWriter, r *http.Request) {
	err := json.NewDecoder(r.Body).Decode(&task)
	if err != nil {
		panic(err)
	}
	log.Println(task.Matrix)
}

func calcVariantDist(variant []int) int {
	route := make([]int, len(variant) + 3)
	route[0] = 0
	route[1] = task.Start_city
	for i := 0 ; i < len(variant); i++ {
		route[i + 2] = variant[i]
	}
	route[len(route) - 1] = 0
	dist := 0
	for i := 1; i < len(route); i++ {
		dist += task.Matrix[route[i - 1]][route[i]]
	}
	return dist
}

func solve(w http.ResponseWriter, r *http.Request) {
	matrixSize := len(task.Matrix)
	var start []int
	for i := 1; i < matrixSize; i++ {
		if i != task.Start_city {
			start = append(start, i)
		}
	}
	permutation := permutations.Create(start)
	minDist := math.MaxUint16
	minRoute := make([]int, len(start))
	for {
		currentDist := calcVariantDist(permutation.Permutation)
		if currentDist < minDist {
			minDist = currentDist
			copy(minRoute, permutation.Permutation)
		}
		if !permutations.HasNext(&permutation) {
			break
		} else {
			permutations.NextPermutation(&permutation)
		}
	}
	route := make([]int, len(minRoute) + 3)
	route[0] = 0
	route[1] = task.Start_city
	for i := 0 ; i < len(minRoute); i++ {
		route[i + 2] = minRoute[i]
	}
	route[len(route) - 1] = 0
	res := result{Min_dist: minDist, Min_route: route}
	w.Header().Add("Content-Type", "application/json")
	err := json.NewEncoder(w).Encode(res)
	if err != nil {
		panic(err)
	}
}

func main() {

	// Create an instance representing this service. "my-service" is the
	// name of _this_ service. The service should be cleaned up via Close.
	config := api.DefaultConfig()
	config.Address = os.Getenv("CONSUL_HOST") + ":8500"
	svc, _ := api.NewClient(config)
	serviceDef := &api.AgentServiceRegistration{
		Name: os.Getenv("NAME"),
	}
	err := svc.Agent().ServiceRegister(serviceDef)
	if err != nil {
		panic(err)
	}

	http.HandleFunc("/task", setTask)
	http.HandleFunc("/", solve)
	err = http.ListenAndServe(":5000", nil)
	if err != nil {
		panic(err)
	}
}
