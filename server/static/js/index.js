let board = null
let game = new Chess()
let whiteGray = '#a9a9a9'
let blackGrey = '#696969'
console.log('ok');

function generateMove(input_fen){
  // sends FEN position to the flask server which generates moves
  // returns a move generates by the engine in the string form(from + to squares)
    $.ajax({
        url:'/handle_request',
        type: 'POST',
        dataType: 'json',
        data: input_fen,
        success: function(data) {
          let move = data.move
          console.log(move);
          if (move == 'Invalid fen') {
            alert('Invalid fen')
          } else {
            hightlightMove(move)  
          }
        }
    })
}


function hightlightMove(move) {
  // highlights from a to square of the move
  let squares = move.split(' ')
  console.log(squares);
  let from = $('#board .square-' + squares[0])
  let to = $('#board .square-' + squares[1])
  squares[0] = from
  squares[1] = to
  squares.forEach(square => {
    if (square.hasClass('white-1e1d7')) {
      square.addClass('white-highlight')
    } else {
      square.addClass('black-highlight')
    }
    console.log(square);
  });
}

$(window).on('click', function() {
  $('.white-highlight').removeClass('white-highlight')
  $('.black-highlight').removeClass('black-highlight')
})

function squareIsVaild(square) {
  let is_valid = true
  if (square.length != 2) {
    // too long
    is_valid = false
  } else {
    // if 2 chars, check if the format is correct file A-H and rank 1-8
    if (square[0] <= 'a' | square[0] >= 'h') {
      is_valid = false
    }
    if (square[1] <= 1 | square[1] >= 8) {
      is_valid = false
    }
  }
  return is_valid
}

function buildFen() {
  // builds fen when option changes
  let fen = board.fen() + ' '
  // side to move
  fen += $('.btn-side.active-side').text()[0].toLowerCase()
  let castle = ''
  // castling rights
  if ($('#wk').hasClass('active-side')){
    castle += 'K'
  }
  if ($('#wq').hasClass('active-side')){
    castle += 'Q'
  }
  if ($('#bk').hasClass('active-side')){
    castle += 'k'
  }
  if ($('#bq').hasClass('active-side')){
    castle += 'q'
  }
  if (castle.length == 0) {
    castle += '-'
  }
  fen += ' ' + castle;
  // en passant value
  ep = $('.ep-input').val()
  if (squareIsVaild(ep)) {
    fen += ' ' + ep
  } else {
    fen += ' -'
  }
  fen += ' ' + '0 1'

  displayFen(fen)
}

function displayFen(fen) {
  // shows up a fen on screen
  $('.fen-string').text(fen)
}

$('.btn-start').on('click', function() {
  board.start()
  buildFen()
})
  
$('.btn-empty').on('click', function() {
  board.clear()
  buildFen()
})

$('.btn-move').on('click', function() {
  // generates a best move
  buildFen()
  generateMove($('.fen-string').text())
})

$('.btn-side').on('click', function() {
  // checks which side to move (only one)
  $('.btn-side').removeClass('active-side')
  $(this).addClass('active-side');
})

$('.btn-castle').on('click', function() {
  // changes castle availability
  if ($(this).hasClass('active-side')) {
    $(this).removeClass('active-side')
  } else {
    $(this).addClass('active-side')
  }
})

$('.fen-btn').on('click', function() {
  // optins changes -> we might need a new fen
  buildFen()
})

$('.ep-input').on('keyup', function() {
  // sets en passant target if the square is valid
  buildFen()
})

let config = {
  draggable: true,
  dropOffBoard: 'trash',
  sparePieces: true,
}


board = Chessboard('board', config)
buildFen()