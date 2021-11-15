package permutations

type Permutation struct {
	Array        []int
	Permutation  []int
	BaseIndex    int
	ReplaceIndex int
}

func Create(array []int) Permutation {
	permutation := Permutation{}
	permutation.Array = array
	permutation.Permutation = make([]int, len(array))
	copy(permutation.Permutation, permutation.Array)
	permutation.BaseIndex = len(array) - 1
	permutation.ReplaceIndex = len(array) - 1
	return permutation
}

func NextPermutation(permutation *Permutation) {
	var index int
	for i := len(permutation.Permutation) - 1; i > 0; i-- {
		if permutation.Permutation[i] > permutation.Permutation[i - 1] {
			index = i - 1
			break
		}
	}
	if index != -1 {
		l := -1
		for i := len(permutation.Permutation) - 1; i > index; i-- {
			if permutation.Permutation[i] > permutation.Permutation[index] {
				l = i
				break
			}
		}
		temp := permutation.Permutation[index]
		permutation.Permutation[index] = permutation.Permutation[l]
		permutation.Permutation[l] = temp
		tempArray := make([]int, len(permutation.Permutation)-index-1)
		for i := len(permutation.Permutation) - 1; i > index; i-- {
			tempArray[len(permutation.Permutation)-i-1] = permutation.Permutation[i]
		}
		for i := 0; i < len(tempArray); i++ {
			permutation.Permutation[index+i+1] = tempArray[i]
		}
	}

}

func HasNext(permutation *Permutation) bool {
	flag := false
	for i := len(permutation.Permutation) - 1; i > 0; i-- {
		if permutation.Permutation[i] > permutation.Permutation[i - 1] {
			flag = true
			break
		}
	}
	return flag
}
