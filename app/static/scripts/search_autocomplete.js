const searchResults = document.querySelector(".search-results");
const inputBox = document.getElementById("input-box");

inputBox.onkeyup = function(){
    let input = inputBox.value;
    let result = searched.filter((keyword)=>{
        return keyword.toLowerCase().includes(input.toLowerCase());
    });
    console.log(result)
}
