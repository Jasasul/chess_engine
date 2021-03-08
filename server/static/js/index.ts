let board = null
let game = new Chess()

function generateMove(input_fen: string){
  // sends FEN position to the flask server which generates moves
  // returns a move generates by the engine in the string form(from + to squares)
    $.ajax({
        url:'/handle_request',
        type: 'POST',
        dataType: 'json',
        data: input_fen,
        success: function(data) {
          let move = data.move
          if (move == 'Draw' || move == 'Checkmate' || move == 'Invalid fen') {
            alert(move)
          } else {
            console.log(1);
          }
        }
    })
}