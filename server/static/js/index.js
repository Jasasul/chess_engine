let board = null
let game = new Chess()

function generateMove(input_fen){
  // sends FEN position to the flask server which generates moves
  // returns a move in standard notation
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
            movePiece(move)
          }
        }
    })
}

function movePiece(move) {
  game.move(move)
  board.position(game.fen())
  if ($('#w').hasClass('active-side')) {
    $('#w').removeClass('active-side')
    $('#b').addClass('active-side')
  } else {
      $('#b').removeClass('active-side')
      $('#w').addClass('active-side')
  }
  updateFen()
}

$('.btn-start').on('click', function() {
  // on click sets a starting position of chess
  if (board != null) {
    board.start()
    updateFen()
  }
})
$('.btn-clear').on('click', function() {
  // on click removes all pieces from the board
  if (board != null) {
    board.clear()
    updateFen()
  }
})
$('.btn-move').on('click', function() {
  // generates move
  fen = $('#fen').val()
  generateMove(fen)
})

$('.btn-side').on('click', function() {
  // switch between side to move
  $('.btn-side').removeClass('active-side')
  $(this).addClass('active-side')

  updateFen()
})

$('.btn-castle').on('click', function() {
  // toggle castle
  if ($(this).hasClass('active-side')) {
    $(this).removeClass('active-side')
  } else {
    $(this).addClass('active-side')
  }

  updateFen()
})

$('.ep-input').on('keyup', function() {
  // en passant square if entered
  updateFen()
})

function get_side() {
  // updates side to move
  side = ''
  if ($('#w').hasClass('active-side')) {
    side += 'w'
  }
  if ($('#b').hasClass('active-side')) {
    side += 'b'
  }
  return side || '-'
}

function get_castle() {
  // updates castling rights
  castles = ''
  if ($('#wk').hasClass('active-side')) {
    castles += 'K'
  }
  if ($('#wq').hasClass('active-side')) {
    castles += 'Q'
  }
  if ($('#bk').hasClass('active-side')) {
    castles += 'k'
  }
  if ($('#bq').hasClass('active-side')) {
    castles += 'q'
  }
  return castles || '-'
}

function get_ep() {
  // sets up a special en passant target square if a valid square available
  validFiles = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
  validRanks = ['1', '2', '3', '4', '5', '6', '7', '8']
  square = ''
  epInput = $('.ep-input').val()
  if (epInput.length == 2) {
    if (validFiles.includes(epInput[0]) && validRanks.includes(epInput[1])) {
      square = epInput
    }
  }

  return square || '-'
}

function updateFen() {
  // updates fen string when it's properties change
  fen = board.fen()
  fen += ' ' + get_side()
  fen += ' ' + get_castle()
  fen += ' ' + get_ep()
  fen += ' ' + '0' + ' ' + '1'
  fenParts = fen.split(' ')
  $('#fen').val(fen)
}

function onSnapEnd() {
  // when piece moves, fen must be updated
  updateFen()
}

var config = {
  draggable: true,
  position: 'start',
  sparePieces: true,
  onSnapEnd: onSnapEnd
}
board = Chessboard('board', config)
updateFen()