let board = null
let game = new Chess()
let whiteGray = '#a9a9a9'
let blackGrey = '#696969'

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
          hightlightMove(move)
        }
    })
}


function hightlightMove(move) {
  // highlights from a to square of the move
  let squares = move.split(' ')
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

$(window).click(function() {
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
    if (square[0] <'a' | square[0] > 'h') {
      is_valid = false
    }
    if (square[1] < 0 | square[1] > 8) {
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

$('.btn-start').click(function() {
  // sets starting position
  board.start()
  displayFen(buildFen());
})

$('.btn-empty').click(function() {
  // sets empty position
  board.clear()
  displayFen(buildFen())
})

$('.btn-move').click(function() {
  // generates a best move
  let is_valid = false
  let chars = ['p', 'n', 'b', 'r', 'q', 'k']
  let fen = $('.fen-string').text()
  let first_part = fen.split(' ')[0]
  for (let i = 0; i < first_part.length; i++) {
    console.log(first_part[i][0])
    if (first_part[i] in chars | first_part[i].toLowerCase() in chars) {
      is_valid = true
    }
  }
  if (is_valid) {
    generateMove(fen)
  } else {
    alert('empty board')
  }
})

$('.btn-side').click(function() {
  // checks which side to move (only one)
  $('.btn-side').removeClass('active-side')
  $(this).addClass('active-side');
})

$('.btn-castle').click(function() {
  // changes castle availability
  if ($(this).hasClass('active-side')) {
    $(this).removeClass('active-side')
  } else {
    $(this).addClass('active-side')
  }
})

$('.fen-btn').click(function() {
  // optins changes -> we might need a new fen
  buildFen()
})

$('.ep-input').keyup(function() {
  // sets en passant target if the square is valid
  buildFen()
})


function onSnapEnd() {
  displayFen(buildFen())
}

let config = {
  draggable: true,
  dropOffBoard: 'trash',
  sparePieces: true,
  onSnapEnd: onSnapEnd
}

board = Chessboard('board', config)
displayFen(buildFen())